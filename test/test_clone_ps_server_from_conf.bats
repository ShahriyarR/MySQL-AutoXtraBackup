#!/usr/bin/env bats

# Run this to clone PS(percona server) branches. By default 5.5 , 5,6 and 5.7

DIRNAME=$BATS_TEST_DIRNAME

@test "Running test_clone_ps_server_from_conf" {
  run python -m pytest -vv ${DIRNAME}/test_clone_build_start_server.py::TestCloneBuildStartServer::test_clone_ps_server_from_conf
  echo $output
  [ $status -eq 0 ]
}