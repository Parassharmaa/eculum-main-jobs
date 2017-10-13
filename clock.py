from common.config import *
import jobs as jobs
import pymongo
import os

client = pymongo.MongoClient(os.environ['DB_STRING'], connect=False)
db = client.get_database()

coll = db['user']
data = coll.find()

proc_list = []

for i in data:
	proc_list.append(jobs.TwAnalyse(i))

for p in proc_list:
	p.start()
