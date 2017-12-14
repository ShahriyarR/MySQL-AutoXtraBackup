#!/usr/bin/env bats

# Generating specific config files based on PXB and PS versions.
# Those config files can be used with autoxtrabackup by passing to --defaults_file option.

DIRNAME=$BATS_TEST_DIRNAME

@test "Running test_generate_config_files" {
  run python -m pytest -vv ${DIRNAME}/test_config_generator.py::TestConfigGenerator::test_generate_config_files
  echo $output
  [ $status -eq 0 ]
}