#!/usr/bin/env python
# -*- coding: utf-8 -*-


from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import json

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
LOG = logging.getLogger(__name__)

TOKEN = None
CHANNEL_URL = None


def start(bot, update):
    update.message.reply_text('Hi!')


def help(bot, update):
    update.message.reply_text('Help!')


def echo(bot, update):
    channel_post = update["channel_post"]
    update_id = update["update_id"]

    if update_id and channel_post:
        LOG.info("This is a channel post")
        LOG.info(channel_post)

        forward_date = channel_post["forward_date"]
        forward_from = {}
        forward_from_chat = {}
        try:
            forward_from = channel_post["forward_from"]
            forward_from_chat = channel_post["forward_from_chat"]
        except KeyError:
            LOG.error("Key error")

        message_id = channel_post["message_id"]
        original_user_id = None
        original_user_username = None
        original_user_nickname = None

        if forward_date and message_id:
            LOG.info("This is a forward message")
            text = channel_post["text"] # 原文
            if forward_from:
                original_user = channel_post["forward_from"] # 原始用户
                original_user_id = original_user["id"]
                original_user_username = original_user["username"]
                original_user_nickname = original_user["first_name"] + original_user["last_name"]
            elif forward_from_chat:
                original_user = channel_post["forward_from_chat"]  # 原始用户
                original_user_id = original_user["id"]
                original_user_username = original_user["username"]
                original_user_nickname = original_user["title"]

            url = CHANNEL_URL + str(message_id)

            LOG.info(forward_date)
            LOG.info(update_id)
            LOG.info(text)
            LOG.info(original_user_id)
            LOG.info(original_user_username)
            LOG.info(original_user_nickname)
            LOG.info(CHANNEL_URL + str(message_id))


def error(bot, update, error):
    LOG.warn('Update "%s" caused error "%s"' % (update, error))


def read_config():
    global TOKEN
    global CHANNEL_URL
    config = open("./config.json")
    config = json.load(config)
    TOKEN = config["TOKEN"]
    CHANNEL_URL = config["CHANNEL_URL"]


def main():
    read_config()
    updater = Updater(TOKEN)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(MessageHandler(Filters.text, echo))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    LOG.info("Start")
    main()
