#! /usr/bin/python2.7
# -*- coding:utf-8 -*

import tweepy
from tweepy import OAuthHandler
import json
 
consumer_key = '2sMf8cVSQ7E23SaY9nROPRgAq'
consumer_secret = 'W7wwom2Nh7EdguMBLRQo9F1hEeRGobhFeM6bObixtDGNNhRtfa'
access_token = '722474282681556992-7XsPh7g9bOroOQNbcu6LzrQ3O6434Ti'
access_secret = '00KKLiK1yi9rHYfhdqWKdJBLr3yyVrWUSrN8OgRMz1AT4'
 
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth)
