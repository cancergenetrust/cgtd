FROM alpine:latest

RUN apk add --update python py-pip
RUN pip install --upgrade pip
RUN apk add --update uwsgi-python

RUN apk add curl

# requirements to compile uwsgi
RUN apk add --update linux-headers libc-dev build-base musl-dev python-dev
RUN pip install uwsgi

WORKDIR /app
ADD ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

ADD . /app

EXPOSE 5000

CMD uwsgi --ini uwsgi.ini
