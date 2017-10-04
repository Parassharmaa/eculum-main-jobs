import pymongo

client = pymongo.MongoClient()
db = client.get_database("eculum")
