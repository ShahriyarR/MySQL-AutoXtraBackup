#!/bin/sh -e
set -x

# Sort imports one per line, so autoflake can remove unused imports
isort --recursive mysql_autoxtrabackup tests docs scripts --force-single-line-imports
sh ./scripts/format.sh
