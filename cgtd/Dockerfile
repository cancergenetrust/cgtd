FROM alpine:latest

RUN apk add --update python py-pip
RUN pip install --upgrade pip
RUN apk add --update uwsgi-python

RUN apk add curl

WORKDIR /app
ADD ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

ADD . /app

CMD uwsgi --ini uwsgi.ini
