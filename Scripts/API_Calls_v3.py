'''
Functions for common API calls that HootyBot makes
Detects new posts and comments on a specific subreddit
'''

import pandas as pd
import praw as pr
import time as t
from datetime import datetime as dt
import logging as log
import csv
from os import path

# Custom function for logging and printing a message
def log_and_print(message, level = 'info'):
    log_message = message.encode('unicode_escape')
    if level == 'debug':
        log.debug(log_message)
    elif level == 'info':
        log.info(log_message)
    elif level == 'warning':
        log.warning(log_message)
    elif level == 'error':
        log.error(log_message)
    elif level == 'critical':
        log.critical(log_message)
    print(message)        

# Reads in messages, detects keywords in them, then responds appropriately
# str, str -> int
def cond_except_parser(text_to_reply_to, bot_config): 
    
    # Load necessary bot config data
    responseDF_path = bot_config['responseDF_path']
    blacklist_words_path = bot_config['blacklist_words_path']
    
    # Load the ResponseDF
    responseDF = pd.read_csv(responseDF_path)
    responseDF = responseDF.fillna('')
    
    # Load the BlacklistWords
    blacklist_words = pd.read_csv(blacklist_words_path)['Blacklist']
      
    # returns a reply index, returns -1 if not found    
    DONT_REPLY = -1
    
    # Read in the conditions and exceptions
    conditions = responseDF['Condition']
    excepts = responseDF['Exception']
    
    # lowercase all strings for comparison to remove case-sensitivity
    text_to_reply_to_casefold = text_to_reply_to.casefold()
    for i in conditions:
        # If the condition word is a substring of the message body, 
        # then return the index for the proper response.
        if i.casefold() in text_to_reply_to_casefold:  
            # If a blacklisted keyword is found, don't reply
            for bword in blacklist_words:
                if bword.casefold() in text_to_reply_to_casefold:
                    return DONT_REPLY        
              
            # If an exception keyword is found, don't reply
            for j in excepts: 
                if (j != '') and (j.casefold() in text_to_reply_to_casefold):
                    return DONT_REPLY
                            
            # Implement exceptions!!!
            print('Remember to implement exceptions!!!')
                
            return responseDF[responseDF['Condition'] == i].index[0]
    
    # Insert special parsing code here
    print('Insert special parsing code here')
    
    # Insert special convos code here
    print('Insert special convos code here')
    
    # If no matches are found, don't reply
    return DONT_REPLY   
            
# Reply to posts or comments
def reply_to(msg_obj, bot_config, username, reply_to_self = False):
    # msg_obj: Object representing a post or comment
    
    # Load necessary bot config data
    version = bot_config['version']
    bot_creator = bot_config['bot_creator']
    responseDF_path = bot_config['responseDF_path']
    
    
    # Load the ResponseDF
    responseDF = pd.read_csv(responseDF_path)
    responseDF = responseDF.fillna('')
        
    # Anti-recursion mechanism. We don't want HootyBot replying to himself forever and ever and ever and ever...
    if (msg_obj.author.name == username) and not(reply_to_self):
        return
    
    # Template reply ending for a bot
    reply_ending = '^(I am a bot written by [{i}](https://www.reddit.com/user/{i}) | Check out my [Github](https://github.com/{i}) ) \n\n'.format(i = bot_creator) 
    reply_ending += '^(Help improve Hooty\'s [vocabulary](https://forms.gle/jJzJTGC36ykLhWxB6) | Current version: {v} )'.format(v = version)
    
    # Check if there's poll text, if so, add that to the detection
    try:
        poll_text = ''
        poll_options = msg_obj.poll_data.options
        for opt in poll_options:
            poll_text = poll_text + opt.text
        poll_text = poll_text + '\n\n'
    except:
        poll_text = ''
    
    timestamp = dt.fromtimestamp(msg_obj.created_utc)
    author = msg_obj.author.name
    s_id = msg_obj.id 
    
    # Check if message object is a post or comment, 
    # then modify the url and text to reply to accordingly
    if type(msg_obj) is pr.models.Submission:
        body = msg_obj.selftext + poll_text
        post_title = msg_obj.title
        url = msg_obj.url
        text_to_reply_to = post_title + body            
    elif type(msg_obj) is pr.models.Comment:
        body = msg_obj.body
        url = 'https://www.reddit.com' + msg_obj.permalink
        text_to_reply_to = body     
    else:
        raise TypeError("Error, post_or_comment must be a \'pr.models.Submission\' or \'pr.models.Comment object\'")
    
                
    reply_index = cond_except_parser(text_to_reply_to, bot_config) 
    if -1 != reply_index:
        message_body = responseDF['Reply'][reply_index]
        message = message_body + '\n\n' + reply_ending
        msg_obj.reply(message)
        print('')
        log_and_print("Replied to " + url + ' with the following message:')
        log_and_print('v----------------------v')
        log_and_print(message)
        log_and_print('^----------------------^')
        print('')
            
    return

