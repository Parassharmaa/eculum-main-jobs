import tweepy
from datetime import datetime
import time
import pymongo
from bson import ObjectId
from collections import Counter, OrderedDict
from jobs.tw_base import UserAuth
from common.util import dict_list_reduce

class Keywords(UserAuth):
    def __init__(self, user_data, username=False, count=500):
        super().__init__(user_data)
        self.tw_count = count
        self.result_data = {"tweets":'', "hashtags":[]}
        self.load_words()

    def load_words(self):
        for i in self.api.user_timeline(screen_name = self.screen_name, count=self.tw_count):
            self.result_data['tweets']+=i.text
            ht = dict_list_reduce(i.entities['hashtags'], 'text')
            if ht:
                self.result_data['hashtags'].extend(ht)

    def get_recent_words(self):
        w = Counter(self.firefly_client.keyword(payload=self.result_data['tweets']))
        return dict(w.most_common(20))


    def get_tag_words(self):
        es = 0
        self.htags = Counter(self.result_data['hashtags'])
        self.wtags = Counter(self.firefly_client.keyword(payload=self.result_data['tweets']))
        w = dict(self.htags.most_common(50))
        if len(w) < 20:
            es = 20
        w.update(dict(self.wtags.most_common(es)))
        return w


