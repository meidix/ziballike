from pymongo import MongoClient

client = MongoClient("db", 27017)

db = client["zibal_db"]
