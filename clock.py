from common.conn_db import *
import jobs as jobs
import pymongo

coll = db['user']
data = coll.find()

proc_list = []

for i in data:
	proc_list.append(jobs.TwAnalyse(i))

for p in proc_list:
	p.start()
