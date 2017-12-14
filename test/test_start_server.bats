#!/usr/bin/env bats

# Starting PS servers with default values(executing start script inside basedirs).

DIRNAME=$BATS_TEST_DIRNAME

@test "Running test_start_server" {
  run python -m pytest -vv ${DIRNAME}/test_clone_build_start_server.py::TestCloneBuildStartServer::test_start_server
  echo $output
  [ $status -eq 0 ]
}