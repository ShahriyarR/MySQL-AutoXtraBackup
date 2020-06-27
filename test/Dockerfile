FROM mysql/mysql-server:8.0
USER root
WORKDIR /opt
RUN yum install -y git
RUN yum install -y python3
RUN yum install -y vim
RUN yum install -y perl
RUN yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
RUN yum install -y https://repo.percona.com/yum/percona-release-latest.noarch.rpm
RUN percona-release enable-only tools
RUN yum install -y percona-xtrabackup-80
RUN yum install -y python3-pip
RUN cd /opt && \
    git clone https://github.com/sstephenson/bats.git && \
    cd bats && \
    ./install.sh /usr/local
ARG GIT_BRANCH_NAME
RUN cd /opt && \
    git clone -b $GIT_BRANCH_NAME https://github.com/ShahriyarR/MySQL-AutoXtraBackup.git && \
    cd /opt/MySQL-AutoXtraBackup && \
    python3 setup.py install

RUN cd /opt/MySQL-AutoXtraBackup/test && \
    pip3 install -r requirements.txt

# TODO: figure out the way to fix this issue
# TODO: Unable to update the root password
RUN echo 'echo "${MYSQL_ROOT_PASSWORD}"' >> /entrypoint.sh
RUN echo 'python3 /opt/MySQL-AutoXtraBackup/test/docker_reset_mysql_password.py "${MYSQL_ROOT_PASSWORD}"' >> /entrypoint.sh
