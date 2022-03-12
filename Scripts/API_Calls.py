'''
Functions for common API calls that the bot makes
Detects new posts and comments on a specific subreddit
'''

import sys
import pandas as pd
import praw as pr
import time as t
from datetime import datetime as dt
from datetime import timedelta
import logging as log
import csv
from os import path
import traceback
from random import random

def log_and_print(message: str, level: str = 'info' ) -> None:
    '''
    str, str -> None
    
    Custom function for logging and printing a message. Function doesn't output anything
    '''
    
    print(message)
    
    # Encode emojis differently    
    log_message = message#.encode('unicode_escape') # No longer required
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

def advanced_query(parsed_query: str) -> bool:
    '''
    str -> bool
    
    Processes the boolean operations inside of a parsed query using recursion
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

def q_parser(text_to_reply_to: str, cond: str) -> list:
    '''
    str, str -> list
    
    parses & q commands into lists that the advanced_query() function can handle
    Returns a list
    '''
    colon_idx = cond.find(':')
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
            
    return parsed_query

def advanced_cond_wrapper(text_to_reply_to: str, cond: str) -> bool: 
    '''
    str, str -> bool
    
    Wrapper for dealing with advanced conditions, 
    checks if text_to_reply_to satisfies the condition
    
    Syntax:
    - & q: is a str or a str struct such that each side of a boolean operator is either a str, or round brackets enclosing a q
        eg: <str> BOOL <str> BOOL (<str> BOOL <str>)
        eg: 'trauma' OR ('marcy' AND 'stab') OR 'agony' OR 'agoniz' OR 'emotional rollercoaster'
    - & prob: a float
        eg: <float>
        eg: 0.01
    - & probq: contains a float and a q seperated by a comma
        eg: <float>, <q>
        eg: 0.01, 'Lumity'
    '''
    
    # Determine the command
    colon_idx = cond.find(':')
    str_cmd = cond[2:colon_idx]
    
    # probq represents a query with a probability
    if str_cmd == 'probq':
        
        # Parse the probability threshold
        prob_idx = colon_idx+2
        comma_idx = cond.find(',')
        prob = float(cond[prob_idx:comma_idx])
        
        # Parse the query
        q_idx = comma_idx + 2
        q = cond[q_idx:]
        q = '& q: ' + q
        parsed_query = q_parser(text_to_reply_to, cond)
        query_result = advanced_query(parsed_query)
        
        # Generate a random number in [0.0, 1.0)
        # To simulate the probability necessary for replying
        x = random()
        if query_result and x < prob:
            return True
        else:
            return False

    # q represents an advanced query
    elif str_cmd == 'q':
        
        parsed_query = q_parser(text_to_reply_to, cond)
        
        # Return the query's result
        query_result = advanced_query(parsed_query)
        return query_result
        
    # prob represents a probability
    elif str_cmd == 'prob':
        
        # Parse the probability threshold
        prob_idx = colon_idx+2
        prob = float(cond[prob_idx:])
        
        # Generate a random number in [0.0, 1.0)
        # To simulate the probability necessary for replying
        x = random()
        if x < prob:
            return True
        else:
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
        except_cond = advanced_cond_wrapper(text_to_reply_to, except_words)
    else:
        except_cond = except_words.casefold() in text_to_reply_to_casefold
        
    return except_cond

def cond_except_parser(msg_obj: str, text_to_reply_to: str, bot_config: dict) -> int: 
    '''
    str, str, dict -> int
    
    Reads in messages, detects keywords in them, then returns an integer representing
    and index that can be used to output a response.
    '''
    
    # Load necessary bot config data
    responseDF_path = bot_config['responseDF_path']
    blacklist_words_path = bot_config['blacklist_words_path']
    
    # Load the ResponseDF
    responseDF = pd.read_csv(responseDF_path)
    responseDF = responseDF.fillna('')
        
    # Set post title if msg_obj is a comment
    if type(msg_obj) is pr.models.reddit.comment.Comment:
        post_text = msg_obj.link_title + msg_obj.submission.selftext
        post_text = post_text.casefold()
    else:
        post_text = ''
        
    # lowercase all strings for comparison to remove case-sensitivity
    text_to_reply_to_casefold = text_to_reply_to.casefold()
    check_blacklist = text_to_reply_to_casefold
    check_blacklist += post_text
    
    # returns a reply index, returns -1 if not found    
    DONT_REPLY = -1
    
    # Load the BlacklistWords
    blacklist_words = pd.read_csv(blacklist_words_path)['Blacklist']
    # If a blacklisted keyword is found, don't reply
    for bword in blacklist_words:
        if bword.casefold() in check_blacklist:
            return DONT_REPLY  
                  
    # Read in the conditions and exceptions
    conditions = responseDF['Condition']
    excepts = responseDF['Exception']
        
    for i in conditions:
        ### For advanced queries
        
        # Insert special convos code here
        # print('Insert special convos code here')
        
        
        # If an advanced condition is met,
        # then return the index for the proper response
        if i[0] == '&':                 
            parsed_cond = advanced_cond_wrapper(text_to_reply_to, i)
            response_index = responseDF[responseDF['Condition'] == i].index[0]
            
            if parsed_cond:
                except_cond = except_parser(excepts, response_index, text_to_reply_to)
                if except_cond:
                    return DONT_REPLY
                else:
                    return response_index                    
        
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
    
    # If no matches are found, don't reply
    return DONT_REPLY   
           
def check_reply_delay(bot_config: dict,
                      ) -> dict:
    '''
    dict -> dict
    
    Checks when the bot's last reply was.
    Changes bot_config accordingly.
    Calls edit_status() 
    '''
    
    # Load bot_config variables
    last_comment_time_path = bot_config['last_comment_time_path']
    min_between_replies = bot_config['min_between_replies']
    bot_username = bot_config['bot_username']
    
    # Create most recent reply file if missing:
    last_comment_time_path = bot_config['last_comment_time_path']
    if not(path.exists(last_comment_time_path)):
        with open(last_comment_time_path, 'w') as f:
            f.write('')   
    
    # Check the time of the most recent bot reply, except if bot_username is mentioned
    with open(last_comment_time_path, 'r') as f:
        last_comment_time = f.readline()
    
    # Check if bot's replies are on a timer delay
    if (last_comment_time != ''):    
        last_comment_time_obj = dt.strptime(last_comment_time, "%Y-%m-%d %H:%M:%S.%f")
        delta_since_last_comment = dt.now() - last_comment_time_obj
        min_between_replies_delta = timedelta(minutes = min_between_replies)
        reply_delay_remaining = min_between_replies_delta.seconds - delta_since_last_comment.seconds
        bot_config['reply_delay_remaining'] = reply_delay_remaining
        if (reply_delay_remaining > 0):
            mins_left = reply_delay_remaining//60
            secs_left = reply_delay_remaining%60
            time_till_reply_avail_msg = f"# ⏸ {bot_username}'s replies are currently paused. ⏸ \n\n## {bot_username} will continue to reply to messages in about {mins_left} mins and {secs_left} sec"
            custom_status = {
                'delay_active': True,
                'delay_message': time_till_reply_avail_msg
            }
            bot_config = edit_status(bot_config, True, custom_status)
            return bot_config
        else:
            bot_config = edit_status(bot_config, True) 
            return bot_config  
    else:
        bot_config = edit_status(bot_config, True) 
        return bot_config         

def reply_to(msg_obj: str, 
             bot_config: dict, 
             reply_to_self: bool = False
             ) -> None:
    '''
    str, dict, dict, bool -> None
    
    msg_obj: A praw object representing a post or comment
    
    Replies to posts or comments
    '''
                    
    # Load necessary bot config data
    bot_username = bot_config['bot_username']
    responseDF_path = bot_config['responseDF_path']
    min_between_replies = bot_config['min_between_replies']
    reply_ending = bot_config['reply_ending']
    opt_out_list_path = bot_config['opt_out_list_path']
    
    # Load the ResponseDF
    responseDF = pd.read_csv(responseDF_path)
    responseDF = responseDF.fillna('')
            
    # Create most recent reply file if missing:
    last_comment_time_path = bot_config['last_comment_time_path']
    if not(path.exists(last_comment_time_path)):
        with open(last_comment_time_path, 'w') as f:
            f.write('')   
            
    # Identify author of message
    author = msg_obj.author.name
            
    # Anti-recursion mechanism. We don't want the bot replying to itself forever and ever and ever and ever...
    if (author == bot_username) and not(reply_to_self):
        return

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
        raise TypeError("Error, msg_obj_type must be a \'pr.models.Submission\' or \'pr.models.Comment object\'")
                                    
    if bot_username in text_to_reply_to:
        reply_index = cond_except_parser(msg_obj, text_to_reply_to, bot_config) 
        if -1 != reply_index:
            message_body = responseDF['Reply'][reply_index]
            message = message_body + '\n\n' + reply_ending
            msg_obj.reply(message)
            with open(last_comment_time_path, 'w') as f:
                f.write(str(dt.now()))
            print('')
            log_and_print("Replied to " + url + ' with the following message:')
            log_and_print('v----------------------v')
            log_and_print(message)
            log_and_print('^----------------------^')
            print('')
        return
    
    # Check if there is currently a reply delay
    bot_config = check_reply_delay(bot_config)
    reply_delay_remaining = bot_config['reply_delay_remaining']
    if reply_delay_remaining > 0:
        return
        
    # Create opt-out csv if missing
    if not(path.exists(opt_out_list_path)):
        with open(opt_out_list_path) as f:
            csvf = csv.writer(f)
            csvf.writerow('users_opted_out')
            
    # Check if author has opted-out of bot's replies
    opt_out_list = pd.read_csv(opt_out_list_path)
    users_opted_out = opt_out_list['users_opted_out']
    if author in users_opted_out.values:
        return      
        
    # Reply to the message based on the ResponseDF conditions
    reply_index = cond_except_parser(msg_obj, text_to_reply_to, bot_config) 
    if -1 != reply_index:
        message_body = responseDF['Reply'][reply_index]
        message = message_body + '\n\n' + reply_ending
        msg_obj.reply(message)
        with open(last_comment_time_path, 'w') as f:
            f.write(str(dt.now()))
        print('')
        log_and_print("Replied to " + url + ' with the following message:')
        log_and_print('v----------------------v')
        log_and_print(message)
        log_and_print('^----------------------^')
        print('')
    check_reply_delay(bot_config)
            
    return

def edit_status(bot_config: dict, is_online: bool, custom_status: dict = {}) -> dict:
    '''
    dict, bool, dict -> dict
    
    Edits the bot's status message. 
    Changes bot_config
    '''
    
    # Load bot config variables
    bot_username = bot_config['bot_username']
    sr = bot_config['sr']
    bot_status_post_id = bot_config['bot_status_post_id']
    replies_enabled = bot_config['replies_enabled']
    status = bot_config['status']
    
    # Set the API to be ready to edit the post
    reddit = pr.Reddit(bot_username)
    bot_status_post = reddit.submission(id = bot_status_post_id)
    
    # Load custom status messages
    if 'delay_active' in custom_status:
        delay_active = custom_status['delay_active']
        delay_message = custom_status['delay_message']
    else: 
        delay_active = False
    
    # Detect which status message to output
    if is_online: # Online, replies enabled
        if replies_enabled:
            if delay_active:
                status_post_msg = delay_message + '\n\n'
                terminal_status_msg = delay_message
                status = 'reply_delayed'
            elif not(delay_active) and (status != 'online'):
                status_post_msg = '# ✅ {bot_username} is currently online! ✅ \n\n'.format(bot_username=bot_username)
                terminal_status_msg = 'Status post edited to indicate that {bot_username} is now ✅ online and replying ✅'.format(bot_username=bot_username)
                status_post_msg += '## {bot_username} is currently monitoring r/{sr} and is allowed to make replies.\n\n'.format(bot_username=bot_username, sr=sr) 
                status = 'online'
            else:
                return bot_config
        elif not(replies_enabled) and (status != 'paused'): # Online, replies disabled
            status_post_msg = ('# ✳️ {bot_username} is currently online, but won\'t reply! ✳️ \n\n'.format(bot_username=bot_username) +
                           '## {bot_username} is currently monitoring r/{sr} and is NOT allowed to make replies.\n\n'.format(bot_username=bot_username, sr=sr)
                            )
            terminal_status_msg = 'Status post edited to indicate that {bot_username} is now ✳️ online and NOT replying ✳️'.format(bot_username=bot_username)
            status = 'paused'
        else:
            return bot_config
    elif not(is_online) and (status != 'offline'): # Offline
        status_post_msg = '# ❌ {bot_username} is currently offline D,: ❌ \n\n' .format(bot_username=bot_username)
        terminal_status_msg = 'Status post edited to indicate that {bot_username} is now ❌ offline ❌'.format(bot_username=bot_username)
        status = 'offline'
    else:
        return bot_config
   
    # Append the end of the status message   
    status_post_msg += ('This automatic status message only detects errors in the source code. ' + 
                    'I run {bot_username} on my personal laptop, so if my laptop fails or turns off for any reason, ' +
                    'this post will not update to reflect that {bot_username} has gone offline. \n\n' +  
                    'Note: {bot_username} will only monitor and respond to posts and comments on r/TheOwlHouse. '+
                    'If you pm it, it won\'t respond automatically.')
    status_post_msg = status_post_msg.format(bot_username = bot_username)
    
    # Edit the status post, then log it
    bot_status_post.edit(status_post_msg)
    log_and_print(terminal_status_msg)
    print('')
    bot_config['status'] = status
    return bot_config

def check_admin_codes(msg_obj: pr.Reddit, bot_config: dict) -> dict:
    '''
    msg_obj, dict -> dict
    
    Checks comments to see if an admin code has been detected
    
    Changes bot_config
    ''' 
    
    # Load data from msg_obj
    body = msg_obj.body
    author = msg_obj.author
    url = 'https://www.reddit.com' + msg_obj.permalink
    
    # Load necessary data from bot_config
    admin_codes_path = bot_config['admin_codes_path']
    replies_enabled = bot_config['replies_enabled']
    reply_ending = bot_config['reply_ending']
    bot_creator = bot_config['bot_creator']
    bot_username = bot_config['bot_username']
    
    # Load the admin codes
    admin_codes = pd.read_csv(admin_codes_path)
    
    # Find the mods of the subreddit and the bot creator
    admin_code_users = [bot_creator]
    for i in msg_obj.subreddit.moderator():
        admin_code_users.append(i)
        
    # Load the codes and responses
    codes = admin_codes['Code']
    responses = admin_codes['Response']
    
    for code in codes:
        if (code in body) and (author in admin_code_users):
            
            reply_msg = responses[code == codes].array[0]+ reply_ending
            msg_obj.reply(reply_msg)
            
            print('')
            log_and_print("Replied to " + url + ' with the following message:')
            log_and_print('v----------------------v')
            log_and_print(reply_msg)
            log_and_print('^----------------------^')
            print('')
            
            if codes[0] == code: # pause code
                replies_enabled = False
                bot_config['replies_enabled'] = replies_enabled
                bot_config = edit_status(bot_config, True)
                return replies_enabled
            elif codes[1] == code: # stop code
                bot_config = edit_status(bot_config, False)
                exit_msg = 'u/' 
                exit_msg += str(author) 
                exit_msg += ' used the admin code `'
                exit_msg += code
                exit_msg += '`. The {bot_username} program is now exiting.'
                exit_msg = exit_msg.format(bot_username = bot_username)
                sys.exit(exit_msg)
            elif codes[2] == code: # unpause code
                replies_enabled = True
                bot_config['replies_enabled'] = replies_enabled
                bot_config = edit_status(bot_config, True)
                return bot_config
            
            return bot_config
    
    return bot_config

def log_msg(msg_obj: pr.Reddit, msg_obj_type: str, bot_config: dict) -> str:
    '''
    msg_obj, dict, dict -> str 
    
    Logs msg_obj data and then calls reply_to on the object.
    
    Returns msg_obj_type.
    '''
    
    # Load necessary bot config data
    csv_log_name = bot_config['csv_log_name']
    replies_enabled = bot_config['replies_enabled']
        
    if msg_obj_type != 'None':
                    
        # If the post is a poll, add the options to body
        try:
            poll_text = ''
            poll_options = msg_obj.poll_data.options
            i = 1
            for opt in poll_options:
                poll_text = poll_text + '\n\n [Option {}]: '.format(i) + opt.text
                i += 1
            poll_text = poll_text + '\n\n'
        except:
            poll_text = ''
        
        try:
            # Define variables for post data
            is_dst = t.localtime().tm_isdst
            if is_dst == 1:
                tz = ' EDT'
            else:
                tz = ' EST'
                
            timestamp = dt.fromtimestamp(msg_obj.created_utc)
            timestamp = str(timestamp) + tz
            author = msg_obj.author.name
            s_id = msg_obj.id      
            
            if msg_obj_type == 'post':
                post_title = msg_obj.title
                body = msg_obj.selftext + poll_text
                url = msg_obj.url
            elif msg_obj_type == 'comment':
                post_title = msg_obj.link_title
                body = msg_obj.body
                url = 'https://www.reddit.com' + msg_obj.permalink
            else: 
                print('Error: msg_obj_type must be one of [post, comment, None]')
                
        except BaseException as e:
            print('Error!')
            print(e)
            return msg_obj_type
        
        # Encode emojis differently
        post_title_to_csv = post_title.encode('unicode_escape')
        body_to_csv = body.encode('unicode_escape')
        
        # Log post data to csv
        with open(csv_log_name, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            post_entry = [timestamp, msg_obj_type, author, post_title_to_csv, body_to_csv, url, s_id]
            writer.writerow(post_entry)
        
        # Log and print post data
        if msg_obj_type == 'comment':
            on_a_post_ = ' on a post'
        else:
            on_a_post_ = ''
            
        msg_description = "New {msg_obj_type} from u/".format(msg_obj_type = msg_obj_type)
        msg_description += author 
        msg_description += '{on_a_post_} titled \"{post_title}\":'.format(on_a_post_ = on_a_post_, post_title = post_title)
        
        print('')
        log_and_print('timestamp: ' + timestamp)
        log_and_print(msg_description)
        log_and_print('v----------------------v')
        log_and_print(body)
        log_and_print('^----------------------^')
        log_and_print("url: " + url)
        log_and_print("id: " + s_id)
        print('')
        
        # reply to the message if keywords are detected
        if replies_enabled:
            reply_to(msg_obj, bot_config)
            
    msg_obj_type = 'None'
    return msg_obj_type

def check_inbox(reddit_instance: pr.Reddit, bot_config: dict) -> None:
    '''
    Reddit, dict -> None
    
    Checks the inbox for unread messages. 
    Modifies opt-out list if commands are found.
    Returns nothing
    '''
    
    # Load bot config variables
    unsub_url = bot_config['unsub_url']
    subscribe_url = bot_config['subscribe_url']
    opt_out_list_path = bot_config['opt_out_list_path']
    bot_username = bot_config['bot_username']
    
    # Create opt-out list csv if it doesn't exist
    if not(path.exists(opt_out_list_path)):
        with open(opt_out_list_path, 'w', newline = '') as f:
            csvf = csv.writer(f)
            csvf.writerow(['users_opted_out']) 
    
    # Load unread messages
    reddit = reddit_instance
    msgs = reddit.inbox.unread()
    for msg in msgs:
        log_and_print('New inbox notification, of type ' + str(type(msg)))
        if (type(msg) == pr.models.Message):
            log_and_print('Subject line: ' + msg.subject)
            
            # If message is unsubscribe, then execute unsubscribe script
            if (msg.subject == 'hb!unsubscribe'):
                author = msg.author
                
                # Read the opt out list csv
                with open(opt_out_list_path, 'a', newline = '') as f:
                    csvf = csv.writer(f)
                    csvf.writerow([author.name]) 
                    
                # Generate and send a reply message
                reply_msg = 'You have sucessfully opted-out of {bot_username}\'s replies.\n\n'
                reply_msg += '{bot_username} will no longer reply to posts and comments that you make. \n\n'
                reply_msg += 'Note that you\'ll still see {bot_username} responding to other people\'s posts and comments. \n\n'
                reply_msg += 'If you wish to not see {bot_username} entirely, use Reddit\'s block feature. \n\n'
                reply_msg += 'If you wish to resubscribe at a later date, use this [subscribe]({subscribe_url}) link.'
                reply_msg = reply_msg.format(subscribe_url = subscribe_url, bot_username = bot_username)
                msg.reply(reply_msg)
                log_and_print('Message Body: ' + msg.body)
                log_and_print('Successfully unsubscribed u/' + author.name + ' from {bot_username}\'s replies.'.format(bot_username = bot_username))
                
                # Mark the message as read
                msg.mark_read()
                
            # If message is subscribe, then execute subscribe script
            elif (msg.subject == 'hb!subscribe'):
                author = msg.author
                
                # Write to the opt out list csv
                df = pd.read_csv(opt_out_list_path)
                df = df[df.users_opted_out != str(author)]
                df.to_csv(opt_out_list_path, index = False)
                
                # Generate and send a reply message
                reply_msg = 'You have sucessfully opted back in for {bot_username}\'s replies.\n\n'
                reply_msg += '{bot_username} will now reply to new posts and comments that you make. '
                reply_msg += 'If you wish to unsubscribe again, use this [unsubscribe]({unsub_url}) link.'
                reply_msg = reply_msg.format(unsub_url = unsub_url, bot_username = bot_username)
                msg.reply(reply_msg)
                log_and_print('Message Body: ' + msg.body)
                log_and_print('Successfully resubscribed u/' + author.name + ' to {bot_username}\'s replies.'.format(bot_username = bot_username))
                
        # Mark the message as read
        msg.mark_read()
        print('')
    
def monitor_new_posts(reddit_instance: pr.Reddit, 
                      bot_config: dict, 
                      ) -> dict:
    '''
    Reddit, str, dict, dict, bool, int, bool -> dict
    
    Monitors new posts.
    This function has no return statement, it is written to run forever 
    (Take that halting problem!)
    
    reddit_instance: a praw object for interacting with the Reddit API
    sr: a string representing a subreddit
    skip_existing: a bool, tells the function whether or not to skip the last 100 existing posts and comments
    pause_after: int, after 'pause_after' failed API calls, pause the current API call and move on to the next one
    replies_enabled: bool, decides whether to allow the bot to reply to comments and posts
    
    Changes bot_config. Will return it if an error is raised.
    '''
       
    # Template for loading bot config
    # bot_username = bot_config['bot_username']
    # sr = bot_config['sr']
    # responseDF_path = bot_config['responseDF_path']
    # blacklist_words_path = bot_config['blacklist_words_path']
    # last_comment_time_path = bot_config['last_comment_time_path']
    # version = bot_config['version']
    # bot_creator = bot_config['bot_creator']
    # log_file_name = bot_config['log_file_name']
    # csv_log_name = bot_config['csv_log_name']
    # bot_status_post_id = bot_config['bot_status_post_id']
    # skip_existing = bot_config['skip_existing']
    # replies_enabled = bot_config['replies_enabled']
    # pause_after = bot_config['pause_after']
    # min_between_replies = bot_config['min_between_replies']
    # unsub_url = bot_config['unsub_url']
    # subscribe_url = bot_config['subscribe_url']
    # opt_out_list_path = bot_config['opt_out_list_path']
    
    try:
        # Load bot config settings
        skip_existing = bot_config['skip_existing']
        replies_enabled = bot_config['replies_enabled']
        pause_after = bot_config['pause_after']
        sr = bot_config['sr']
            
        # Create logging csv file if missing
        csv_log_name = bot_config['csv_log_name']
        header = ['Timestamp', 'Type', 'Subreddit', 'Author', 'Post_Title', 'Body', 'URL', 'ID', 'replied_to_id', 'post_id']
        if not(path.exists(csv_log_name)):
            with open(csv_log_name, 'w', encoding='UTF8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(header)
                    
        # Record which bot is being used and which subreddit it's monitoring
        bot_username = reddit_instance.user.me().name
        subreddit = reddit_instance.subreddit(sr)
        log_and_print('u/' + bot_username + " is now monitoring r/" + subreddit.display_name + ' for new posts and comments!')
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
            print('')  
            # This loop checks for new posts
            log_and_print("Checking for new posts...")
            for post in posts:        
                # Check inbox and reply delay
                check_inbox(reddit_instance, bot_config)
                bot_config = check_reply_delay(bot_config)
                    
                # If no new post has been detected, break
                if post is None:
                    msg_obj_type = 'None'
                    break
                
                # Reset delay, save message data
                failed_delay = 0.1
                msg_obj_type = 'post'
                msg_obj = post
                
                # Log the message, and reply if keywords are detected
                msg_obj_type = log_msg(msg_obj, msg_obj_type, bot_config)
                        
                    
            # This loop checks for new comments
            log_and_print("Checking for new comments...")
            for comment in comments: 
                # Check inbox and reply delay
                check_inbox(reddit_instance, bot_config)
                bot_config = check_reply_delay(bot_config)
                
                # If no new comment has been detected, break
                if comment is None:
                    msg_obj_type = 'None'
                    break
                
                # Reset delay, save message data
                failed_delay = 0.1
                msg_obj_type = 'comment'
                msg_obj = comment
                
                # Check if any admin codes have been used
                bot_config = check_admin_codes(msg_obj, bot_config)
                
                # Log the message, and reply if keywords are detected
                msg_obj_type = log_msg(msg_obj, msg_obj_type, bot_config)
                
                    
            # If no new post/comment has been detected recently, 
            # introduce an exponeentially increasing delay before checking again  
            log_and_print('API calls have found no new posts/comments.')
            log_and_print('Sleeping for ' + str(failed_delay) + ' s' )  
            t.sleep(failed_delay)
            if failed_delay < 16:
                failed_delay *= 1.2
    
    except:
        return bot_config
             
def activate_bot(bot_config: dict,
                 ) -> None:
    '''
    str, str, dict, dict, bool, int, bool -> None
    
    Activates the bot    
    '''
    
    # Load necessary bot config data
    bot_username = bot_config['bot_username']
    sr = bot_config['sr']
    
    # Load credentials from praw.ini to generate a Reddit instance
    try:
        reddit = pr.Reddit(bot_username)
    except:
        print("WARNING! praw.ini file not set up properly!")
        sys.exit("WARNING! praw.ini file not set up properly!")
    
    bot_creator = bot_config['bot_creator']
    
    while True:
        try:
            # Update bot status to 'online'
            if sr == 'TheOwlHouse':
                bot_config = edit_status(bot_config, True)
                
            # Monitor for new posts/comments
            bot_config = monitor_new_posts(
                                reddit_instance = reddit,
                                bot_config = bot_config, 
                                )  
            
        # If an error is detected, notify creator and update status post 
        except BaseException as e:
            
            try:
                if e.message in ['Something is broken, please try again later.',
                                'Comments are locked.'
                                ]:
                    t.sleep(60)
                    continue
            except:
                print(e)
            
            if sr == 'TheOwlHouse':
                bot_config = edit_status(bot_config, False)
        
            err_message = 'An error occurred in the code: \n\n'
            err_message += traceback.format_exc()
            print(err_message)
            reddit.redditor(bot_creator).message('{bot_username} is now offline'.format(bot_username = bot_username), err_message )
            break
