from pymongo import MongoClient
from .celery import app as celery_app

client = MongoClient("mongodb://%s:%s@localhost:27017" % ("zibal", "pass123Sec"))

db = client["zibal_db"]

__all__ = ('celery_app', )
