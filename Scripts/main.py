'''
Main script controlling u/HootyBot
To install all necessary packages, 
(ensure that your working directory is setup to be the Hooty-Bot folder)
type the command below into your terminal:
py -m pip install -U -r requirements.txt
'''

import os
import requests as r
import time as t
import API_Calls_v3 as api
import praw as pr

# Define global 'constants'
version = api.version # Version number is set in API_Calls module
APP_ID = os.environ.get('REDDIT_HOOTY_APP_ID')
user_agent = 'reddit:' + APP_ID + ':' + version + ' (by /u/zyxwvu28)'

# Load credentials from praw.ini to generate a Reddit instance
username = 'HootyBot'
reddit = pr.Reddit(username)

### API Calls

# 1. Monitor new posts
sr = "TheOwlHouse"
reply_mode = True

# sr = 'TOH_Bot_Testing'
# reply_mode = True

api.monitor_new_posts(reddit, sr, skip_existing = reply_mode, pause_after = 2, replies_enabled = reply_mode)
