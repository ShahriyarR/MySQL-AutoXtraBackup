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

client = docker.from_env()

# TODO: replace all returned bare strings to logging


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
            return "The image is already pulled", False
    client.images.pull(repository='mysql/mysql-server', tag=tag)
    return "Successfully pulled", True


def run_container(name, tag):
    """
    Function for running MySQL container with a given name
    :param name: We expect the name is the development branch name for each test cycle
    :param tag: the tag of image
    :return: See doc https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.ContainerCollection.run
    :raises: See doc https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.ContainerCollection.run
    """
    client.containers.run(image='mysql/mysql-server:{}'.format(tag), name=name, detach=True)
    return True


def stop_container(name):
    """
    Function for stopping docker container with given name
    :param name: The name of docker container
    :return: True if no error
    """
    list_of_running_containers = client.containers.list()
    if list_of_running_containers:
        for container in client.containers.list():
            if container.name == name:
                container.stop()
    return True


def remove_container(name):
    """
    Function for removing docker container with given name
    :param name: The name of docker container
    :return: True if no error
    """
    list_of_running_containers = client.containers.list()
    if list_of_running_containers:
        for container in client.containers.list():
            if container.name == name:
                container.remove()
    return True


def get_current_git_branch():
    """
    Function for returning current branch name
    :return: str
    """
    path = os.path.dirname(__file__)
    repo = Repository(path[:-4])
    return repo.head.shorthand


if __name__ == "__main__":
    pull_image(tag='8.0')
    repo_name = get_current_git_branch()
    run_container(name=repo_name, tag='8.0')
    # Stopping docker container maybe we can use it at the very end of test cycle
    # stop_container(repo_name)
    # remove_container(repo_name)
