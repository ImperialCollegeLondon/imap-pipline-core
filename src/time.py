"""Definitions of supported time formats."""

from datetime import datetime

import astropy.time


class Time:
    """Define time and conversions."""

    date: datetime
    gps: int

    def __init__(self, date: datetime, gsp: int) -> None:
        """Initialize Time object."""

        self.date = date
        self.gps = gsp

    @staticmethod
    def from_gps(gps: int):
        """Create Time object from GSP time."""

        date = astropy.time.Time(gps / 1e6, format="gps").datetime

        return Time(date, gps)

    @staticmethod
    def from_datetime(date: datetime):
        """Create Time object from datetime object."""

        gps = astropy.time.Time(date).gps * 1e6

        return Time(date, gps)
