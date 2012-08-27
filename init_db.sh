#!/bin/bash

set -e

PYTHON=bin/python

DB_URI=$(${PYTHON} -c "from talkatv import app
print app.config['SQLALCHEMY_DATABASE_URI']")


if [ -z "$DB_URI" ]; then
    echo "Can't get DB uri from talkatv config. Aborting."
    exit 1
fi

if [ "$1" == "drop" ]; then
    echo "Database URI: $DB_URI"
    echo -n "drop: Are you sure you want to DROP THE ENTIRE DATABASE? [y/n]: "
    read confirm

    case $confirm in
        y)
            ${PYTHON} -c "from talkatv import db; db.drop_all()"
            echo "drop: All tables have been removed from $DB_URI"
            ;;
        *)
            echo "drop: Aborting..."
            exit 1
            ;;
    esac
fi

if [ ! "$2" == "noinit" ]; then
    echo "Creating new tables in $DB_URI ..."
    ${PYTHON} -c "from talkatv import db; db.create_all()"
else
    echo "noinit: Won't create any new tables in $DB_URI"
fi
