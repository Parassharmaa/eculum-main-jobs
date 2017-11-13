import tweepy
from datetime import datetime
import time
import pymongo
from bson import ObjectId
from collections import Counter, OrderedDict
from jobs.tw_base import UserAuth
from jobs.tw_words import Keywords
from newspaper import Article

class SuggestedArticles(Keywords, UserAuth):
	def __init__(self, user_data):
		Keywords.__init__(self, user_data, count=50)
		UserAuth.__init__(self, user_data)
		self.words = self.get_recent_words()
		self.words = sorted(self.words.items(), key=lambda value: value[1], reverse=True)[:10]
		self.articles = []
		self.coll = self.db['articles']

	def curate_articles(self):
		for i in self.words:
			for t in self.api.search(q=i[0], rpp=10, lang='en'):
				t = t._json
				if t['entities'].get('urls'):
					try:
						url = t['entities']['urls'][0]['expanded_url']
						a = Article(url)
						a.download()
						a.parse()
						if a.has_top_img() and a.meta_lang == 'en':
							a.nlp()
							temp_data = {
								"url": a.canonical_link,
								"title": a.title,
								"image": a.top_img,
								"description": a.meta_description,
								"keywords": a.keywords,
								"summary": a.summary
							}
							k = self.coll.insert_one(temp_data)
							self.articles.append(temp_data)
					except: 
						pass
	def save_articles(self):
		self.coll.update({'uid': self.id}, {'$set': {'articles': self.articles}}, upsert=True)

