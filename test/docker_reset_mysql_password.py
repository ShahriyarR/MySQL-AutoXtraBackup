import docker
import re
import sys
from typing import Tuple
from subprocess import getstatusoutput

client = docker.from_env()

# TODO: learn how to indicate objects as return type using type hints


def get_container_instance_object(name: str):
    """
    Return the container object of given named container.
    Search for container inside the list of up and running containers.
    :param name: The name of docker container
    :return: Container object, if found the running container
    """
    container = client.containers.list(filters={'name': name, 'status': 'running'})
    if container:
        return container[0]


def get_default_mysql_password(cnt=None) -> str:
    """
    As per doc https://dev.mysql.com/doc/mysql-installation-excerpt/8.0/en/docker-mysql-getting-started.html#docker-starting-mysql-server
    It states that the default generated MySQL root password can be obtained using:
        docker logs container_name 2>&1 | grep GENERATED
        GENERATED ROOT PASSWORD: Axegh3kAJyDLaRuBemecis&EShOs
    As we need to extract and use this password to update the default password.
    :param cnt: The instance object of docker container
    :return: Default password if no error
    """
    output = cnt.logs().decode()
    pattern = r"(ROOT PASSWORD:)\s(.*)\b"
    p = re.compile(pattern)
    match = p.search(output)
    return match.groups()[-1]


def update_default_mysql_password(cnt) -> None:
    """
    Function for updating default generated MySQL docker password to 12345
    As we will use it only for testing there is no problem with such pretty password.
    :param cnt: The instance object of docker container
    :return: None
    """
    password = get_default_mysql_password(cnt)
    base_cmd = "mysql -uroot -p'{}' --connect-expired-password".format(password)
    update_cmd = base_cmd + " -e " + "\"ALTER USER 'root'@'localhost' IDENTIFIED BY '12345'\""
    run_commands(cnt, update_cmd)


def reset_mysql_password(password):
    base_cmd = "mysql -uroot -p'{}' --connect-expired-password".format(password)
    update_cmd = base_cmd + " -e " + "\"ALTER USER 'root'@'localhost' IDENTIFIED BY '12345'\""
    try:
        getstatusoutput(update_cmd)
    except:
        print("something went wrong")


def run_commands(cnt, cmd, work_dir=None) -> Tuple[int, str]:
    """
    Function for running given commands against running docker container
    :param cnt: The instance object of docker container
    :param cmd: The string or list of string commands passed to docker exec_run
    :return exit_code, output: tuple of the result of running command
    """
    exit_code, output = cnt.exec_run(cmd, workdir=work_dir)
    return exit_code, output


def env_main(container_name: str) -> None:
    container_obj = get_container_instance_object(name=container_name)
    update_default_mysql_password(cnt=container_obj)


if __name__ == "__main__":
    # env_main(sys.argv[1])
    print(sys.argv[1])
    reset_mysql_password(sys.argv[1])
