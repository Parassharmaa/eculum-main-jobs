import tweepy
from datetime import datetime
import time
import pymongo
from bson import ObjectId
from collections import Counter, OrderedDict
from jobs.tw_base import UserAuth
from jobs.tw_words import Keywords
from newspaper import Article
import multiprocessing

class SuggestedArticles(multiprocessing.Process, Keywords, UserAuth):
	def __init__(self, user_data):
		multiprocessing.Process.__init__(self)
		Keywords.__init__(self, user_data, count=50)
		UserAuth.__init__(self, user_data)
		self.words = self.get_tag_words(count=20)
		self.words = sorted(self.words.items(), key=lambda value: value[1], reverse=True)[:10]
		self.articles = []
		self.coll = self.db['articles']

	def is_article_url(self, url):
		not_allowed = ['https://twitter.com', 'https://facebook.com', 'https://instagram.com']
		if len(url.split('/')) < 4:
			return False
		for n in not_allowed:
			if len(url.split('/')) > 3 and n.split('/')[2] == url.split('/')[2]:
				return False
		return True

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
						if a.has_top_image() and a.meta_lang == 'en' and self.is_article_url(a.canonical_link):
							a.nlp()
							temp_data = {
								"url": a.canonical_link,
								"title": a.title,
								"image": a.top_img,
								"description": a.meta_description,
								"keywords": a.keywords,
								"summary": a.summary
							}
							print("{} | Saving | {}".format(self.screen_name, a.title))
							k = self.coll.insert_one(temp_data)
							self.articles.append(temp_data)
					except Exception as e: 
						print(e)
						print("Continue...")
	def save_articles(self):
		self.coll = self.db['users_articles']
		self.coll.update({'uid': self.id}, {'$set': {'articles': self.articles}}, upsert=True)
		print(print("{} | Halting | All data saved".format(self.screen_name)))
	def run(self):
		try:
		    self.curate_articles()
		    self.save_articles()
		except Exception as e:
		    print("Error:", e)
		    print("Error ocurred: ", self.screen_name)
