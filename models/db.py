# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: clarkzjw
# @Date:   2017-05-27


from sqlalchemy import create_engine, Column, String, Integer, TEXT
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.mysql import DOUBLE
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager

from uuid import uuid4
import os
import time
import logging


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
LOG = logging.getLogger(__name__)

Base = declarative_base()


class Config:
    def __init__(self):
        self.TOKEN = os.getenv("TOKEN", None)
        self.MYSQL_URI = os.getenv("MYSQL_URI", "mysql+pymysql://root:root@127.0.0.1:3306/nembot")

config = Config()

engine = create_engine(config.MYSQL_URI, echo=False, encoding="utf8", connect_args={'charset': 'utf8'})


@contextmanager
def sqlalchemy_session():
    session = sessionmaker(bind=engine, expire_on_commit=False)()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.expunge_all()
        session.close()


class Info(Base):

    __tablename__ = "info"

    id = Column(Integer, primary_key=True)
    user_tg_id = Column(String(255), nullable=False)
    user_tg_name = Column(String(255), nullable=False)

    date = Column(DOUBLE, nullable=False, default=lambda: time.time())


ACTION_BOT_START_BY_USER = "action_bot_start_by_user"
ACTION_BOT_QUERY_BY_KEYWORD = "action_bot_query_by_keyword"
ACTION_BOT_QUERY_BY_PEOPLE = "action_bot_query_by_people"
ACTION_BOT_FORWARD_MSG = "action_bot_forward_msg"


class Action(Base):

    __tablename__ = "action"

    id = Column(String(255), primary_key=True, default=lambda: str(uuid4()))
    user_tg_id = Column(String(255), nullable=False)
    user_tg_name = Column(String(255), nullable=True)

    action = Column(String(255), nullable=False)

    date = Column(DOUBLE, nullable=False, default=lambda :time.time())


class Quote(Base):

    __tablename__ = "quote"

    id = Column(String(255), primary_key=True, nullable=False)
    fwd_date = Column(DOUBLE, nullable=False)
    text = Column(TEXT, nullable=False)
    ori_user_id = Column(String(255), nullable=False)
    ori_user_username = Column(String(255), nullable=True)
    ori_user_nickname = Column(String(255), nullable=True)
    ori_url = Column(String(255), nullable=False)

    # def insert(self):
    #     uri = config.MONGO_URI
    #     conn = MongoClient(uri)
    #     database = conn[config.DB_NAME]
    #     collection = database.entries
    #     count = collection.find({"text": self.text, "ori_user_id": self.ori_user_id}).count()
    #     if count > 0:
    #         LOG.info("record exists")
    #         return
    #
    #     post = {"id": self.id,
    #             "fwd_date": self.fwd_date,
    #             "text": self.text,
    #             "ori_user_id": self.ori_user_id,
    #             "ori_user_username": self.ori_user_username,
    #             "ori_user_nickname": self.ori_user_nickname,
    #             "url": self.url}
    #     collection.insert(post)
    #     conn.close()


def query_yulu_by_text(text):
    pass
    # uri = config.MONGO_URI
    # conn = MongoClient(uri)
    # database = conn[config.DB_NAME]
    # collection = database.entries
    # yulus = collection.find({"text": text})
    # result = []
    # if yulus.count() > 0:
    #     for yulu in yulus:
    #         LOG.info(yulu)
    #         result.append(yulu["url"])
    #
    # return result


def query_yulu_by_keyword(text):
    pass
    # from elasticsearch import Elasticsearch
    # es = Elasticsearch(config.ES_URL)
    # body = {
    #     "from": 0, "size": 100,
    #     "query": {
    #         "bool": {
    #             "must": [
    #                 {
    #                     "match_phrase": {
    #                         "text": text
    #                     }
    #                 }
    #             ]
    #         }
    #     }
    # }
    #
    # res = es.search(index=config.DB_NAME, doc_type="entries", body=body)
    # LOG.info(res)
    # return res


def query_yulu_by_username(username):
    pass
    # uri = config.MONGO_URI
    # conn = MongoClient(uri)
    # database = conn[config.DB_NAME]
    # collection = database.entries
    # yulus = collection.find({"ori_user_username": username})
    # count = yulus.count()
    # result = []
    # if count > 0:
    #     for yulu in yulus:
    #         LOG.info(yulu)
    #         result.append(yulu["url"])
    # elif count == 0:
    #     pass
    # return count, result


def query_similar_username(username):

    pass