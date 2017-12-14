#!/usr/bin/env bats

# Running this to create start_dynamic scripts in basedirs, it is needed for slave startup etc.

DIRNAME=$BATS_TEST_DIRNAME

@test "Running test_prepare_start_dynamic" {
  run python -m pytest -vv ${DIRNAME}/test_clone_build_start_server.py::TestCloneBuildStartServer::test_prepare_start_dynamic
  echo $output
  [ $status -eq 0 ]
}