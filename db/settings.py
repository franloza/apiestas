import os

MONGODB_HOST = os.getenv('MONGO_HOST')
MONGODB_PORT = int(os.getenv('MONGO_PORT'))
MONGODB_DB = os.getenv('MONGO_DB')
MONGO_ODDS_COLLECTION = "odds"