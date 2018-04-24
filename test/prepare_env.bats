#!/usr/bin/env bats

# Run this BATS file to prepare full test environment

DIRNAME=$BATS_TEST_DIRNAME

@test "Running test_clone_percona_qa" {
  run python -m pytest -vv ${DIRNAME}/test_clone_build_start_server.py::TestCloneBuildStartServer::test_clone_percona_qa
  echo $output
  [ $status -eq 0 ]
}

@test "Running test_clone_ps_server_from_conf" {
  run python -m pytest -vv ${DIRNAME}/test_clone_build_start_server.py::TestCloneBuildStartServer::test_clone_ps_server_from_conf
  echo $output
  [ $status -eq 0 ]
}

@test "Running test_clone_pxb" {
  run python -m pytest -vv ${DIRNAME}/test_clone_build_start_server.py::TestCloneBuildStartServer::test_clone_pxb
  echo $output
  [ $status -eq 0 ]
}

@test "Running test_build_pxb" {
  run python -m pytest -vv ${DIRNAME}/test_clone_build_start_server.py::TestCloneBuildStartServer::test_build_pxb
  echo $output
  [ $status -eq 0 ]
}

@test "Running test_build_server" {
  run python -m pytest -vv ${DIRNAME}/test_clone_build_start_server.py::TestCloneBuildStartServer::test_build_server
  echo $output
  [ $status -eq 0 ]
}

@test "Running test_rename_basedirs" {
  run python -m pytest -vv ${DIRNAME}/test_clone_build_start_server.py::TestCloneBuildStartServer::test_rename_basedirs
  echo $output
  [ $status -eq 0 ]
}

@test "Running test_prepare_startup" {
  run python -m pytest -vv ${DIRNAME}/test_clone_build_start_server.py::TestCloneBuildStartServer::test_prepare_startup
  echo $output
  [ $status -eq 0 ]
}

@test "Running test_prepare_start_dynamic" {
  run python -m pytest -vv ${DIRNAME}/test_clone_build_start_server.py::TestCloneBuildStartServer::test_prepare_start_dynamic
  echo $output
  [ $status -eq 0 ]
}

@test "Running test_start_server" {
  run python -m pytest -vv ${DIRNAME}/test_clone_build_start_server.py::TestCloneBuildStartServer::test_start_server
  echo $output
  [ $status -eq 0 ]
}

@test "Running test_extract_xb_archive" {
  run python -m pytest -vv ${DIRNAME}/test_clone_build_start_server.py::TestCloneBuildStartServer::test_extract_xb_archive
  echo $output
  [ $status -eq 0 ]
}

@test "Running test_generate_config_files" {
  run python -m pytest -vv ${DIRNAME}/test_config_generator.py::TestConfigGenerator::test_generate_config_files
  echo $output
  [ $status -eq 0 ]
}