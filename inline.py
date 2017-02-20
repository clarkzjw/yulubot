# -*- coding: utf-8 -*-

from uuid import uuid4

import re
import json
from pymongo import MongoClient
from telegram import InlineQueryResultArticle,  \
    InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
from telegram.ext import MessageHandler, Filters
import logging

MONGO_HOST = ''
DBName = ''


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def start(bot, update):
    update.message.reply_text('Hi!')


def help(bot, update):
    update.message.reply_text('Help!')


def escape_markdown(text):
    """Helper function to escape telegram markup symbols"""
    escape_chars = '\*_`\['
    return re.sub(r'([%s])' % escape_chars, r'\\\1', text)


def find_message_record(query):
    global MONGO_HOST
    uri = MONGO_HOST
    conn = MongoClient(uri)
    database = conn[DBName]
    collection = database.entries
    results = collection.find({"text": {'$regex': query}})
    conn.close()
    count = results.count()
    if count == 0:
        return "Not found"
    else:
        return results


def inlinequery(bot, update):
    query_string = update.inline_query.query

    articles = list()

    results = find_message_record(query_string)
    if results == "Not found":
        articles.append(InlineQueryResultArticle(id=uuid4(),
                                                 title="Not Found",
                                                 input_message_content=InputTextMessageContent("Not Found")))
    else:
        for entry in results:
            result = entry["ori_username"] + ": " + entry["text"]
            articles.append(InlineQueryResultArticle(id=uuid4(),
                                                     title=result,
                                                     input_message_content=InputTextMessageContent(result)))
    update.inline_query.answer(articles)


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    config = open("./config.json")
    config = json.load(config)
    TOKEN = config["TOKEN"]
    MONGO_HOST = config["MONGO_HOST"]
    DBName = config["DBName"]

    updater = Updater(TOKEN)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(InlineQueryHandler(inlinequery))

    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
