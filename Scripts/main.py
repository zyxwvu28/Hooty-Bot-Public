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
import API_Calls as api
import praw as pr
from datetime import date as da
import logging as log

# Define global 'constants'
with open('data/version.txt') as f:
    version = f.readlines()[0]
APP_ID = os.environ.get('REDDIT_HOOTY_APP_ID')
user_agent = 'reddit:' + APP_ID + ':' + version + ' (by /u/zyxwvu28)'
today = str(da.today())
log_prefix = 'Logs/HootyBot_' + version + '_' + today
log_file_name = log_prefix + ".log"
csv_log_name = log_prefix + ".csv"
bot_status_post_id = 'svj2yd'
responseDF_path = 'ReplyDFs\HootyBotResponseDF.csv'
blacklist_words_path = 'ReplyDFs\BlacklistWords.csv'
last_comment_time_path = 'data/last_comment_time.txt'

# Configure logging
log.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s', 
                filename=log_file_name, 
                # encoding='utf-8', 
                level=log.DEBUG
                )

# Create missing directories
with open('Directories_needed.txt', 'r') as f:
    dirs_needed = []
    line = f.readline()[:-1]
    while line:
        dirs_needed.append(line)
        line = f.readline()
        if '\n' in line:
            line = line[:-1]
lst_dir = os.listdir()
for needed in dirs_needed:
    if not(needed in lst_dir):
        os.mkdir(needed)

# Define creator of bot
bot_creator = os.environ.get('REDDIT_BOT_CREATOR')
if bot_creator is None:
    bot_creator = '' # Change this string to be your main Reddit account username (without the u/)
    while bot_creator == '':
        bot_creator = input('Enter your Reddit username with the \'u/\':\n')
        print('Welcome u/' + bot_creator)
    

# Setting external urls
github_README_url = 'https://github.com/{}/Hooty-Bot-Public/blob/main/README.md'.format(bot_creator)
reply_suggestions_form = 'https://forms.gle/jJzJTGC36ykLhWxB6'
external_urls = {
    'github_README_url': github_README_url,
    'reply_suggestions_form': reply_suggestions_form
}

# Set bot's username
username = 'HootyBot'

# Set subreddit and reply mode
# sr = "TheOwlHouse"
# reply_mode = True

sr = 'TOH_Bot_Testing'
reply_mode = True

# Variables and data importamt for configuring HootyBot
bot_config = {
    'responseDF_path': responseDF_path,
    'blacklist_words_path': blacklist_words_path,
    'last_comment_time_path': last_comment_time_path,
    'version': version, 
    'bot_creator': bot_creator,
    'log_file_name': log_file_name,
    'csv_log_name': csv_log_name,
    'bot_status_post_id': bot_status_post_id,
    'skip_existing': reply_mode, 
    'replies_enabled': reply_mode,
    'pause_after': 2, 
    'min_between_replies': 30
}

### Call API
api.activate_bot(username, sr, bot_config = bot_config, external_urls = external_urls)
