FROM python:alpine
LABEL maintainer clarkzjw <clarkzjw@gmail.com>

WORKDIR /usr/src/app
ENV PYTHONPATH /usr/src/app

COPY requirements.txt /usr/src/app/requirements.txt

RUN \
    pip install python-telegram-bot && \
    pip install -r requirements.txt

COPY . /usr/src/app

CMD "python3" "/usr/src/app/bot.py"
