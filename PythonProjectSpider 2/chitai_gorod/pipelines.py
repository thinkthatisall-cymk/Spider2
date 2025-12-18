import os

import pymongo
from itemadapter import ItemAdapter


class MongoBooksPipeline:
    def __init__(self, mongo_uri, mongo_db, mongo_collection):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection
        self.client = None
        self.collection = None

    @classmethod
    def from_crawler(cls, crawler):
        mongo_user = os.getenv("MONGO_USER", "books_user")
        mongo_password = os.getenv("MONGO_PASSWORD", "books_pass")
        mongo_host = os.getenv("MONGO_HOST", "localhost")
        mongo_port = os.getenv("MONGO_PORT", "27017")
        mongo_db = os.getenv("MONGO_DATABASE", "items")
        mongo_collection = os.getenv("MONGO_DATABASE_COLLECTION", "scraped_books")

        mongo_uri = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/"
        return cls(mongo_uri, mongo_db, mongo_collection)

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        db = self.client[self.mongo_db]
        self.collection = db[self.mongo_collection]

    def close_spider(self, spider):
        if self.client:
            self.client.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        data = dict(adapter)

        isbn = data.get("isbn")
        if not isbn:
            return item

        self.collection.update_one(
            {"isbn": isbn},
            {"$set": data},
            upsert=True,
        )
        return item
