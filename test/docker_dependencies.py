"""
This file is for storing global list or tuple of dependency installation and environment creation.
The commands will be executed sequentially in order.
As we use official MySQL docker image provided by Oracle it is based on OEK7 or CentOS 7.
So the commands are for RHEL or yum
"""
from docker_env_for_test import run_commands, get_current_git_branch, get_container_instance_object

name = get_current_git_branch()

CMD = [
    ("yum install -y git",),
    ("yum install -y python3",),
    ("yum install -y vim",),
    ("yum install -y perl",),
    ("yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm",),
    ("yum install -y https://repo.percona.com/yum/percona-release-latest.noarch.rpm",),
    ("percona-release enable-only tools",),
    ("yum install -y percona-xtrabackup-80",),
    ("git clone -b {} {}".format(name, 'https://github.com/ShahriyarR/MySQL-AutoXtraBackup.git'), '/home'),
    ("python3 setup.py install", '/home/MySQL-AutoXtraBackup'),
    ("git clone https://github.com/sstephenson/bats.git", '/home'),
    ("./install.sh /usr/local", '/home/bats')
]


def install_packages(cnt):
    for cmd in CMD:
        if len(cmd) == 1:
            print(run_commands(cnt, cmd[0]))
        else:
            print(run_commands(cnt, cmd[0], cmd[1]))


if __name__ == "__main__":
    cnt = get_container_instance_object(name)
    install_packages(cnt=cnt)

