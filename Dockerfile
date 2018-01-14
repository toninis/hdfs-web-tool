FROM centos:latest

MAINTAINER Antonis Stamatiou "stamatiou.antonis@protonmail.com"

RUN yum update -y && yum install -y wget && wget http://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
RUN rpm -ivh epel-release-latest-7.noarch.rpm
RUN yum update -y && yum install --enablerepo=epel -y python3.5 python-pip

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app

EXPOSE 5000

ENTRYPOINT [ "python" ]

CMD [ "server.py" ]
