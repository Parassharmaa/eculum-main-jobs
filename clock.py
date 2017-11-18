from common.config import *
import jobs as jobs
import pymongo
from datetime import datetime
import os
from apscheduler.schedulers.blocking import BlockingScheduler

import multiprocessing
import multiprocessing.pool

class NoDaemonProcess(multiprocessing.Process):
	def _get_daemon(self):
		return False
	def _set_daemon(self, value):
		pass
	daemon = property(_get_daemon, _set_daemon)

class NoDaemonProcessPool(multiprocessing.pool.Pool):
	Process = NoDaemonProcess

print('[{}] Starting Scheduler'.format(datetime.strftime(datetime.utcnow(), "%Y-%m-%d %H:%M:%S")))
client = pymongo.MongoClient(os.environ['DB_STRING'], connect=False)
db = client.get_database()
sched = BlockingScheduler()

def proc_analytics(user_data):
		obj = jobs.TwAnalyse(user_data)
		obj.start()

@sched.scheduled_job('cron', day_of_week='mon-sun', hour=0)
def job_analytics():
	print('[{}] Running Job'.format(datetime.strftime(datetime.utcnow(), "%Y-%m-%d %H:%M:%S")))

	coll = db['user']
	data = coll.find()
	user_list = [u for u in data]

	pool = NoDaemonProcessPool(processes=os.cpu_count())
	pool.map(proc_analytics, user_list)
	pool.close()
	pool.join()
	print('[{}] Job Finished'.format(datetime.strftime(datetime.utcnow(), "%Y-%m-%d %H:%M:%S")))

def proc_articles(user_data):
	obj = jobs.SuggestedArticles(user_data)
	obj.start()

@sched.scheduled_job('interval', hours=1)
def job_articles():
	print('[{}] Running Job'.format(datetime.strftime(datetime.utcnow(), "%Y-%m-%d %H:%M:%S")))	
	coll = db['user']
	data = coll.find()
	user_list = [u for u in data]

	pool = NoDaemonProcessPool(processes=os.cpu_count())
	pool.map(proc_articles, user_list)
	pool.close()
	pool.join()
	print('[{}] Job Finished'.format(datetime.strftime(datetime.utcnow(), "%Y-%m-%d %H:%M:%S")))


sched.start()
