import pymongo
from scrapy.conf import settings


class MongoDB:
    def __init__(self):
        uri = "mongodb://{user}:{password}@{host}:{port}/{db}?authSource={auth_source}".format(
            user=settings['MONGODB_USER'],
            password=settings['MONGODB_PASSWORD'],
            host=settings['MONGODB_HOST'],
            port=settings['MONGODB_PORT'],
            db=settings['MONGODB_DB'],
            auth_source=settings['MONGODB_AUTHSOURCE']
        )
        connection = pymongo.MongoClient(uri)
        self.db = connection[settings['MONGODB_DB']]
        self.collection = self.db[settings['MONGODB_COLLECTION']]