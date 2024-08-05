# imap-db: admin util for DB managment and schema updates

This is a utility for managing the database schema and data for the IMAP data pipeline.

## Database commands

CLI Commands to demonstrate database use, and to manage the database have been added. Typer has been used to make a user friendly CLI app.

```bash
# connect to postgress, create the database if required and then create 2 tables based on the ORM.  Thhis comand shows how to use the ORM to create the database schema and populate some rows of data
imap-db create-db

# upgrade the database schema to the latest version. This command uses alembic to apply the migrations in the migrations folder
imap-db upgrade-db

# Use sql alchemy to query the database.
imap-db query-db

# clean up once done and drop the database
imap-db drop-db
```

The database connection details including password are loaded from a config file alembic.ini but can easily be overridden from the SQLALCHEMY_URL environment variable.

## Database migrations

To enable you to manage a production database over time you can use alembic to migrate the data schema. Migrations are the .py files in the `/migrations` folder. The `alembic.ini` file configures the database connection string and the location of the migrations folder. Use the `alembic` command line tool to add and run the migrations.

```bash
export DB_HOST=host.docker.internal
# create database using the postgres client cli tools - apt-get install -y postgresql-client
createdb imap -h $DB_HOST -U postgres --port 5432

# upgrade an empty database to the latest version
alembic upgrade head

# or generate a SQL script so you can apply the migration manually
alembic upgrade head --sql > upgrade.sql

# create a new migration by detetcing changes in the ORM. Will create a new file in the migrations folder
alembic revision --autogenerate -m "Added some table or column"

# Remove the db (postgresql-client)
dropdb imap -h $DB_HOST -U postgres --port 5432
```

## IDE, Docker, Python

The app uses VS code with docker the devcontainers feature to setup a python environment with all tools preinstalled. All you need is vscode and docker to be able develop.

You can connect to the database externally using Azure data studio or some other database tool on 127.0.0.1:5432 as well as using sqltools from within VSCode.

## Command line database access

It is also possible to connect to the database from the command line using psql which is pre-installed in the dev container. The database is exposed on port 5432 on localhost and host "db". The password is in the alembic.ini file.

```bash
$ psql -U postgres -p 5432 -h db -d imap
Password for user postgres:
psql (15.3 (Debian 15.3-0+deb12u1))
Type "help" for help.
                      ^
imap=# SELECT * FROM file;
 id |   name    |       fullname
----+-----------+-----------------------
  1 | file1.txt | /path/to/file1.txt
  2 | file2.txt | /path/to/file2.txt
  3 | file3.txt | /path/to/file3.txt
(3 rows)

imap=# exit
```
