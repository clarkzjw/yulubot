FROM python:3.6.0
LABEL maintainer clarkzjw <clarkzjw@gmail.com>

RUN \
    apt-get update && \
    apt-get -y install vim

WORKDIR /usr/src/app
ENV PYTHONPATH /usr/src/app

COPY requirements.txt /usr/src/app/requirements.txt

RUN \
    pip install python-telegram-bot && \
    pip install -r requirements.txt

COPY . /usr/src/app

CMD "python3" "/usr/src/app/bot.py"