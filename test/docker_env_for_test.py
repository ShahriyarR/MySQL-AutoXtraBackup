"""
docker_env_for_test.py file contains actions for preparing docker environment for running tests.
The logic is, kind of simple.
It requires to pull official MySQL docker image with given tag.
And then run the given container based on current development active branch.
And after running all kind of tests inside docker container it should stop and remove container.
"""

import docker
from pygit2 import Repository
import os
import re

client = docker.from_env()


def pull_image(tag):
    """
    Function for pulling official MySQL docker image
    :param tag: the tag of image
    :return: Message, True/False
    :raises: docker.errors.APIError
    """
    full_image_name = 'mysql/mysql-server:{}'.format(tag)
    list_of_local_images = client.images.list(full_image_name)
    for image in list_of_local_images:
        if image.tags[0] == full_image_name:
            return False
    client.images.pull(repository='mysql/mysql-server', tag=tag)
    return True


def run_container(name, tag):
    """
    Function for running MySQL container with a given name
    :param name: We expect the name is the development branch name for each test cycle
    :param tag: the tag of image
    :return: See doc https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.ContainerCollection.run
    :raises: See doc https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.ContainerCollection.run
    """
    container_obj = get_container_instance_object(name)
    if container_obj:
        stop_container(container_obj)
        remove_container(container_obj)

    client.containers.run(image='mysql/mysql-server:{}'.format(tag), name=name, detach=True)
    return True


def stop_container(container_obj):
    """
    Function for stopping docker container with given name
    :param container_obj: The instance object of docker container
    :return: True if no error
    """
    container_obj.stop()
    return True


def remove_container(container_obj):
    """
    Function for removing docker container with given name
    :param container_obj: The instance object of docker container
    :return: True if no error
    """
    container_obj.remove()
    return True


def get_default_mysql_password(name):
    """
    As per doc https://dev.mysql.com/doc/mysql-installation-excerpt/8.0/en/docker-mysql-getting-started.html#docker-starting-mysql-server
    It states that the default generated MySQL root password can be obtained using:
        docker logs container_name 2>&1 | grep GENERATED
        GENERATED ROOT PASSWORD: Axegh3kAJyDLaRuBemecis&EShOs
    As we need to extract and use this password to update the default password.
    :param name: The name of docker container
    :return: Default password if no error
    """
    output = get_container_instance_object(name).logs().decode()
    pattern = r"(ROOT PASSWORD:)\s(.*)\b"
    p = re.compile(pattern)
    match = p.search(output)
    return match.groups()[-1]


def update_default_mysql_password(name):
    """
    Function for updating default generated MySQL docker password to 12345
    As we will use it only for testing there is no problem with such pretty password.
    :param name: The name of docker container
    :return: None
    """
    password = get_default_mysql_password(name)
    base_cmd = "mysql -uroot -p'{}' --connect-expired-password".format(password)
    update_cmd = base_cmd + " -e " + "\"ALTER USER 'root'@'localhost' IDENTIFIED BY '12345'\""
    get_container_instance_object(name).exec_run(update_cmd)


def get_container_instance_object(name):
    """
    Return the container object of given named container.
    Search for container inside the list of up and running containers.
    :param name: The name of docker container
    :return: Container object if found the running container
    """
    list_of_running_containers = client.containers.list()
    if list_of_running_containers:
        for container in list_of_running_containers:
            if container.name == name:
                return container


def get_current_git_branch():
    """
    Function for returning current branch name
    :return: str
    """
    path = os.path.dirname(__file__)
    repo = Repository(path[:-4])
    return repo.head.shorthand


if __name__ == "__main__":
    repo_name = get_current_git_branch()
    pull_image(tag='8.0')
    run_container(name=repo_name, tag='8.0')
    from time import sleep
    sleep(10)
    update_default_mysql_password(repo_name)
    # Stopping docker container maybe we can use it at the very end of test cycle
    # stop_container(repo_name)
    # remove_container(repo_name)
