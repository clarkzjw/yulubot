#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from datetime import timezone

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from models.db import ACTION_BOT_QUERY_BY_KEYWORD, ACTION_BOT_QUERY_BY_PEOPLE
from models.db import ACTION_BOT_START_BY_USER
from models.db import Quote, config, sqlalchemy_session
from utils import get_tg_user_from_update, add_action, check_blacklist
from utils import query_yulu_by_keyword, query_yulu_by_username, insert_quote

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
LOG = logging.getLogger(__name__)


first_use_text = u"""
坚持一个高层的原则绝不动摇！

现有如下功能：

💫 关键字搜索：
/search keyword 
如：/search 你好，得到一条语录“你好变态啊！”；

💫按被forward人搜索：
/list username（不带@）
如：/list MayGreen, 得到100多条语录；

现不支持inline（后续可能支持）, 为了不让消息爆炸（可能搜到100条消息），暂不建议添加至群组中。
"""


def start(bot, update):
    LOG.info("start")
    user = get_tg_user_from_update(update)
    add_action(user, ACTION_BOT_START_BY_USER)
    target_id = update["message"]["from_user"]["id"]
    if check_blacklist(user[0]):
        bot.sendMessage(target_id, u"You have been banned")
        return
    update.message.reply_text(first_use_text)


def forward_message(bot, update, chat_id, from_chat_id, disable_notification, message_id):
    LOG.info("forward_message")
    bot.forwardMessage(chat_id=chat_id,
                       from_chat_id=from_chat_id,
                       disable_notification=disable_notification,
                       message_id=message_id)


def search_by_keyword(bot, update):
    LOG.info("search_by_keyword")
    user = get_tg_user_from_update(update)

    is_bot_cmd = update["message"]["entities"][0]["type"]
    target_id = update["message"]["from_user"]["id"]
    message_type = update["message"]["chat"]["type"]
    if check_blacklist(user[0]):
        bot.sendMessage(target_id, u"You have been banned")
        add_action(user, ACTION_BOT_QUERY_BY_KEYWORD, comments="banned")
        return

    if is_bot_cmd == "bot_command":
        text = ""
        offset = update["message"]["entities"][0]["length"] + 1
        if message_type == "private":
            text = update["message"]["text"][offset:]
        elif message_type == "group":
            text = update["message"]["text"][offset:]
            target_id = update["message"]["chat"]["id"]
        if text == "":
            update.message.reply_text(u"请输入关键词")
            return
        results = query_yulu_by_keyword(text)
        add_action(user, ACTION_BOT_QUERY_BY_KEYWORD, comments=text)
        total = len(results)
        count = 0
        deleted_quote = []
        if total > 0:
            update.message.reply_text(u"共有 %s 条语录，分别是" % total)
            for result in results:
                url = str(result.ori_url)
                try:
                    if "ingayressHZ" in url:
                        forward_message(bot, update, target_id, "@ingayressHZ", False, url[25:])
                    elif "ingayssHZ" in url:
                        forward_message(bot, update, target_id, "@ingayssHZ", False, url[23:])
                    count += 1
                except Exception as e:
                    deleted_quote.append(u"{}: {}".format(result.ori_user_nickname, result.text))
            if count < total:
                update.message.reply_text(u"有 {} 条语录被删了！".format(total - count))
                for msg in deleted_quote:
                    update.message.reply_text(msg)
        elif total == 0:
            update.message.reply_text(u"找不到对应的语录")


def search_by_people(bot, update):
    LOG.info("search_by_people")
    user = get_tg_user_from_update(update)

    is_bot_cmd = update["message"]["entities"][0]["type"]
    target_id = update["message"]["from_user"]["id"]
    message_type = update["message"]["chat"]["type"]
    if check_blacklist(user[0]):
        bot.sendMessage(target_id, u"You have been banned")
        add_action(user, ACTION_BOT_QUERY_BY_PEOPLE, comments="banned")
        return

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

        count, yulus = query_yulu_by_username(username)
        add_action(user, ACTION_BOT_QUERY_BY_PEOPLE, comments=username)
        if count > 0:
            bot.sendMessage(target_id, u"%s 有 %s 条语录，如下：" % (username, count))
            bot.sendMessage(target_id, yulus)
        elif count == 0:
            bot.sendMessage(target_id, u"用户名%s 不存在！" % username)


def echo(bot, update):
    LOG.info("echo")

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
            original_user = None
            if forward_from:
                original_user = channel_post["forward_from"]
                # 原始用户
                original_user_id = original_user["id"]
                original_user_username = original_user["username"]
                original_user_nickname = " ".join(x for x in [original_user["first_name"],
                                                              original_user["last_name"]] if x is not None)
            elif forward_from_chat:
                original_user = channel_post["forward_from_chat"]
                # 原始用户
                original_user_id = original_user["id"]
                original_user_username = original_user["username"]
                original_user_nickname = original_user["title"]

            url = config.CHANNEL_URL + str(message_id)
            with sqlalchemy_session() as session:
                quote = session.query(Quote).filter(
                    Quote.ori_user_id == original_user_id,
                    Quote.text == text
                ).first()
                if not quote:
                    quote = Quote(id=update_id,
                                  fwd_date=forward_date.replace(tzinfo=timezone.utc).timestamp(),
                                  text=text,
                                  ori_user_id=original_user_id,
                                  ori_user_username=original_user_username,
                                  ori_user_nickname=original_user_nickname,
                                  ori_url=url)
                    insert_quote(quote)


def error(bot, update, error):
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
