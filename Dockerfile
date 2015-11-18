FROM ubuntu:12.04

MAINTAINER siimeon<siimeon.developer@gmail.com>

RUN apt-get update && apt-get install -y python python-django git

RUN git clone https://github.com/siimeon/Kipa.git /root/kipa

EXPOSE 8000

WORKDIR /root/kipa/web

CMD git pull &&  python manage.py runserver 0.0.0.0:8000
