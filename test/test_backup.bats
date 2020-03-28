#!/usr/bin/env bats

# Run this BATS file to run Backup related tests

DIRNAME=$BATS_TEST_DIRNAME

@test "Running test_create_mysql_client_command" {
run python3 -m pytest -vv ${DIRNAME}/test_backup.py::TestBackup::test_create_mysql_client_command
  echo $output
  [ $status -eq 0 ]
}

@test "Running test_full_backup_without_tag" {
run python3 -m pytest -vv ${DIRNAME}/test_backup.py::TestBackup::test_full_backup_without_tag
  echo $output
  [ $status -eq 0 ]
}

@test "Running test_full_backup_with_tag" {
run python3 -m pytest -vv ${DIRNAME}/test_backup.py::TestBackup::test_full_backup_with_tag
  echo $output
  [ $status -eq 0 ]
}