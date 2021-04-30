#!/bin/sh -e
set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place mysql_autoxtrabackup docs scripts tests --exclude=__init__.py
black mysql_autoxtrabackup docs scripts tests
isort --recursive mysql_autoxtrabackup docs scripts tests
