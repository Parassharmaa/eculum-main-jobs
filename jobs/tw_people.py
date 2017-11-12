import tweepy
from datetime import datetime
import time
import pymongo
from bson import ObjectId
import multiprocessing
import firefly
from collections import Counter, OrderedDict

class Keywords():
    def __init__(self, user_data, username=False, count=500,):
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
        self.tw_count = count
        self.firefly_client = firefly.Client(PREDICT_URL, auth_token='cortexai')

        try:
            self.api = tweepy.API(self.auth)
            self.me = self.api.me()
            self.result_data = {"tweets":'', "hashtags":[]}
            self.start_time = time.time()
        except Exception as e:
            print(e)

    def get_tweet_words(self):
        for i in self.api.user_timeline(screen_name = self.screen_name, count=self.tw_count):
            self.result_data['tweets']+=i.text
            ht = dict_list_reduce(i.entities['hashtags'], 'text')
            if ht:
                self.result_data['hashtags'].extend(ht)

    def get_recent_words(self):
        self.get_tweet_words()
        w =Counter(self.firefly_client.keyword(payload=self.result_data['tweets']))
        return dict(w.most_common(20))


    def get_tags_count(self):
        es = 0
        self.htags = Counter(self.result_data['hashtags'])
        self.wtags = Counter(self.firefly_client.keyword(payload=self.result_data['tweets']))
        w = dict(self.htags.most_common(50))
        if len(w) < 20:
            es = 20
        w.update(dict(self.wtags.most_common(es)))
        return w



