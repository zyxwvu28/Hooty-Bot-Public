import API_Calls as api

# Variables and data importamt for configuring HootyBot
bot_config = {
    'metadata':{
        'bot_username': 'HootyBot',                               # str: the bots username
        'sr': 'TheOwlHouse',                                           # str: the subreddit being monitored
        'bot_status_post_id': 'svj2yd',           # str: Reddit id of the bot status post
    },
    
    'dynamic_settings':{
        'replies_enabled': False,                      # bool: if true, allows the bot to reply to msgs
        'status': ''
    }
}

api.edit_status(bot_config, False)
        