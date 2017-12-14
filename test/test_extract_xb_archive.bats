#!/usr/bin/env bats

# Extracting PXB binary archives to the target folder inside testpath(which is grabbed from config file).

DIRNAME=$BATS_TEST_DIRNAME

@test "Running test_extract_xb_archive" {
  run python -m pytest -vv ${DIRNAME}/test_clone_build_start_server.py::TestCloneBuildStartServer::test_extract_xb_archive
  echo $output
  [ $status -eq 0 ]
}