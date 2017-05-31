# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: clarkzjw
# @Date:   2017-05-27

from sqlalchemy import create_engine, Column, String, TEXT
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

ACTION_BOT_START_BY_USER = "action_bot_start_by_user"
ACTION_BOT_QUERY_BY_KEYWORD = "action_bot_query_by_keyword"
ACTION_BOT_QUERY_BY_PEOPLE = "action_bot_query_by_people"


class Config:
    def __init__(self):
        self.CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/ingayssHZ/")
        self.TOKEN = os.getenv("TOKEN", None)
        self.MYSQL_URI = os.getenv("MYSQL_URI", "mysql+pymysql://root:root@127.0.0.1:3306/quote_bot")

config = Config()
engine = create_engine(config.MYSQL_URI, echo=False, encoding="utf8", connect_args={'charset': 'utf8mb4'})
Base.metadata.create_all(engine)


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


def create_db():
    engine = create_engine(config.MYSQL_URI, echo=False, encoding="utf8", connect_args={'charset': 'utf8mb4'})
    Base.metadata.create_all(engine)


class Action(Base):

    __tablename__ = "action"

    id = Column(String(255), primary_key=True, default=lambda: str(uuid4()))

    user_tg_id = Column(String(255), nullable=False)
    user_tg_name = Column(String(255), nullable=True)
    user_tg_nickname = Column(String(255), nullable=True)

    action = Column(String(255), nullable=False)
    comments = Column(String(255), nullable=True)

    date = Column(DOUBLE, nullable=False, default=lambda: time.time())


class Quote(Base):

    __tablename__ = "quote"

    id = Column(String(255), primary_key=True, nullable=False, default=lambda: str(uuid4()))
    fwd_date = Column(DOUBLE, nullable=False)
    text = Column(TEXT, nullable=False)
    ori_user_id = Column(String(255), nullable=False)
    ori_user_username = Column(String(255), nullable=True)
    ori_user_nickname = Column(String(255), nullable=True)
    ori_url = Column(String(255), nullable=False)

