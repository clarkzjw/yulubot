FROM python:3.7.0
LABEL maintainer clarkzjw <clarkzjw@gmail.com>

WORKDIR /usr/src/app
ENV PYTHONPATH /usr/src/app

COPY requirements.txt /usr/src/app/requirements.txt

RUN pip install -r requirements.txt

COPY . /usr/src/app

EXPOSE 8080

CMD "python3" "/usr/src/app/bot.py"
