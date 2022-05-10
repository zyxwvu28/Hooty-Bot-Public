'''
Main script controlling u/HootyBot
To install all necessary packages, 
(ensure that your working directory is setup to be the Hooty-Bot folder)
type the command below into your terminal:
py -m pip install -U -r requirements.txt
'''

import os
import API_Calls as api
import bot_config_editor as bce
from datetime import date as da
import logging as log
import json

def main():
    ## Create missing directories
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
            print(f'Created directory ../{needed}/') 
            
    ## File paths
    version_path = 'data/version.txt'
    responseDF_path = 'ReplyDFs\HootyBotResponseDF.csv'
    blacklist_words_path = 'ReplyDFs\BlacklistWords.csv'
    admin_codes_path = 'data/admin_codes.csv'
    opt_out_list_path = 'data/opt_out_list.csv'
    reply_stats_by_post_path = 'data/bot_reply_stats_by_post.csv'

    files_required = [version_path,
                    admin_codes_path,
                    opt_out_list_path,
                    blacklist_words_path,
                    responseDF_path,
                    reply_stats_by_post_path,
                    'Scripts\API_Calls.py',
                    'praw.ini',
                    ]

    ## Notify user about missing files
    for i in files_required:
        if not(os.path.exists(i)):
            print('WARNING! file ' + i + ' not found.')

    ## Read in the bot's version number
    with open(version_path) as f:
        version = f.readlines()[0] 
            
    ## Define global 'constants'
    today = str(da.today())
    log_prefix = 'Logs/HootyBot_' + version + '_' + today
    log_file_path = log_prefix + ".log"

    ## Configure logging
    root_logger= log.getLogger()
    root_logger.setLevel(log.DEBUG) 
    handler = log.FileHandler(log_file_path, 
                            'w', 
                            'utf-8'
                            ) 
    handler.setFormatter(log.Formatter('%(asctime)s [%(levelname)s]: %(message)s'))
    root_logger.addHandler(handler)

    ## Set the subreddit
    sr = "TheOwlHouse"
    sr = 'TOH_Bot_Testing'
    bce.change_subreddit(sr)

    ## Load bot_config.json
    with open('data/bot_config.json') as f:
        bot_config = json.load(f)

    ### Call API
    api.activate_bot(bot_config)
    
if __name__ == '__main__':
    main()
