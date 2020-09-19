FROM mysql/mysql-server:8.0
COPY entrypoint.sh /entrypoint.sh
USER root
WORKDIR /opt
RUN yum install -y git
RUN yum install -y python3
RUN yum install -y vim
RUN yum install -y perl
RUN yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
RUN yum install -y https://repo.percona.com/yum/percona-release-latest.noarch.rpm
RUN yum install -y libev
RUN percona-release enable-only tools
RUN yum install -y --exclude=Percona-Server\* percona-xtrabackup-80
RUN yum install -y qpress
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

RUN cd /opt/MySQL-AutoXtraBackup && \
    pipenv --python `which python3` install

RUN cd /opt/MySQL-AutoXtraBackup/api
CMD ["uvicorn", "main:app", "--reload"]

