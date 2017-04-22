#!/usr/bin/env python
# -*- coding: utf-8 -*-


from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging

from db import Quote, config

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
LOG = logging.getLogger(__name__)


def start(bot, update):
    update.message.reply_text('Hi!')


def help(bot, update):
    update.message.reply_text('Help!')


def echo(bot, update):
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
            LOG.error("Key error")

        message_id = channel_post["message_id"]
        original_user_id = None
        original_user_username = None
        original_user_nickname = None

        if forward_date and message_id:
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
    LOG.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    updater = Updater(config.TOKEN)

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
