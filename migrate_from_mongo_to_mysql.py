#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from pymongo import MongoClient
from models.db import Quote, config
from models.db import sqlalchemy_session

from models.db import ACTION_BOT_FORWARD_MSG, ACTION_BOT_QUERY_BY_KEYWORD, ACTION_BOT_QUERY_BY_PEOPLE
from models.db import ACTION_BOT_START_BY_USER, ACTION_BOT_INSERT_QUOTE

from utils import get_tg_user_from_update, add_action
from utils import query_yulu_by_keyword, query_yulu_by_username, insert_quote

from datetime import timezone
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
LOG = logging.getLogger(__name__)


def migrate_from_mongo_to_mysql():
    uri = "mongodb://54.65.15.71:27017/hzresquote"
    conn = MongoClient(uri)
    database = conn["hzresquote"]
    collection = database.entries
    yulus = collection.find()
    for yulu in yulus:
        fwd_date = yulu["fwd_date"]
        quote = Quote(
            id=yulu["id"],
            fwd_date=fwd_date.replace(tzinfo=timezone.utc).timestamp(),
            text=yulu["text"],
            ori_user_id=yulu["ori_user_id"],
            ori_user_username=yulu["ori_user_username"],
            ori_user_nickname=yulu["ori_user_nickname"],
            ori_url=yulu["url"]
        )
        with sqlalchemy_session() as session:
            session.add(quote)
            session.commit()


if __name__ == "__main__":
    migrate_from_mongo_to_mysql()