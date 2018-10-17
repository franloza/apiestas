import pymongo
import ..settings

class MongoDB:
    def __init__(self):
        uri = "mongodb://{user}:{password}@{host}:{port}/{db}?authSource={auth_source}".format(
            user=st.MONGODB_USER,
            password=st.MONGODB_PASSWORD,
            host=st.MONGODB_HOST,
            port=st.MONGODB_PORT,
            db=st.MONGODB_DB,
            auth_source=st.MONGODB_AUTHSOURCE
        )
        connection = pymongo.MongoClient(uri)
        self.db = connection[st.MONGODB_DB]
        self.collection = self.db[st.MONGODB_COLLECTION]