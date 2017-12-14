#!/usr/bin/env bats

# This is for cloning percona-qa repo.
# It is crucial because we are going to use some setup scripts from this repo.

DIRNAME=$BATS_TEST_DIRNAME

@test "Running test_clone_percona_qa" {
  run python -m pytest -vv ${DIRNAME}/test_clone_build_start_server.py::TestCloneBuildStartServer::test_clone_percona_qa
  echo $output
  [ $status -eq 0 ]
}