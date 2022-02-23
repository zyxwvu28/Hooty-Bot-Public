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
import random as rng

def log_and_print(message: str, level: str = 'info' ) -> None:
    '''
    str, str -> None
    
    Custom function for logging and printing a message. Function doesn't output anything
    '''
    
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

def advanced_query(parsed_query: str) -> bool:
    '''
    str -> bool
    
    Processes the boolean operations inside of a parsed query
    '''
    
    pq_len = len(parsed_query)
    if pq_len == 1:
        return parsed_query[0]  
    
    curr_idx = 0
    while curr_idx < pq_len - 1:
        prev_idx = curr_idx - 1
        next_idx = curr_idx + 1
        lb_count = 0
        rb_count = 0
        if '(' == parsed_query[curr_idx]:
            lb_count += 1
            i = curr_idx + 1
            rb_idx = 0
            while i < pq_len:
                ch1 = parsed_query[i]
                if ')' == ch1:
                    rb_count += 1
                elif '(' == ch1:
                    lb_count += 1
                
                if lb_count == rb_count:
                    rb_idx = i  
                    break
                i += 1
                
            replace_bracket = advanced_query(parsed_query[next_idx:rb_idx])
            if rb_idx + 1 == pq_len:
                after_rb = []
            else:
                after_rb = parsed_query[(rb_idx+1):]
            if type(replace_bracket) is bool:
                new_lst = parsed_query[:curr_idx] + [replace_bracket] + after_rb 
            else:
                new_lst = parsed_query[:curr_idx] + replace_bracket + after_rb
            return advanced_query(new_lst)
        elif parsed_query[curr_idx] == 'OR' and parsed_query[next_idx] != '(':
            new_bool = parsed_query[prev_idx] or parsed_query[next_idx]
            new_lst = [new_bool] + parsed_query[(next_idx+1):]
            return advanced_query(new_lst)
        elif parsed_query[curr_idx] == 'AND' and parsed_query[next_idx] != '(':
            new_bool = parsed_query[prev_idx] and parsed_query[next_idx]
            new_lst = [new_bool] + parsed_query[(next_idx+1):]
            return advanced_query(new_lst)
        curr_idx += 1    

def advanced_keyword_parser(text_to_reply_to: str, cond: str) -> bool: 
    '''
    str, str -> bool
    
    Parses the advanced keyword search, checks if text_to_reply_to satisfies the condition
    '''
    
    # What's the command?
    colon_idx = cond.find(':')
    str_cmd = cond[2:colon_idx]
    
    # probq represents a query with a probability
    if str_cmd == 'probq':
        return False

    # q represents an advanced query
    elif str_cmd == 'q':
        parsed_query = []
        cond_len = len(cond)
        i = colon_idx + 2
        
        # Loop through all chars in the cond str
        while i < cond_len:
            ch1 = cond[i]
            
            # if a ' is detected, parse the enclosed word as one str
            if '\'' == ch1:
                temp_word = ''
                for j in range(i+1, cond_len):
                    ch2 = cond[j]                        
                    if '\'' == ch2:
                        if '\\' == cond[j-1]:
                            temp_word += ch2
                            continue
                        i = j
                        break
                    if '\\' == ch2:
                        continue
                    temp_word += ch2
                parsed_query.append(temp_word)
                
            # if any bracket is detected, parse it as-is
            elif ch1 in ['(', ')']:
                parsed_query.append(ch1)
                
            # if either boolean operator is detected, parse the entire operator
            elif cond[i:i+2] == "OR":
                parsed_query.append('OR')
            elif cond[i:i+3] == 'AND':
                parsed_query.append('AND')
                
            # ignore whitespaces and other foreign characters, then iterate
            i += 1
        
        # convert all keywords in the cond into a boolean value 
        # based on whether the keyword is found in the msg_obj                   
        text_to_reply_to_casefold = text_to_reply_to.casefold()
        pq_len = len(parsed_query)
        for i in range(pq_len):
            x = parsed_query[i]
            if not(x in ['(', ')', 'AND', 'OR']):
                parsed_query[i] = x.casefold() in text_to_reply_to_casefold            
        
        # Return the query's result
        query_result = advanced_query(parsed_query)
        return query_result
        
    # prob represents a probability
    elif str_cmd == 'prob':
        return False
    
    return False

def except_parser(excepts_DF: pd.DataFrame, response_index: int, text_to_reply_to: str) -> bool:
    '''
    Dataframe, int, str -> bool
    
    Parses the except messages. Returns a boolean that represents whether the except condition
    has been detected.    
    '''
    
    text_to_reply_to_casefold = text_to_reply_to.casefold()
    except_words = excepts_DF[response_index]
    if except_words == '':
        return False
    elif except_words[0] == '&':
        except_cond = advanced_keyword_parser(text_to_reply_to, except_words)
    else:
        except_cond = except_words.casefold() in text_to_reply_to_casefold
        
    return except_cond

