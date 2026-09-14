"""Unit tests for imap_mag.db.DeleteOldRows."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from psycopg.errors import InsufficientPrivilege, UndefinedTable
from sqlalchemy.exc import ProgrammingError

from imap_mag.config.DeleteDatabaseRowsConfig import DeleteRowsTask
from imap_mag.db.DeleteOldRows import delete_old_rows
from imap_mag.util import DatetimeProvider


def _make_task(
    name="delete-ace-mag-noaa-rows",
    table="ace_mag_noaa",
    datetime_column="id",
    threshold_days=7,
):
    return DeleteRowsTask(
        name=name,
        table=table,
        datetime_column=datetime_column,
        threshold_days=threshold_days,
    )


def _make_mock_settings(tasks=None, dry_run=False, db_lookup_key="imap-database"):
    mock_settings = MagicMock()
    mock_settings.database_delete_rows.tasks = tasks or [_make_task()]
    mock_settings.database_delete_rows.dry_run = dry_run
    mock_settings.database_delete_rows.database_url_env_var_or_block_name = (
        db_lookup_key
    )
    return mock_settings


def _make_mock_database(scalar_return=0, rowcount=0):
    mock_connection = MagicMock()
    mock_connection.execute.return_value.scalar_one.return_value = scalar_return
    mock_connection.execute.return_value.rowcount = rowcount

    mock_engine = MagicMock()
    mock_engine.begin.return_value.__enter__.return_value = mock_connection

    mock_db = MagicMock()
    mock_db.engine = mock_engine
    return mock_db, mock_connection


class TestDeleteOldRowsDatabaseUrlNormalization:
    @pytest.mark.asyncio
    async def test_rewrites_bare_postgresql_url_to_use_psycopg_driver(self) -> None:
        # `get_database_connectionstring` strips the driver suffix for crump's
        # benefit; `Database` (plain SQLAlchemy) needs it restored, or it defaults
        # to the (uninstalled) psycopg2 driver.
        mock_settings = _make_mock_settings()
        mock_db, _ = _make_mock_database()

        with (
            patch(
                "imap_mag.db.DeleteOldRows.get_database_connectionstring",
                new_callable=AsyncMock,
                return_value="postgresql://user:pass@host/db",
            ),
            patch(
                "imap_mag.db.DeleteOldRows.Database", return_value=mock_db
            ) as mock_database_cls,
        ):
            await delete_old_rows(mock_settings, dry_run=True)

        mock_database_cls.assert_called_once_with(
            "postgresql+psycopg://user:pass@host/db"
        )

    @pytest.mark.asyncio
    async def test_leaves_already_qualified_url_unchanged(self) -> None:
        mock_settings = _make_mock_settings()
        mock_db, _ = _make_mock_database()

        with (
            patch(
                "imap_mag.db.DeleteOldRows.get_database_connectionstring",
                new_callable=AsyncMock,
                return_value="postgresql+psycopg://user:pass@host/db",
            ),
            patch(
                "imap_mag.db.DeleteOldRows.Database", return_value=mock_db
            ) as mock_database_cls,
        ):
            await delete_old_rows(mock_settings, dry_run=True)

        mock_database_cls.assert_called_once_with(
            "postgresql+psycopg://user:pass@host/db"
        )


class TestDeleteOldRowsDelete:
    @pytest.mark.asyncio
    async def test_deletes_rows_and_returns_total_rowcount(self) -> None:
        task = _make_task()
        mock_settings = _make_mock_settings(tasks=[task])
        mock_db, mock_connection = _make_mock_database(rowcount=3)

        with (
            patch(
                "imap_mag.db.DeleteOldRows.get_database_connectionstring",
                new_callable=AsyncMock,
                return_value="postgresql+psycopg://user:pass@host/db",
            ),
            patch("imap_mag.db.DeleteOldRows.Database", return_value=mock_db),
        ):
            affected = await delete_old_rows(
                mock_settings,
                dry_run=False,
                datetime_provider=DatetimeProvider(fixed_now=datetime(2026, 7, 21)),
            )

        assert affected == 3
        statement, params = mock_connection.execute.call_args[0]
        assert "DELETE FROM" in str(statement)
        assert "ace_mag_noaa" in str(statement)
        assert params["cutoff"] == datetime(2026, 7, 14)


class TestDeleteOldRowsDryRun:
    @pytest.mark.asyncio
    async def test_counts_rows_without_deleting(self) -> None:
        task = _make_task()
        mock_settings = _make_mock_settings(tasks=[task])
        mock_db, mock_connection = _make_mock_database(scalar_return=5)

        with (
            patch(
                "imap_mag.db.DeleteOldRows.get_database_connectionstring",
                new_callable=AsyncMock,
                return_value="postgresql+psycopg://user:pass@host/db",
            ),
            patch("imap_mag.db.DeleteOldRows.Database", return_value=mock_db),
        ):
            affected = await delete_old_rows(mock_settings, dry_run=True)

        assert affected == 5
        statement = mock_connection.execute.call_args[0][0]
        assert "SELECT COUNT" in str(statement)
        assert "DELETE" not in str(statement)


class TestDeleteOldRowsMissingTable:
    def _make_database_raising(self, orig_exception):
        mock_connection = MagicMock()
        mock_connection.execute.side_effect = ProgrammingError(
            "statement", {}, orig_exception
        )

        mock_engine = MagicMock()
        mock_engine.begin.return_value.__enter__.return_value = mock_connection

        mock_db = MagicMock()
        mock_db.engine = mock_engine
        return mock_db

    @pytest.mark.asyncio
    async def test_continues_when_table_does_not_exist(self) -> None:
        task = _make_task()
        mock_settings = _make_mock_settings(tasks=[task])
        mock_db = self._make_database_raising(
            UndefinedTable('relation "ace_mag_noaa" does not exist')
        )

        with (
            patch(
                "imap_mag.db.DeleteOldRows.get_database_connectionstring",
                new_callable=AsyncMock,
                return_value="postgresql+psycopg://user:pass@host/db",
            ),
            patch("imap_mag.db.DeleteOldRows.Database", return_value=mock_db),
        ):
            affected = await delete_old_rows(mock_settings, dry_run=False)

        assert affected == 0

    @pytest.mark.asyncio
    async def test_subsequent_task_still_runs_after_earlier_task_fails(self) -> None:
        # Regression test: each task must run in its own transaction. Sharing a
        # single transaction across tasks would leave it aborted after the first
        # failure, causing every subsequent task to fail too (even though we
        # already handled/logged the earlier one).
        task_missing = _make_task(name="missing", table="ace_mag_noaa")
        task_ok = _make_task(name="ok", table="ace_wind_noaa")
        mock_settings = _make_mock_settings(tasks=[task_missing, task_ok])

        failing_connection = MagicMock()
        failing_connection.execute.side_effect = ProgrammingError(
            "statement", {}, UndefinedTable('relation "ace_mag_noaa" does not exist')
        )

        ok_connection = MagicMock()
        ok_connection.execute.return_value.rowcount = 4

        mock_engine = MagicMock()
        mock_engine.begin.return_value.__enter__.side_effect = [
            failing_connection,
            ok_connection,
        ]

        mock_db = MagicMock()
        mock_db.engine = mock_engine

        with (
            patch(
                "imap_mag.db.DeleteOldRows.get_database_connectionstring",
                new_callable=AsyncMock,
                return_value="postgresql+psycopg://user:pass@host/db",
            ),
            patch("imap_mag.db.DeleteOldRows.Database", return_value=mock_db),
        ):
            affected = await delete_old_rows(mock_settings, dry_run=False)

        assert affected == 4
        assert mock_engine.begin.call_count == 2

    @pytest.mark.asyncio
    async def test_reraises_other_programming_errors(self) -> None:
        task = _make_task()
        mock_settings = _make_mock_settings(tasks=[task])
        mock_db = self._make_database_raising(
            InsufficientPrivilege("permission denied")
        )

        with (
            patch(
                "imap_mag.db.DeleteOldRows.get_database_connectionstring",
                new_callable=AsyncMock,
                return_value="postgresql+psycopg://user:pass@host/db",
            ),
            patch("imap_mag.db.DeleteOldRows.Database", return_value=mock_db),
            pytest.raises(ProgrammingError),
        ):
            await delete_old_rows(mock_settings, dry_run=False)
