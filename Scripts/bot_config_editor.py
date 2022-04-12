'''
This script creates the bot_config.json file
'''

import os
import json
from datetime import date as da

def set_everything():
    raise NotImplementedError
    
def change_subreddit(subreddit):
    '''
    Changes the subreddit that the bot monitors

    Args:
        subreddit (str): The subreddit that you want the bot to monitor
    '''
    
    bot_config_file = 'data/bot_config.json'
    with open(bot_config_file, 'r') as f:
        bot_config = json.load(f)
        bot_config['metadata']['sr'] = subreddit
        
    with open(bot_config_file, 'w') as f:
        json.dump(bot_config, f)
        print(f'Target subreddit set to r/{subreddit}')
        print('bot_config.json saved.')
        
    return

def old_config():
    '''
    The old way I defined the bot_config dict
    '''

    # Set bot's username
    bot_username = os.environ.get('REDDIT_BOT_USERNAME')
    if bot_username is None:
        bot_username = '' # Change this string to be your main Reddit account username (without the u/)
        while bot_username == '':
            bot_username = input('Enter your bot\'s username without the \'u/\':\n')
    # print('Setting up control for u/' + bot_username)
    
    # Define creator of bot
    bot_creator = os.environ.get('REDDIT_BOT_CREATOR')
    if bot_creator is None:
        bot_creator = '' # Change this string to be your main Reddit account username (without the u/)
        while bot_creator == '':
            bot_creator = input('Enter your Reddit username without the \'u/\':\n')
    # print('Welcome u/' + bot_creator)
    
    # File paths
    version_path = 'data/version.txt'
    responseDF_path = 'ReplyDFs/HootyBotResponseDF.csv'
    blacklist_words_path = 'ReplyDFs/BlacklistWords.csv'
    last_comment_time_path = 'data/last_comment_time.txt'
    admin_codes_path = 'data/admin_codes.csv'
    opt_out_list_path = 'data/opt_out_list.csv'
    
    # Read in the bot's version number
    with open(version_path) as f:
        version = f.readlines()[0] 
        
    # Define global 'constants'
    APP_ID = os.environ.get('REDDIT_HOOTY_APP_ID')
    user_agent = 'reddit:' + APP_ID + ':' + version + ' (by /u/{})'.format(bot_creator)
    today = str(da.today())
    log_prefix = 'Logs/HootyBot_' + version + '_' + today
    log_file_path = log_prefix + ".log"
    csv_log_path = log_prefix + ".csv"
    bot_status_post_id = 'svj2yd'
    
    # Setting external urls
    github_README_url = 'https://github.com/{}/Hooty-Bot-Public/blob/main/README.md'.format(bot_creator)
    reply_suggestions_form = 'https://forms.gle/jJzJTGC36ykLhWxB6'
    unsub_url = 'https://www.reddit.com/message/compose/?to=HootyBot&subject=hb!unsubscribe&message=Hit%20send%20to%20finish%20unsubscribing.%20You%20may%20replace%20this%20message%20with%20your%20feedback%20if%20you%20wish.%20Do%20NOT%20edit%20the%20subject%20line%2C%20otherwise%20HootyBot%20may%20not%20recognize%20the%20message%20as%20an%20unsubscribe%20request.'
    subscribe_url = 'https://www.reddit.com/message/compose/?to=HootyBot&subject=hb!subscribe&message=Hit%20send%20to%20finish%20resubscribing.%20You%20may%20replace%20this%20message%20with%20your%20feedback%20if%20you%20wish.%20Do%20NOT%20edit%20the%20subject%20line%2C%20otherwise%20HootyBot%20may%20not%20recognize%20the%20message%20as%20a%20subscribe%20request.'

    # Template reply ending for a bot
    reply_ending = '\n\n^(I) ^(am) ^(a) ^(bot) ^(written) ^(by) [^({bot_creator})](https://www.reddit.com/user/{bot_creator}) ^(|) ^(Check) ^(out) ^(my) [^(Github)]({github_README_url}) \n\n'
    reply_ending += '^(If) ^(you) ^(no) ^(longer) ^(wish) ^(to) ^(receive) ^(replies) ^(from) ^({bot_username},) [^(unsubscribe here)]({unsub_url}) ^(|) ^(Alternatively,) ^(you) ^(could) ^(block) ^(me) \n\n'
    reply_ending += '^(Help) ^(improve) ^(Hooty\'s) [^(vocabulary)]({reply_suggestions_form}) ^(|) ^(Current) ^(version:) ^({v})'
    reply_ending = reply_ending.format(bot_creator = bot_creator, 
                                    github_README_url = github_README_url, 
                                    v = version, 
                                    reply_suggestions_form = reply_suggestions_form,
                                    unsub_url = unsub_url,
                                    bot_username = bot_username
                                    )
    
    # sr = "TheOwlHouse"
    sr = 'TOH_Bot_Testing'
    
    # Variables and data important for configuring HootyBot
    bot_config = {
        'metadata': {
            'bot_username': bot_username,                       # str: the bots username
            'sr': sr,                                    # str: the subreddit being monitored
            'version': version,                                 # str: the version of the bot
            'bot_creator': bot_creator,                         # str: the username of the bot creator
            'bot_status_post_id': bot_status_post_id,           # str: Reddit id of the bot status post
        },
        
        'file_path_names': {
            'responseDF_path': responseDF_path,                 # str: the directory path of responseDF
            'blacklist_words_path': blacklist_words_path,       # str: the directory path of blacklist_words
            'last_comment_time_path': last_comment_time_path,   # str: the directory path of last_comment_time
            'admin_codes_path': admin_codes_path,               # str: the directory path of admin codes
            'opt_out_list_path': opt_out_list_path,             # str: directory path of the opt out list
            'log_file_path': log_file_path,                     # str: name of log file
            'csv_log_path': csv_log_path,                       # str: name of csv log file
        
        },
        
        'urls': {
            'unsub_url': unsub_url,                             # str: url for unsubscribing
            'subscribe_url': subscribe_url,                     # str: url for resubscribing
        },
        
        'static_settings': {
            'skip_existing': True,                        # bool: if true, tells the bot to skip the 100 most recent msgs 
            'pause_after': 2,                                   # int: How many failed API calls to make before pausing
            'min_between_replies': 15,                          # int: Min minutes between replies
        },
        
        'dynamic_settings':{
            'replies_enabled': True,                      # bool: if true, allows the bot to reply to msgs
            'status': '',                                       # str: one of ['', online, reply_delayed, paused, offline]
            'reply_delay_remaining': -1                         # float: The delay time remaining until the bot can reply again 
        },
        
        'template_responses':{
            'reply_ending': reply_ending,                       # str: Template ending that HootyBot appends to the end of all replies
        },
    }
    
    with open("data/bot_config.json", 'w') as f:  
        json.dump(bot_config, f)
        print('bot_config.json saved.')


def main():
    # old_config()
    return
    
if  __name__ == '__main__':
    main()