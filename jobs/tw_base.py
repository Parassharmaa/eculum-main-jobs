import tweepy
from datetime import datetime
import time
import pymongo
from bson import ObjectId
import multiprocessing
import firefly
from common.config import *
from collections import Counter, OrderedDict

class UserAuth():
    def __init__(self, user_data, username=False, count=500):
        self.id = user_data['_id']
        self.screen_name = user_data['twitter']['screen_name']
        if username:
            self.screen_name = username
        self.access_token = user_data['twitter']['access_token']
        self.access_token_secret = user_data['twitter']['access_secret_token']
        self.auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        self.auth.set_access_token(self.access_token, self.access_token_secret)
        client = pymongo.MongoClient(os.environ['DB_STRING'], connect=False)
        self.db = client.get_database()
        self.firefly_client = firefly.Client(PREDICT_URL, auth_token='cortexai')

        try:
            self.api = tweepy.API(self.auth)
            self.me = self.api.me()
            self.start_time = time.time()
        except Exception as e:
            print(e)