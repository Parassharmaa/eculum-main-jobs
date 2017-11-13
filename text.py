import jobs
import os
import pymongo
client = pymongo.MongoClient(os.environ['DB_STRING'], connect=False)
db = client.get_database()
coll = db['user']
uo = coll.find_one({})
sa = jobs.SuggestedArticles(uo)
sa.curate_articles()
sa.save_articles()