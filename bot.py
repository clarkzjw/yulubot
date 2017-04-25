#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from elasticsearch import ConnectionTimeout
from db import Quote, config, query_yulu_by_username, query_yulu_by_keyword

from datadog import ThreadStats
from datadog import initialize

import logging
import logging.config
import loggly.handlers

logging.config.fileConfig('log.conf')
LOG = logging.getLogger(__name__)

options = {
        'api_key': 'e5fc241bb08a9ae8b092765e8cda629b',
        'app_key': 'cf2f3096de4b7c607c67836c0f3680b5f9bb2209'
}

initialize(**options)
stats = ThreadStats()
stats.start()


def start(bot, update):
    stats.increment('start')
    LOG.info("start")
    update.message.reply_text(u"坚持一个高层的原则绝不动摇！")


def forward_message(bot, chat_id, from_chat_id, disable_notification, message_id):
    stats.increment('forward_message')
    LOG.info("forward_message")
    bot.forwardMessage(chat_id=chat_id,
                       from_chat_id=from_chat_id,
                       disable_notification=disable_notification,
                       message_id=message_id)


def search_by_keyword(bot, update):
    stats.increment('search_by_keyword')
    LOG.info("search_by_keyword")

    LOG.info(update)
    is_bot_cmd = update["message"]["entities"][0]["type"]
    target_id = update["message"]["from_user"]["id"]
    message_type = update["message"]["chat"]["type"]
    if is_bot_cmd == "bot_command":
        text = ""
        offset = update["message"]["entities"][0]["length"] + 1
        if message_type == "private":
            text = update["message"]["text"][offset:]
        elif message_type == "group":
            text = update["message"]["text"][offset:]
            target_id = update["message"]["chat"]["id"]
        try:
            results = query_yulu_by_keyword(text)
            stats.increment('keyword.%s' % text)
            total = results["hits"]["total"]
            hits = results["hits"]["hits"]
            if total > 0:
                update.message.reply_text(u"共有 %s 条语录，分别是" % total)
                for hit in hits:
                    result = hit["_source"]["url"]
                    if "ingayressHZ" in result:
                        forward_message(bot, target_id, "@ingayressHZ", False, result[25:])
                    elif "ingayssHZ" in result:
                        forward_message(bot, target_id, "@ingayssHZ", False, result[23:])
            elif total == 0:
                update.message.reply_text(u"No result")
        except ConnectionTimeout:
            LOG.error("ConnectionTimeout")
            update.message.reply_text(u"查询超时")


def search_by_people(bot, update):
    stats.increment('search_by_people')
    LOG.info(update)

    is_bot_cmd = update["message"]["entities"][0]["type"]
    target_id = update["message"]["from_user"]["id"]
    message_type = update["message"]["chat"]["type"]
    if is_bot_cmd == "bot_command":
        username = ""
        offset = update["message"]["entities"][0]["length"] + 1
        if message_type == "private":
            username = update["message"]["text"][offset:]
        elif message_type == "group":
            username = update["message"]["text"][offset:]
            target_id = update["message"]["chat"]["id"]
        if username == "":
            username = update["message"]["from_user"]["username"]

        stats.increment('username.%s' % username)
        count, yulus = query_yulu_by_username(username)
        if count > 0:
            bot.sendMessage(target_id, u"%s 有 %s 条语录，如下：" % (username, count))
            bot.sendMessage(target_id, yulus)
        elif count == 0:
            bot.sendMessage(target_id, u"用户名%s 不存在！" % username)


def echo(bot, update):
    stats.increment("echo")
    
    channel_post = update["channel_post"]
    update_id = update["update_id"]

    if update_id and channel_post:
        forward_date = channel_post["forward_date"]
        forward_from = {}
        forward_from_chat = {}
        try:
            forward_from = channel_post["forward_from"]
            forward_from_chat = channel_post["forward_from_chat"]
        except KeyError:
            LOG.error(u"Key error")

        message_id = channel_post["message_id"]
        original_user_id = None
        original_user_username = None
        original_user_nickname = None

        if forward_date and message_id:
            text = channel_post["text"]
            # 原文
            if forward_from:
                original_user = channel_post["forward_from"]
                # 原始用户
                original_user_id = original_user["id"]
                original_user_username = original_user["username"]
                original_user_nickname = original_user["first_name"] + original_user["last_name"]
            elif forward_from_chat:
                original_user = channel_post["forward_from_chat"]
                # 原始用户
                original_user_id = original_user["id"]
                original_user_username = original_user["username"]
                original_user_nickname = original_user["title"]

            url = config.CHANNEL_URL + str(message_id)
            quote = Quote(id=update_id,
                          fwd_date=forward_date,
                          text=text,
                          ori_user_id=original_user_id,
                          ori_user_username=original_user_username,
                          ori_user_nickname=original_user_nickname,
                          url=url)
            quote.display()
            quote.insert()


def error(bot, update, error):
    stats.increment("error")
    LOG.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    updater = Updater(config.TOKEN)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("search", search_by_keyword))
    dp.add_handler(CommandHandler("list", search_by_people))

    dp.add_handler(MessageHandler(Filters.text, echo))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    LOG.info("Start...")
    main()
