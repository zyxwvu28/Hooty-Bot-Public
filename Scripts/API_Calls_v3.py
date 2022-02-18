'''
Functions for common API calls that HootyBot makes
Detects new posts and comments on a specific subreddit
'''

import pandas as pd
import praw as pr
import time as t
from datetime import datetime as dt
from datetime import date as da
import logging as log
import csv
from os import path, environ

# Set version number
version = 'v1.0'

# Define creator of bot
creator = environ.get('REDDIT_BOT_CREATOR')
if creator is None:
    print('Please remember to declare yourself as the creator of this bot!')
    creator = '' # Change this string to your main Reddit account username
        
# String representing todaay's date
today = str(da.today())

# Log files prefix
log_prefix = 'Logs/HootyBot_' + version + '_' + today

# Configure logging
log_file_name = log_prefix + ".log"
log.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s', 
                filename=log_file_name, 
                # encoding='utf-8', 
                level=log.DEBUG
                )

# Set up csv file
csv_log_name = log_prefix + ".csv"
header = ['Timestamp', 'Type', 'Author', 'Post_Title', 'Body', 'URL', 'ID']
if not(path.exists(csv_log_name)):
    with open(csv_log_name, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        
# Load the ResponseDF
responseDF_path = 'ReplyDFs\HootyBotResponseDF.csv'
responseDF = pd.read_csv(responseDF_path)
responseDF = responseDF.fillna('')

# Load the BlacklistWords
blacklist_words_path = 'ReplyDFs\BlacklistWords.csv'
blacklist_words = pd.read_csv(blacklist_words_path)['Blacklist']

# Custom function for logging and printing a message
def log_and_print(message, level = 'info'):
    if level == 'debug':
        log.debug(message)
    elif level == 'info':
        log.info(message)
    elif level == 'warning':
        log.warning(message)
    elif level == 'error':
        log.error(message)
    elif level == 'critical':
        log.critical(message)
    print(message)        

# Monitoring new posts
def monitor_new_posts(reddit_instance, sr, skip_existing = False, pause_after = 3, replies_enabled = False):
    # This function has no return statement, it is written to run forever (Take that halting problem!)
    # reddit_instance: a praw object for interacting with the Reddit API
    # sr: a string representing a subreddit
    # skip_existing: a bool, tells the function whether or not to skip the last 100 existing posts and comments
    # pause_after: int, after 'pause_after' failed API calls, pause the current API call and move on to the next one
    # replies_enabled: bool, decides whether to allow the bot to reply to comments and posts
    
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
            
            # Define variables for post data
            timestamp = dt.fromtimestamp(post.created_utc)
            author = post.author.name
            post_title = post.title
            body = post.selftext + poll_text
            url = post.url
            s_id = post.id      
            post_or_comment = 'post'  
            
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
                reply_to(post, username = username)
                    
                    
        # This loop checks for new comments
        log_and_print("Checking for new comments...")
        for comment in comments:            
            # If no new comment has been detected, break
            if comment is None:
                break
            failed_delay = 0.1
            
            # Define variables for comment data
            timestamp = dt.fromtimestamp(comment.created_utc)
            author = comment.author.name
            post_title = comment.link_title
            body = comment.body
            url = 'https://www.reddit.com' + comment.permalink
            s_id = comment.id
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
                reply_to(comment, username = username)
        
        # If no new post/comment has been detected recently, 
        # introduce an exponeentially increasing delay before checking again  
        log_and_print("Failed Delay = " + str(failed_delay))  
        t.sleep(failed_delay)
        if failed_delay < 16:
            failed_delay *= 1.2

# Reads in messages, detects keywords in them, then responds appropriately
# str, str -> int
def cond_except_parser(text_to_reply_to, responseDF = responseDF):   
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
def reply_to(msg_obj, username, reply_to_self = False):
    # post_or_comment: Object representing a post or comment
    
    # Anti-recursion mechanism. We don't want HootyBot replying to himself forever and ever and ever and ever...
    if (msg_obj.author.name == username) and not(reply_to_self):
        return
    
    # Template reply ending for a bot
    reply_ending = '^(I am a bot written by [{i}](https://www.reddit.com/user/{i}) | Check out my [Github](https://github.com/{i}))'.format(i = creator)
    
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
    
                
    reply_index = cond_except_parser(text_to_reply_to) 
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