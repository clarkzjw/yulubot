#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import timezone
from pymongo import MongoClient

from models.db import Quote
from models.db import create_db
from models.db import sqlalchemy_session


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
    create_db()
    migrate_from_mongo_to_mysql()