# Monitoring new posts
def monitor_new_posts(reddit_instance, sr, bot_config, skip_existing = False, pause_after = 3, replies_enabled = False):
    # This function has no return statement, it is written to run forever (Take that halting problem!)
    # reddit_instance: a praw object for interacting with the Reddit API
    # sr: a string representing a subreddit
    # skip_existing: a bool, tells the function whether or not to skip the last 100 existing posts and comments
    # pause_after: int, after 'pause_after' failed API calls, pause the current API call and move on to the next one
    # replies_enabled: bool, decides whether to allow the bot to reply to comments and posts
    
    # Template for loading bot config
    # version = bot_config['version']
    # bot_creator = bot_config['bot_creator']
    # today = bot_config['today']
    # log_prefix = bot_config['log_prefix']
    # log_file_name = bot_config['log_file_name']
    # csv_log_name = bot_config['csv_log_name']
    # responseDF_path = bot_config['responseDF_path']
    # blacklist_words_path = bot_config['blacklist_words_path']
        
    # Set up csv file
    csv_log_name = bot_config['csv_log_name']
    header = ['Timestamp', 'Type', 'Author', 'Post_Title', 'Body', 'URL', 'ID']
    if not(path.exists(csv_log_name)):
        with open(csv_log_name, 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
    
    # Record which bot is being used and which subreddit it's monitoring
    username = reddit_instance.user.me().name
    subreddit = reddit_instance.subreddit(sr)
    log_and_print('u/' + username + " is now monitoring r/" + subreddit.display_name + ' for new posts and comments!')
    if replies_enabled:
        re = ''
    else: 
        re = 'NOT '
    log_and_print('Replies are ' + re + 'enabled')
     
    # Save the praw objects that monitor posts and comments
    posts = subreddit.stream.submissions(skip_existing = skip_existing, pause_after=pause_after)       
    comments = subreddit.stream.comments(skip_existing = skip_existing, pause_after=pause_after)
    
    # If the bot fails to detect new posts and comments, delay the time between API calls in an exponential fashion
    failed_delay = 0.1
    
    # Loop that continuously monitors and replies to posts and comments
    while True:
                
        # This loop checks for new posts
        log_and_print("Checking for new posts...")
        for post in posts:            
            # If no new post has been detected, break
            if post is None:
                break
            failed_delay = 0.1
                        
            # If the post is a poll, add the options to body
            try:
                poll_text = ''
                poll_options = post.poll_data.options
                i = 1
                for opt in poll_options:
                    poll_text = poll_text + '\n\n {}. '.format(i) + opt.text
                    i += 1
                poll_text = poll_text + '\n\n'
            except:
                poll_text = ''
            
            try:
                # Define variables for post data
                timestamp = dt.fromtimestamp(post.created_utc)
                author = post.author.name
                post_title = post.title
                body = post.selftext + poll_text
                url = post.url
                s_id = post.id      
                post_or_comment = 'post'  
            except:
                print("Error, post probably deleted...")
                continue
            
            # Encode emojis differently
            post_title_to_csv = post_title.encode('unicode_escape')
            body_to_csv = body.encode('unicode_escape')
            
            # Log post data to csv
            with open(csv_log_name, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                post_entry = [timestamp, post_or_comment, author, post_title_to_csv, body_to_csv, url, s_id]
                writer.writerow(post_entry)
            
            # Log and print post data
            print('')
            log_and_print('timestamp: ' + str(timestamp) + " EST")
            log_and_print("New post from u/" + author + ' titled \"{}\":'.format(post_title) )
            log_and_print('v----------------------v')
            log_and_print(body)
            log_and_print('^----------------------^')
            log_and_print("url: " + url)
            log_and_print("id: " + s_id)
            print('')
            
            # reply to the message if keywords are detected
            if replies_enabled:
                reply_to(post, bot_config, username = username)
                    
                    
        # This loop checks for new comments
        log_and_print("Checking for new comments...")
        for comment in comments:            
            # If no new comment has been detected, break
            if comment is None:
                break
            failed_delay = 0.1
            
            try:
                # Define variables for comment data
                timestamp = dt.fromtimestamp(comment.created_utc)
                author = comment.author.name
                post_title = comment.link_title
                body = comment.body
                url = 'https://www.reddit.com' + comment.permalink
                s_id = comment.id
            except:
                print("Error, comment likely deleted...")
                continue
                
            if author == username:
                post_or_comment = 'reply'
            else:
                post_or_comment = 'comment'  
            
            # Encode emojis differently
            post_title_to_csv = post_title.encode('unicode_escape')
            body_to_csv = body.encode('unicode_escape')
            
            # Log comment data to csv
            with open(csv_log_name, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                comment_entry = [timestamp, post_or_comment, author, post_title_to_csv, body_to_csv, url, s_id]
                writer.writerow(comment_entry)
            
            # Log and print comment data         
            print('')   
            log_and_print('timestamp: ' + str(timestamp) + " EST")
            log_and_print("New comment from u/" + author + ' on a post titled \"{}\":'.format(post_title) )
            log_and_print('v----------------------v')
            log_and_print(body)
            log_and_print('^----------------------^')
            log_and_print("url: " + url)
            log_and_print("id: " + s_id)
            print('')
            
            # reply to the message if keywords are detected
            if replies_enabled:
                reply_to(comment, bot_config, username = username)
        
        # If no new post/comment has been detected recently, 
        # introduce an exponeentially increasing delay before checking again  
        log_and_print("Failed Delay = " + str(failed_delay))  
        t.sleep(failed_delay)
        if failed_delay < 16:
            failed_delay *= 1.2