import tweepy
from datetime import datetime
import time
from common.config import *
from common.conn_db import *
from bson import ObjectId
import multiprocessing

class TwAnalyse(multiprocessing.Process):
    def __init__(self, user_data):
        multiprocessing.Process.__init__(self)
        self.r = 1
        self.id = user_data['_id']
        self.access_token = user_data['twitter']['access_token']
        self.access_token_secret = user_data['twitter']['access_secret_token']
        self.old_followers_count = user_data['twitter']['followers_count']
        self.old_friends_count = user_data['twitter']['friends_count']
        self.auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        self.auth.set_access_token(self.access_token, self.access_token_secret)
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
        follower_growth_rate = 100 * ((self.new_followers_count - self.old_followers_count) / self.old_followers_count)
        friends_growth_rate = 100 * ((self.new_friends_count - self.old_friends_count) / self.old_friends_count)
        timeline = self.api.user_timeline()
        print(timeline[0]._json)
        # for i in self.new_followers:
        #     # get info about ids and analyse the bio
        #     # append into temp_data
        #     # under construction
        #     i['category'] = ""
        #     self.analysed_data['followers'].append(i)

        # for i in self.new_friends: 
        #     i['category'] = ""
            # self.analysed_data['friends'].append(i)
        print(follower_growth_rate, friends_growth_rate)

    def save_data(self):
        time_taken = round(time.time() - self.start_time, 2)
        timestamp = datetime.strftime(datetime.utcnow(), "%Y-%m-%d %H:%M:%S")
        print("Saving Data...")

    def run(self):
        #testing
        while self.r is not 0:
            try:
                print(self.me.screen_name)
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

