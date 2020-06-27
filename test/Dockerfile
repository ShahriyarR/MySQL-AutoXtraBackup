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
RUN cd /opt && \
    git clone https://github.com/sstephenson/bats.git && \
    cd bats && \
    ./install.sh /usr/local
ARG GIT_BRANCH_NAME
RUN cd /opt && \
    git clone -b $GIT_BRANCH_NAME https://github.com/ShahriyarR/MySQL-AutoXtraBackup.git
