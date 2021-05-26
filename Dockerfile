FROM debian:stretch-slim

ARG project_dir=/project/
ADD app/app.py $project_dir
WORKDIR $project_dir

RUN apt-get update
RUN apt-get -y install locales && \
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TZ JST-9
ENV TERM xterm

RUN set -xe \
    && apt-get -y update \
    && apt-get -y install python3-pip

RUN pip3 install --upgrade pip
RUN apt-get update && apt-get -y dist-upgrade
RUN apt-get -y install build-essential libssl-dev libffi-dev python3.5 libblas3$
RUN apt-get -y install python3-numpy python3-sklearn
RUN apt-get -y install python3-pandas

RUN pip3 install requests
RUN pip3 install flask
RUN pip3 install flask_restful
