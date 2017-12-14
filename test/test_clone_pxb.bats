#!/usr/bin/env bats

# Edit /etc/bck.conf and specify PXB branches and github link to clone.
# It will create separate folders for each branch.

DIRNAME=$BATS_TEST_DIRNAME

@test "Running test_clone_pxb" {
  run python -m pytest -vv ${DIRNAME}/test_clone_build_start_server.py::TestCloneBuildStartServer::test_clone_pxb
  echo $output
  [ $status -eq 0 ]
}