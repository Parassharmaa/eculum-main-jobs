import tweepy
from datetime import datetime
import time
from common.config import *
import pymongo
from bson import ObjectId
import multiprocessing
import firefly

class TwAnalyse(multiprocessing.Process):
    def __init__(self, user_data):
        multiprocessing.Process.__init__(self)
        self.r = 1
        self.id = user_data['_id']
        self.screen_name = user_data['twitter']['screen_name']
        self.access_token = user_data['twitter']['access_token']
        self.access_token_secret = user_data['twitter']['access_secret_token']
        self.old_followers_count = user_data['twitter']['followers_count']
        self.old_friends_count = user_data['twitter']['friends_count']
        self.auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        self.auth.set_access_token(self.access_token, self.access_token_secret)

        client = pymongo.MongoClient(connect=False)
        self.db = client.get_database("eculum")

        self.predict_client = firefly.Client(PREDICT_URL)

        print("{} | Starting Fetch | {}".format(datetime.strftime(datetime.utcnow(), "%Y-%m-%d %H:%M:%S"), 
                                            self.screen_name))
        try:
            self.api = tweepy.API(self.auth)
            self.me = self.api.me()
            self.analysed_data = {"followers":[], "friends":[]}
            self.start_time = time.time()
        except Exception as e:
            print(e)


    def get_new_followers(self):
        self.new_followers_count = (self.me.followers_count - self.old_followers_count)
        self.new_followers = list()
        if self.new_followers_count > 0:
            for page in tweepy.Cursor(self.api.followers).items(self.new_followers_count):
                self.new_followers.append(page)
        self.new_followers_count = self.old_followers_count + len(self.new_followers)

    def get_new_friends(self):
        self.new_friends_count = (self.me.friends_count - self.old_friends_count)
        self.new_friends = list()

        if self.new_friends_count > 0:
            for page in tweepy.Cursor(self.api.friends).items(self.new_friends_count):
                self.new_friends.append(page)
        self.new_friends_count = self.old_friends_count + len(self.new_friends)

    def analyse(self):
        followers_growth_rate = 100 * ((self.new_followers_count - self.old_followers_count) \
                                / self.old_followers_count)
        friends_growth_rate = 100 * ((self.new_friends_count - self.old_friends_count) \
                                / self.old_friends_count)

        for i in self.new_followers:
            i._json['interest'] = self.client.predict_interest(payload=i._json['description'])[i._json['description']]
            self.analysed_data['followers'].append(i._json)

        for i in self.new_friends: 
            i._json['interest'] =  self.client.predict_interest(payload=i._json['description'])[i._json['description']]
            self.analysed_data['friends'].append(i._json)

        self.analysed_data['followers_growth_rate'] = followers_growth_rate
        self.analysed_data['friends_growth_rate'] = friends_growth_rate


    def save_data(self):
        timestamp = datetime.strftime(datetime.utcnow(), "%Y-%m-%d")
        time_taken = round(time.time() - self.start_time, 2)
        coll = self.db['user']
        ts_key = 'tw_analytics.' + timestamp
        coll.update({'_id': self.id}, {'$set' : {ts_key: self.analysed_data}}, upsert=True)
        coll.update({'_id': self.id}, {'$set' : {'twitter.followers': self.new_followers_count, \
                                                'twitter.friends': self.new_friends_count }})
        print("{} | Saving Data | {}".format(datetime.strftime(datetime.utcnow(), "%Y-%m-%d %H:%M:%S"), 
                                                self.screen_name))
        print("{} | Time Taken | {}".format(datetime.strftime(datetime.utcnow(), "%Y-%m-%d %H:%M:%S"), 
                                                time_taken))


    def run(self):
        #testing
        while self.r:
            try:
                self.get_new_followers()
                self.get_new_friends()
                self.analyse()
                self.save_data()
                self.r = 0
            except Exception as e:
                self.save_data()
                print(e)
                print("Waiting for 15 min")
                time.sleep(900)
        # under construction
