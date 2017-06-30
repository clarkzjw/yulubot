#!/usr/bin/env python
# -*- coding: utf-8 -*-

from models.db import sqlalchemy_session, Action, Quote, Blacklist

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
LOG = logging.getLogger(__name__)


def get_tg_user_from_update(update):
    chat = update["message"]["chat"]
    tg_id = chat["id"]
    tg_username = chat["username"]
    tg_nickname = " ".join(x for x in [chat["first_name"], chat["last_name"]] if x is not None)
    return tg_id, tg_username, tg_nickname


def add_action(user, action, comments=None):
    with sqlalchemy_session() as session:
        action = Action(
            user_tg_id=user[0],
            user_tg_name=user[1],
            user_tg_nickname=user[2],
            action=action,
            comments=comments
        )
        session.add(action)
        session.commit()


def insert_quote(quote):
    with sqlalchemy_session() as session:
        session.add(quote)
        session.commit()


def query_yulu_by_keyword(text):
    with sqlalchemy_session() as session:
        yulus = session.query(Quote).filter(
            Quote.text.like("%"+text+"%")
        ).all()
        return yulus


def query_yulu_by_username(username):
    result = []
    count = 0
    with sqlalchemy_session() as session:
        yulus = session.query(Quote).filter(
            Quote.ori_user_username==username
        ).all()
        count = len(yulus)
        for yulu in yulus:
            result.append(yulu.ori_url)
    return count, result


def check_blacklist(tg_id):
    with sqlalchemy_session() as session:
        user = session.query(Blacklist).filter(
            Blacklist.tg_id == tg_id
        ).first()
        if user:
            return True
        return False