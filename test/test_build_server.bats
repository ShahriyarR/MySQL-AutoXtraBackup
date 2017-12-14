#!/usr/bin/env bats

# Run this BATS file to build PS servers from source.

DIRNAME=$BATS_TEST_DIRNAME

@test "Running test_build_server" {
  run python -m pytest -vv ${DIRNAME}/test_clone_build_start_server.py::TestCloneBuildStartServer::test_build_server
  echo $output
  [ $status -eq 0 ]
}