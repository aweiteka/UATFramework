FROM fedora:20
MAINTAINER Aaron Weitekamp <aweiteka@redhat.com>

RUN yum install -y python-pip python-devel gcc
ADD requirements.txt /uatframework/
RUN pip install -r /uatframework/requirements.txt
ADD features /uatframework/features
ADD steps /uatframework/steps
ADD environment.py /uatframework/environment.py
ADD central_ci_dynamic_hosts.py /uatframework/central_ci_dynamic_hosts.py
WORKDIR /uatframework
ENTRYPOINT ["/usr/bin/behave"]
