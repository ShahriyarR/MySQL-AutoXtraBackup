#!/usr/bin/env bats

# Run this after running test_clone_pxb.bats
# It will build the cloned/specified branches and will create separate binary .tar.gz files for each branch.

DIRNAME=$BATS_TEST_DIRNAME

@test "Running test_build_pxb" {
  run python -m pytest -vv ${DIRNAME}/test_clone_build_start_server.py::TestCloneBuildStartServer::test_build_pxb
  echo $output
  [ $status -eq 0 ]
}