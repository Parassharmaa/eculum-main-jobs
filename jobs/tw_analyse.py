import tweepy
from datetime import datetime
import time
from common.config import *
import pymongo
from bson import ObjectId
import multiprocessing
import firefly
from jobs.tw_base import UserAuth

class TwAnalyse(multiprocessing.Process, UserAuth):
    def __init__(self, user_data):
        multiprocessing.Process.__init__(self)
        UserAuth.__init__(self, user_data)
        self.old_followers_count = user_data['twitter']['followers_count']
        self.old_friends_count = user_data['twitter']['friends_count']

        print("{} | Starting Fetch | {}".format(datetime.strftime(datetime.utcnow(), "%Y-%m-%d %H:%M:%S"), 
                                            self.screen_name))
        self.analysed_data = {"followers":[], "friends":[], 
                            "followers_growth_rate": 0, 
                            "friends_growth_rate": 0, 
                            'followers_count': 0,
                            'friends_count': 0}

    def get_new_followers(self):
        self.new_followers_count = (self.me.followers_count - self.old_followers_count)
        self.new_followers = list()
        if self.new_followers_count > 0:
            for page in tweepy.Cursor(self.api.followers).items(self.new_followers_count):
                self.new_followers.append(page)
        self.new_followers_count = self.me.followers_count

    def get_new_friends(self):
        self.new_friends_count = (self.me.friends_count - self.old_friends_count)
        self.new_friends = list()

        if self.new_friends_count > 0:
            for page in tweepy.Cursor(self.api.friends).items(self.new_friends_count):
                self.new_friends.append(page)
        self.new_friends_count = self.me.friends_count

    def analyse(self):
        followers_growth_rate = 100 * ((self.new_followers_count - self.old_followers_count) \
                                / self.old_followers_count)
        friends_growth_rate = 100 * ((self.new_friends_count - self.old_friends_count) \
                                / self.old_friends_count)

        for i in self.new_followers:
            st = ''
            if i._json['statuses_count'] and i._json.get('status'):
                st = i._json['status']['text']
            payload = i._json['description'] + st
            i._json['interest'] = self.firefly_client.predict(payload=[payload])[payload]
            self.analysed_data['followers'].append(i._json)

        for i in self.new_friends: 
            st = ''
            if i._json['statuses_count'] and i._json.get('status'):
                st = i._json['status']['text']
            payload = i._json['description'] + st
            i._json['interest'] =  self.firefly_client.predict(payload=[payload])[payload]
            self.analysed_data['friends'].append(i._json)

        self.analysed_data['followers_growth_rate'] = followers_growth_rate
        self.analysed_data['friends_growth_rate'] = friends_growth_rate
        self.analysed_data['followers_count'] = self.new_followers_count
        self.analysed_data['friends_count'] = self.new_friends_count


    def save_data(self):
        timestamp = datetime.strftime(datetime.utcnow(), "%Y-%m-%d")
        time_taken = round(time.time() - self.start_time, 2)
        coll = self.db['twitter_analytics']

        coll.insert({'uid': self.id, 'timestamp': timestamp, 'data': self.analysed_data})

        d = coll.update({'_id': self.id}, {'$set' : {'twitter.followers_count': self.new_followers_count, \
                                                'twitter.friends_count': self.new_friends_count }})
        print("{} | Saving Data | {}".format(datetime.strftime(datetime.utcnow(), "%Y-%m-%d %H:%M:%S"), 
                                                self.screen_name))
        print("{} | Time Taken | {}".format(datetime.strftime(datetime.utcnow(), "%Y-%m-%d %H:%M:%S"), 
                                                time_taken))


    def run(self):
        try:
            self.get_new_followers()
            self.get_new_friends()
            self.analyse()
            # self.save_data()
        except Exception as e:
            print("Error:", e)
            print("Error ocurred: ", self.screen_name)