def cond_except_parser(text_to_reply_to: str, bot_config: dict) -> int: 
    '''
    str, dict -> int
    
    Reads in messages, detects keywords in them, then returns an integer representing
    and index that can be used to output a response.
    '''
    
    # Load necessary bot config data
    responseDF_path = bot_config['responseDF_path']
    blacklist_words_path = bot_config['blacklist_words_path']
    
    # Load the ResponseDF
    responseDF = pd.read_csv(responseDF_path)
    responseDF = responseDF.fillna('')
    
    # lowercase all strings for comparison to remove case-sensitivity
    text_to_reply_to_casefold = text_to_reply_to.casefold()
    
    # returns a reply index, returns -1 if not found    
    DONT_REPLY = -1
    
    # Load the BlacklistWords
    blacklist_words = pd.read_csv(blacklist_words_path)['Blacklist']
    # If a blacklisted keyword is found, don't reply
    for bword in blacklist_words:
        if bword.casefold() in text_to_reply_to_casefold:
            return DONT_REPLY  
              
     
    ### For simple queries
    
    # Read in the conditions and exceptions
    conditions = responseDF['Condition']
    excepts = responseDF['Exception']
        
    for i in conditions:
        ### For advanced queries
        
        # Insert special convos code here
        # print('Insert special convos code here')
        
        
        # Insert special parsing code here
        # print('Insert special parsing code here')
        if i[0] == '&':                 
            parsed_cond = advanced_keyword_parser(text_to_reply_to, i)
            response_index = responseDF[responseDF['Condition'] == i].index[0]
            
            if parsed_cond:
                except_cond = except_parser(excepts, response_index, text_to_reply_to)
                if except_cond:
                    return DONT_REPLY
                else:
                    return response_index
                
                # except_words = excepts[response_index]
                # if except_words[0] == '&':
                #     except_cond = advanced_keyword_parser(text_to_reply_to, except_words)
                # else:
                #     except_cond = except_words.casefold() in text_to_reply_to_casefold
                    
                # if except_cond:
                #     return DONT_REPLY
                # else:
                #     return response_index                       
        
        ### For simple queries
        # If the condition word is a substring of the message body, 
        # then return the index for the proper response.
        if i.casefold() in text_to_reply_to_casefold:                           
            response_index = responseDF[responseDF['Condition'] == i].index[0]
            
            # If an exception keyword is found, don't reply            
            except_cond = except_parser(excepts, response_index, text_to_reply_to)
            if except_cond:
                return DONT_REPLY
            else:
                return response_index            
            
            # for j in excepts: 
            #     if (j != '') and (j.casefold() in text_to_reply_to_casefold):
            #         return DONT_REPLY
                            
            # return response_index
    
    
    # If no matches are found, don't reply
    return DONT_REPLY   
            
def reply_to(msg_obj: str, 
             bot_config: dict, 
             external_urls: dict, 
             username: str, 
             reply_to_self: bool = False
             ) -> None:
    '''
    str, dict, dict, str, bool -> None
    
    msg_obj: A praw object representing a post or comment
    
    Replies to posts or comments
    '''
        
    # Load necessary bot config data
    version = bot_config['version']
    bot_creator = bot_config['bot_creator']
    responseDF_path = bot_config['responseDF_path']
    
    # Load External URLs
    github_README_url = external_urls['github_README_url']
    reply_suggestions_form = external_urls['reply_suggestions_form']
    
    # Load the ResponseDF
    responseDF = pd.read_csv(responseDF_path)
    responseDF = responseDF.fillna('')
        
    # Anti-recursion mechanism. We don't want HootyBot replying to himself forever and ever and ever and ever...
    if (msg_obj.author.name == username) and not(reply_to_self):
        return
    
    # Template reply ending for a bot
    reply_ending = '^(I am a bot written by [{i}](https://www.reddit.com/user/{i}) | Check out my [Github]({github_README_url}) ) \n\n'.format(i = bot_creator, github_README_url = github_README_url) 
    reply_ending += '^(Help improve Hooty\'s [vocabulary]({reply_suggestions_form}) | Current version: {v} )'.format(v = version, reply_suggestions_form = reply_suggestions_form)
    
    # Check if there's poll text, if so, add that to the detection
    try:
        poll_text = ''
        poll_options = msg_obj.poll_data.options
        for opt in poll_options:
            poll_text = poll_text + opt.text
        poll_text = poll_text + '\n\n'
    except:
        poll_text = ''
        
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

