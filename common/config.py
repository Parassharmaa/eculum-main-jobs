import os

#twitter
CONSUMER_KEY  = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
BASE_URL = os.environ['BASE_URL']
callback_url  = BASE_URL + "api/v1/callback/twitter"
SECRET_KEY = os.environ['SECRET_KEY']
PRIVATE_KEY = os.environ['PRIVATE_KEY']

#instagram
instaConfig = {
	'client_id':os.environ.get('CLIENT_ID'),
	'client_secret':os.environ.get('CLIENT_SECRET'),
	'redirect_uri' : os.environ.get('REDIRECT_URI')
}

# email server
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = os.environ.get('MAIL_UNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PSWD')

# administrator list
EMAIL_ADMINS = ['eculumai@gmail.com']

#cortex 
PREDICT_URL = os.environ['PREDICT_URL']