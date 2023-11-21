from pymongo import MongoClient

client = MongoClient("mongodb://%s:%s@localhost:27017" % ("zibal", "pass123Sec"))

db = client["zibal_db"]