def monitor_new_posts(reddit_instance: pr.Reddit, 
                      sr: str, 
                      bot_config: dict, 
                      external_urls: dict, 
                      skip_existing: bool = False, 
                      pause_after: int = 3, 
                      replies_enabled: bool = False
                      ) -> None:
    '''
    Reddit, str, dict, dict, bool, int, bool -> None
    
    Monitors new posts.
    This function has no return statement, it is written to run forever 
    (Take that halting problem!)
    
    reddit_instance: a praw object for interacting with the Reddit API
    sr: a string representing a subreddit
    skip_existing: a bool, tells the function whether or not to skip the last 100 existing posts and comments
    pause_after: int, after 'pause_after' failed API calls, pause the current API call and move on to the next one
    replies_enabled: bool, decides whether to allow the bot to reply to comments and posts
    '''
       
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
                    poll_text = poll_text + '\n\n [Option {}]: '.format(i) + opt.text
                    i += 1
                poll_text = poll_text + '\n\n'
            except:
                poll_text = ''
            
            try:
                # Define variables for post datais_dst = t.localtime().tm_isdst
                if is_dst == 1:
                    tz = ' EDT'
                else:
                    tz = ' EST'
                    
                timestamp = dt.fromtimestamp(comment.created_utc)
                timestamp = str(timestamp) + tz
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
                reply_to(post, bot_config, external_urls, username = username)
                    
                    
        # This loop checks for new comments
        log_and_print("Checking for new comments...")
        for comment in comments:            
            # If no new comment has been detected, break
            if comment is None:
                break
            failed_delay = 0.1
            
            try:
                # Define variables for comment data
                is_dst = t.localtime().tm_isdst
                if is_dst == 1:
                    tz = ' EDT'
                else:
                    tz = ' EST'
                    
                timestamp = dt.fromtimestamp(comment.created_utc)
                timestamp = str(timestamp) + tz
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
                reply_to(comment, bot_config, external_urls, username = username)
        
        # If no new post/comment has been detected recently, 
        # introduce an exponeentially increasing delay before checking again  
        log_and_print('API calls have found no new posts/comments.')
        log_and_print('Sleeping for ' + str(failed_delay) + ' s' )  
        t.sleep(failed_delay)
        if failed_delay < 16:
            failed_delay *= 1.2
    
def bot_offline(username: str, bot_status_post_id: str) -> None:
    '''
    str, str -> None
    
    Updates the status post to the OFFLINE state.
    '''
    reddit = pr.Reddit(username)
    bot_status_post = reddit.submission(id = bot_status_post_id)
    bot_status_post.edit('# ❌ HootyBot is currently offline D: ❌ \n\n' +
                         'This automatic status message only detects errors in the source code. ' + 
                         'I run HootyBot on my personal laptop, so if my laptop fails or turns off for any reason, ' +
                         'this post will not update to reflect that HootyBot has gone offline. \n\n' +  
                         'Note: HootyBot will only monitor and respond to posts and comments on r/TheOwlHouse. '+
                         'If you pm it, it won\'t respond automatically.')
    log_and_print('Status post edited to indicate that HootyBot is now offline')
    print('')
           
def activate_bot(username: str, 
                 sr: str, 
                 bot_config: dict, 
                 external_urls: dict, 
                 skip_existing: bool = False, 
                 pause_after: int = 3, 
                 replies_enabled: bool = False
                 ) -> None:
    '''
    str, str, dict, dict, bool, int, bool -> None
    
    Activates the bot    
    '''
    # Load credentials from praw.ini to generate a Reddit instance
    reddit = pr.Reddit(username)
    
    bot_creator = bot_config['bot_creator']
    bot_status_post_id = bot_config['bot_status_post_id']
    
    while True:
        try:
            # Update bot status to 'online'
            if sr == 'TheOwlHouse':
                bot_status_post = reddit.submission(id = bot_status_post_id)
                bot_status_post.edit('# ✅ HootyBot is currently online! ✅ \n\n' +
                                    'This automatic status message only detects errors in the source code. ' + 
                                    'I run HootyBot on my personal laptop, so if my laptop fails or turns off for any reason, ' +
                                    'this post will not update to reflect that HootyBot has gone offline. \n\n' +  
                                    'Note: HootyBot will only monitor and respond to posts and comments on r/TheOwlHouse. ' +
                                    'If you pm it, it won\'t respond automatically.')
                log_and_print('Status post edited to indicate that HootyBot is now online')
                    
            # Monitor for new posts/comments
            monitor_new_posts(reddit, 
                            sr, 
                            bot_config = bot_config, 
                            external_urls = external_urls,
                            skip_existing = skip_existing, 
                            pause_after = pause_after, 
                            replies_enabled = replies_enabled)  
            
        # If an error is detected, notify creator and update status post 
        except BaseException as e:
            
            if e.message == 'Something is broken, please try again later.':
                t.sleep(60)
                continue
            
            if sr == 'TheOwlHouse':
                bot_offline(username, bot_status_post_id)
        
            err_message = 'An error occurred in the code: \n\n' + str(e) 
            print(err_message)
            reddit.redditor(bot_creator).message('HootyBot is now offline', err_message )
            break
