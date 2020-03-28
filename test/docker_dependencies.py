"""
This file is for storing global list or tuple of dependency installation and environment creation.
The commands will be executed sequentially in order.
As we use official MySQL docker image provided by Oracle it is based on OEK7 or CentOS 7.
So the commands are for RHEL or yum
"""
from docker_env_for_test import run_commands, get_current_git_branch, get_container_instance_object

name = get_current_git_branch()
cnt = get_container_instance_object(name)

CMD = [
    ("yum install git",),
    ("yum install python3",),
    ("git clone -b {} {}".format(name, 'https://github.com/ShahriyarR/MySQL-AutoXtraBackup.git'), '/home'),
    ("python3 setup.py install", '/home/MySQL-AutoXtraBackup'),
]


def install_packages():
    for cmd in CMD:
        if len(cmd) == 1:
            print(run_commands(cnt, cmd[0]))
        else:
            print(run_commands(cnt, cmd[0], cmd[1]))


if __name__ == "__main__":
    install_packages()

