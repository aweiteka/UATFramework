FROM fedora:20
MAINTAINER Aaron Weitekamp <aweiteka@redhat.com>

RUN yum install -y python-pip python-devel gcc
ADD features /uatframework/features
ADD requirements.txt /uatframework/
RUN pip install -r /uatframework/requirements.txt
WORKDIR /uatframework
ENTRYPOINT behave
