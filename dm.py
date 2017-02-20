import telepot
import json
from pymongo import MongoClient
from telepot.helper import InlineUserHandler, AnswererMixin
from telepot.delegate import per_chat_id, per_inline_from_id, create_open, pave_event_space


MONGO_HOST = ''
DBName = ''


class ChatHandler(telepot.helper.ChatHandler):
    global MONGO_HOST
    global DBName

    def __init__(self, *args, **kwargs):
        super(ChatHandler, self).__init__(*args, **kwargs)

    def insert_message_to_database(self, entry):
        uri = MONGO_HOST
        conn = MongoClient(uri)
        database = conn[DBName]
        collection = database.entries
        collection.insert(entry)
        conn.close()

    def format_message(self, msg):
        if "forward_date" in msg:
            _chat = msg["chat"]  # 当前与bot聊天的用户
            _date = msg["date"]  # Unix时间戳
            _forward_from = msg["forward_from"]  # FWD的消息最初来源用户
            _text = msg["text"]  # 文字
            _message_id = msg["message_id"]

            entry = {}
            entry["fwd_username"] = _chat["username"]
            entry["fwd_id"] = _chat["id"]
            entry["date"] = _date
            entry["ori_username"] = _forward_from["username"]
            entry["ori_id"] = _forward_from["id"]
            entry["text"] = _text
            entry["message_id"] = _message_id

            self.insert_message_to_database(entry)
        else:
            self.sender.sendMessage("Please forward message to me!")

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type != "text":
            self.close()
        else:
            self.format_message(msg)


if __name__ == "__main__":
    config = open("./config.json")
    config = json.load(config)
    TOKEN = config["TOKEN"]
    MONGO_HOST = config["MONGO_HOST"]
    DBName = config["DBName"]

    bot = telepot.DelegatorBot(TOKEN, [
        pave_event_space()(
            per_chat_id(), create_open, ChatHandler, timeout=10),
    ])
    bot.message_loop(run_forever='Listening ...')
