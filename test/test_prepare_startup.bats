#!/usr/bin/env bats

# Running startup.sh file from percona-qa repo inside each PS basedir.

DIRNAME=$BATS_TEST_DIRNAME

@test "Running test_prepare_startup" {
  run python -m pytest -vv ${DIRNAME}/test_clone_build_start_server.py::TestCloneBuildStartServer::test_prepare_startup
  echo $output
  [ $status -eq 0 ]
}