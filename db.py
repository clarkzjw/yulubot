from pymongo import MongoClient
import logging
import json

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
LOG = logging.getLogger(__name__)


class Config:
    def __init__(self):
        c = open("./config.json")
        c = json.load(c)
        self.TOKEN = c["TOKEN"]
        self.CHANNEL_URL = c["CHANNEL_URL"]
        self.MONGO_URI = c["MONGO_URI"]
        self.DB_NAME = c["DB_NAME"]

config = Config()


class Quote:
    def __init__(self, id, fwd_date, text, ori_user_id, ori_user_username, ori_user_nickname, url):
        self.id = id
        self.fwd_date = fwd_date
        self.text = text
        self.ori_user_id = ori_user_id
        self.ori_user_username = ori_user_username
        self.ori_user_nickname = ori_user_nickname
        self.url = url

    def display(self):
        LOG.info(self.fwd_date)
        LOG.info(self.id)
        LOG.info(self.text)
        LOG.info(self.ori_user_id)
        LOG.info(self.ori_user_username)
        LOG.info(self.ori_user_nickname)
        LOG.info(self.url)

    def insert(self):
        uri = config.MONGO_URI
        conn = MongoClient(uri)
        database = conn[config.DB_NAME]
        collection = database.entries
        count = collection.find({"text": self.text, "ori_user_id": self.ori_user_id}).count()
        if count > 0:
            LOG.info("record exists")
            return

        post = {"id": self.id,
                "fwd_date": self.fwd_date,
                "text": self.text,
                "ori_user_id": self.ori_user_id,
                "ori_user_username": self.ori_user_username,
                "ori_user_nickname": self.ori_user_nickname,
                "url": self.url}
        collection.insert(post)
        conn.close()
