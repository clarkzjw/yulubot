#!/usr/bin/env python
# -*- coding: utf-8 -*-


from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging

from db import Quote, config, query_yulu_by_text, query_yulu_by_username, query_yulu_by_keyword

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
LOG = logging.getLogger(__name__)


def start(bot, update):
    update.message.reply_text('Hi!')


def help(bot, update):
    update.message.reply_text('Help!')


def listme(bot, update):
    LOG.info(update)
    is_bot_cmd = update["message"]["entities"][0]["type"]
    if is_bot_cmd == "bot_command":
        username = update["message"]["from_user"]["username"]
        count, yulus = query_yulu_by_username(username)
        if count > 0:
            update.message.reply_text("你有 %s 条语录，如下：" % count)
            update.message.reply_text(yulus)

        else:
            update.message.reply_text("你没有语录！")


def forward_message(bot, chat_id, from_chat_id, disable_notification, message_id):
    bot.forwardMessage(chat_id=chat_id,
                       from_chat_id=from_chat_id,
                       disable_notification=disable_notification,
                       message_id=message_id)


def search(bot, update):
    LOG.info(update)
    is_bot_cmd = update["message"]["entities"][0]["type"]
    target_id = update["message"]["from_user"]["id"]
    if is_bot_cmd == "bot_command":
        text = update["message"]["text"][8:]
        results = query_yulu_by_text(text)
        if results is not None:
            LOG.info(results)
            for result in results:
                if "ingayressHZ" in result:
                    forward_message(bot, target_id, "@ingayressHZ", False, result[25:])
                elif "ingayssHZ" in result:
                    forward_message(bot, target_id, "@ingayssHZ", False, result[23:])
        else:
            update.message.reply_text("No result")


def search_by_keyword(bot, update):
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
        results = query_yulu_by_keyword(text)
        total = results["hits"]["total"]
        hits = results["hits"]["hits"]
        if total > 0:
            update.message.reply_text("共有 %s 条语录，分别是" % (total))
            for hit in hits:
                result = hit["_source"]["url"]
                if "ingayressHZ" in result:
                    forward_message(bot, target_id, "@ingayressHZ", False, result[25:])
                elif "ingayssHZ" in result:
                    forward_message(bot, target_id, "@ingayssHZ", False, result[23:])
        elif total == 0:
            update.message.reply_text("No result")


def echo(bot, update):
    channel_post = update["channel_post"]
    update_id = update["update_id"]
    LOG.info(update)

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
    dp.add_handler(CommandHandler("search", search_by_keyword))
    dp.add_handler(CommandHandler("list", listme))

    dp.add_handler(MessageHandler(Filters.text, echo))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    LOG.info("Start")
    main()
