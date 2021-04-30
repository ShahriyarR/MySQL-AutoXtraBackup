FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

WORKDIR /app

RUN git clone https://github.com/sstephenson/bats.git && \
    cd bats && \
    ./install.sh /usr/local

RUN apt-get update && apt-get install -y lsb-release
RUN apt install -y libncurses5
RUN apt-get install -y vim
RUN wget https://repo.percona.com/apt/percona-release_latest.$(lsb_release -sc)_all.deb
RUN dpkg -i percona-release_latest.$(lsb_release -sc)_all.deb
RUN percona-release enable-only tools release
RUN apt-get update
RUN apt-get install -y percona-xtrabackup-80
RUN apt-get install -y qpress

COPY ./ /app
RUN pip install --upgrade pip &&  \
    pip install -r requirements.txt

RUN python3 setup.py install

ENV MODULE_NAME="api.main"
