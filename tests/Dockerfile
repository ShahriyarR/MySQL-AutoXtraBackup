FROM mysql:8.0-oracle
USER root
WORKDIR /opt
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
ARG GIT_BRANCH_NAME
RUN cd /opt && \
    git clone -b $GIT_BRANCH_NAME https://github.com/ShahriyarR/MySQL-AutoXtraBackup.git && \
    cd /opt/MySQL-AutoXtraBackup && \
    pip3.8 install -U pip && \
    pip3.8 install flit && \
    FLIT_ROOT_INSTALL=1 flit install

RUN yum groupinstall -y "Development Tools"
RUN yum -y install python38-devel.x86_64
RUN yum -y install libffi
RUN yum -y install libffi-devel
RUN cd /opt/MySQL-AutoXtraBackup/tests && \
    pip3.8 install -r requirements.txt

EXPOSE 8080

WORKDIR /opt/MySQL-AutoXtraBackup
RUN cd /opt/MySQL-AutoXtraBackup && git pull
RUN pip3.8 install uvicorn
RUN pip3.8 install fastapi

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
#CMD ["uvicorn", "api.main:app", "--port", "8080"]
