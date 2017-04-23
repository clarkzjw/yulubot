FROM ubuntu:16.04
LABEL maintainer clarkzjw <clarkzjw@gmail.com>

RUN \
  sed -i 's/# \(.*multiverse$\)/\1/g' /etc/apt/sources.list && \
  apt-get update && \
  apt-get -y upgrade && \
  apt-get install -y git wget build-essential libconfig-dev libjansson-dev libevent-dev liblua5.2-dev gcc g++ make && \
  rm -rf /var/lib/apt/lists/*

RUN \
  wget https://valtman.name/files/telegram-cli-1222 && \
  mv telegram-cli-1222 telegram-cli && \
  chmod +x telegram-cli

EXPOSE 9009

CMD bash
