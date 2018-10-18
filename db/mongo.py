import pymongo
from . import settings as st

class MongoDB:
    def __init__(self, collection):
        connection = pymongo.MongoClient(
            st.MONGODB_HOST,
            st.MONGODB_PORT
        )
        self.db = connection[st.MONGODB_DB]
        self.collection = self.db[collection]