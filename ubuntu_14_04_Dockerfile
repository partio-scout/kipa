FROM ubuntu

MAINTAINER siimeon<siimeon.developer@gmail.com>

RUN apt-get update && apt-get install -y git python python-pip

RUN pip install Django==1.4

RUN git clone https://github.com/siimeon/Kipa.git /root/kipa

EXPOSE 8000

WORKDIR /root/kipa/web

CMD git pull &&  python manage.py runserver 0.0.0.0:8000
