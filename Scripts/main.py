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

files_required = ['data/version.txt',
                  'data/admin_codes.csv',
                  'ReplyDFs\BlacklistWords.csv',
                  'ReplyDFs\HootyBotResponseDF.csv',
                  'Scripts\API_Calls.py',
                  'praw.ini',
                  ]

# Notify user about missing files
for i in files_required:
    if not(os.path.exists(i)):
        print('WARNING! file ' + i + ' not found.')

# Read in the bot's version number
with open('data/version.txt') as f:
    version = f.readlines()[0] 
    
# Define creator of bot
bot_creator = os.environ.get('REDDIT_BOT_CREATOR')
if bot_creator is None:
    bot_creator = '' # Change this string to be your main Reddit account username (without the u/)
    while bot_creator == '':
        bot_creator = input('Enter your Reddit username with the \'u/\':\n')
        print('Welcome u/' + bot_creator)
        
# Define global 'constants'
APP_ID = os.environ.get('REDDIT_HOOTY_APP_ID')
user_agent = 'reddit:' + APP_ID + ':' + version + ' (by /u/{})'.format(bot_creator)
today = str(da.today())
log_prefix = 'Logs/HootyBot_' + version + '_' + today
log_file_name = log_prefix + ".log"
csv_log_name = log_prefix + ".csv"
bot_status_post_id = 'svj2yd'
responseDF_path = 'ReplyDFs\HootyBotResponseDF.csv'
blacklist_words_path = 'ReplyDFs\BlacklistWords.csv'
last_comment_time_path = 'data/last_comment_time.txt'
admin_codes_path = 'data/admin_codes.csv'
admin_code_users_path = 'data/admin_code_users.txt'

# # Configure logging
root_logger= log.getLogger()
root_logger.setLevel(log.DEBUG) 
handler = log.FileHandler(log_file_name, 
                          'w', 
                          'utf-8'
                          ) 
handler.setFormatter(log.Formatter('%(asctime)s [%(levelname)s]: %(message)s'))
root_logger.addHandler(handler)

# Setting external urls
github_README_url = 'https://github.com/{}/Hooty-Bot-Public/blob/main/README.md'.format(bot_creator)
reply_suggestions_form = 'https://forms.gle/jJzJTGC36ykLhWxB6'
external_urls = {
    'github_README_url': github_README_url,
    'reply_suggestions_form': reply_suggestions_form
}

# Template reply ending for a bot
reply_ending = '\n\n^(I am a bot written by [{i}](https://www.reddit.com/user/{i}) | Check out my [Github]({github_README_url}) ) \n\n'.format(i = bot_creator, github_README_url = github_README_url) 
reply_ending += '^(Help improve Hooty\'s [vocabulary]({reply_suggestions_form}) | Current version: {v} )'.format(v = version, reply_suggestions_form = reply_suggestions_form)

# Set bot's username
username = 'HootyBot'

# Set subreddit and reply mode
sr = "TheOwlHouse"
reply_mode = True

# sr = 'TOH_Bot_Testing'
# reply_mode = True

# Variables and data importamt for configuring HootyBot
bot_config = {
    'username': username,                               # str: the bots username
    'sr': sr,                                           # str: the subreddit being monitored
    'responseDF_path': responseDF_path,                 # str: the directory path of responseDF
    'blacklist_words_path': blacklist_words_path,       # str: the directory path of blacklist_words
    'last_comment_time_path': last_comment_time_path,   # str: the directory path of last_comment_time
    'admin_codes_path': admin_codes_path,               # str: the directory path of admin codes
    'version': version,                                 # str: the version of the bot
    'bot_creator': bot_creator,                         # str: the username of the bot creator
    'log_file_name': log_file_name,                     # str: name of log file
    'csv_log_name': csv_log_name,                       # str: name of csv log file
    'bot_status_post_id': bot_status_post_id,           # str: Reddit id of the bot status post
    'skip_existing': reply_mode,                        # bool: if true, tells the bot to skip the 100 most recent msgs 
    'replies_enabled': reply_mode,                      # bool: if true, allows the bot to reply to msgs
    'pause_after': 2,                                   # int: How many failed API calls to make before pausing
    'min_between_replies': 30,                          # int: Min minutes between replies
    'reply_ending': reply_ending                        # str: Template ending that HootyBot appends to the end of all replies
}

### Call API
api.activate_bot(bot_config = bot_config, external_urls = external_urls)
