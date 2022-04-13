FROM mysql:8.0-oracle
USER root
WORKDIR /opt
COPY . /opt/MySQL-AutoXtraBackup

ENV MYSQL_ROOT_PASSWORD=12345

RUN microdnf install yum
RUN yum install -y git
RUN yum install -y python38
RUN yum install -y vim
RUN yum install -y perl
RUN yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm
RUN yum install -y https://repo.percona.com/yum/percona-release-latest.noarch.rpm
RUN yum install -y libev
RUN percona-release enable-only tools
RUN yum install -y --exclude=Percona-Server\* percona-xtrabackup-80
RUN yum install -y qpress
RUN yum install -y python38-pip
RUN cd /opt && \
    git clone https://github.com/sstephenson/bats.git && \
    cd bats && \
    ./install.sh /usr/local
EXPOSE 8080
RUN cd /opt/MySQL-AutoXtraBackup && \
    pip3.8 install -U pip && \
    pip3.8 install flit && \
    FLIT_ROOT_INSTALL=1 flit install --symlink

WORKDIR /opt/MySQL-AutoXtraBackup/mysql_autoxtrabackup
CMD ["mysqld", "--character-set-server=utf8mb4", "--collation-server=utf8mb4_unicode_ci"]
#CMD ["uvicorn", "api.main:app", "--port", "8080"]
