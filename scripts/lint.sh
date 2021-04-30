#!/usr/bin/env bash

set -e
set -x

mypy mysql_autoxtrabackup
flake8 mysql_autoxtrabackup tests
black mysql_autoxtrabackup tests --check
isort --recursive mysql_autoxtrabackup tests docs scripts --check-only