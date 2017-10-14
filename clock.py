from common.config import *
import jobs as jobs
import pymongo
from datetime import datetime
import os
from apscheduler.schedulers.blocking import BlockingScheduler

print('[{}] Starting Scheduler'.format(datetime.strftime(datetime.utcnow(), "%Y-%m-%d %H:%M:%S")))
client = pymongo.MongoClient(os.environ['DB_STRING'], connect=False)
db = client.get_database()
sched = BlockingScheduler()

@sched.scheduled_job('cron', day_of_week='mon-sun', hour=0)
def job():
	print('[{}] Running Job'.format(datetime.strftime(datetime.utcnow(), "%Y-%m-%d %H:%M:%S")))

	coll = db['user']
	data = coll.find()

	proc_list = []

	for i in data:
		proc_list.append(jobs.TwAnalyse(i))

	for p in proc_list:
		p.start()
	print('[{}] Job Finished'.format(datetime.strftime(datetime.utcnow(), "%Y-%m-%d %H:%M:%S")))

sched.start()
