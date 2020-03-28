from docker_env_for_test import env_main
from docker_dependencies import install_packages
from docker_run_tests import run_tests
from time import sleep

if __name__ == "__main__":
    container_obj = env_main()
    install_packages(cnt=container_obj)
    run_tests(cnt=container_obj)
