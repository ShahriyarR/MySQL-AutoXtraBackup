#!/usr/bin/env bats

# Renaming basedirs in testpath

DIRNAME=$BATS_TEST_DIRNAME

@test "Running test_rename_basedirs" {
  run python -m pytest -vv ${DIRNAME}/test_clone_build_start_server.py::TestCloneBuildStartServer::test_rename_basedirs
  echo $output
  [ $status -eq 0 ]
}