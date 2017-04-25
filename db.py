from pymongo import MongoClient
import logging
import os

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
LOG = logging.getLogger(__name__)


class Config:
    def __init__(self):
        self.TOKEN = os.getenv("TOKEN", None)
        self.CHANNEL_URL = os.getenv("CHANNEL_URL", None)
        self.MONGO_URI = os.getenv("MONGO_URI", None)
        self.DB_NAME = os.getenv("DB_NAME", None)
        self.ES_URL = os.getenv("ES_URL", None)

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


def query_yulu_by_text(text):
    uri = config.MONGO_URI
    conn = MongoClient(uri)
    database = conn[config.DB_NAME]
    collection = database.entries
    yulus = collection.find({"text": text})
    result = []
    if yulus.count() > 0:
        for yulu in yulus:
            LOG.info(yulu)
            result.append(yulu["url"])

    return result


def query_yulu_by_keyword(text):
    from elasticsearch import Elasticsearch
    es = Elasticsearch(config.ES_URL)
    body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match_phrase": {
                            "text": text
                        }
                    }
                ]
            }
        }
    }

    res = es.search(index=config.DB_NAME, doc_type="entries", body=body)
    LOG.info(res)
    return res


def query_yulu_by_username(username):
    uri = config.MONGO_URI
    conn = MongoClient(uri)
    database = conn[config.DB_NAME]
    collection = database.entries
    yulus = collection.find({"ori_user_username": username})
    count = yulus.count()
    result = []
    if count > 0:
        for yulu in yulus:
            LOG.info(yulu)
            result.append(yulu["url"])
    elif count == 0:
        pass
    return count, result


def query_similar_username(username):

    pass