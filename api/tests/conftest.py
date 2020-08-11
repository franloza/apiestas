import os

import pytest
from pymongo import MongoClient
from starlette.testclient import TestClient


@pytest.fixture
def client():
    os.environ['MONGO_DB'] = 'test'
    from api.app.asgi import app
    with TestClient(app) as c:
        yield c


@pytest.yield_fixture(scope='function')
def collection():
    from api.app.core.config import COLLECTION_NAME
    mongo = MongoClient(os.environ['DB_CONNECTION'])['test']
    col = mongo[COLLECTION_NAME]
    col.drop()
    yield col
    col.drop()
