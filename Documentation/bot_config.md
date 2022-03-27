# bot_config.json Documentation <!-- omit in TOC -->
- [About](#about)
- [Variables](#variables)
  - [`metadata`](#metadata)
  - [`file_path_names`](#file_path_names)
  - [`urls`](#urls)
  - [`static_settings`](#static_settings)
  - [`dynamic_settings`](#dynamic_settings)
  - [`template_responses`](#template_responses)

## About
This file describes all variables defined in bot_config.json

## Variables

### `metadata`
| Variable | Data Type | Description |
| -------- | ----------- | ----------- |
| `metadata` | dict | Contains a dictionary that contains information about the bot |
| `bot_username` | str | Reddit username of the bot |
| `sr` | str | Subreddit that the bot monitors |
| `version` | str | Version number of the bot |
| `bot_creator` | str | Reddit username of the bot operator |
| `bot_status_post_id` | str | The Reddit id of the bot's status post |

### `file_path_names`
| Variable | Data Type | Description |
| -------- | ----------- | ----------- |
| `file_path_names` | dict | Contains a dictionary that contains file path names of important files |
| `responseDF_path` | str | File path of the `.csv` that contains the keyword-response pairs for the bot's vocabulary |
| `blacklist_words_path` | str | File path of the `.csv` that contains the words that the bot will avoid replying to |
| `last_comment_time_path` | str | File path of `.txt` that contains the timestamp of the last reply the bot made |
| `admin_codes_path` | str | File path of the `.csv` that contains a list of admin codes |
| `opt_out_list_path` | str | File path of the `.csv` that contains the list of users that opted out of receiving comments from the bot |
| `log_file_path` | str | File path of the `.log` file for the bot |
| `csv_log_path` | str | File path of the `.csv` that contains all posts and comments that the bot has read |

### `urls`
| Variable | Data Type | Description |
| -------- | ----------- | ----------- |
| `urls` | dict | Contains a dictionary that contains urls |
| `unsub_url` | str | url for unsubscribing from the bot's replies |
| `subscribe_url` | str | url for resubscribing to the bot's replies |

### `static_settings`
| Variable | Data Type | Description |
| -------- | ----------- | ----------- |
| `static_settings` | dict | Contains a dictionary that contains variables that the bot shouldn't change while running. These variables control important setting for the bot |
| `skip_existing` | bool | Controls whether the bot skips the last 100 posts and comments immediately after turning it on |
| `pause_after` | int | Controls how many failed API calls the bot should receive before pausing for a while |
| `min_between_replies` | int | Controls the reply cooldown. After the bot makes a reply, it will wait `min_between_replies` minutes before being allowed to make another reply |

### `dynamic_settings`
| Variable | Data Type | Description |
| -------- | ----------- | ----------- |
| `dynamic_settings` | dict | Contains a dictionary that contains variables that the bot can change while running.  These variables control important setting for the bot |
| `replies_enabled` | bool | Indicates whether replies are currently enabled |
| `status` | str | Indicates the status messages of the bot. One of: <ul><li>'  '</li><li>online</li><li>reply_delayed</li><li>paused</li><li>offline</li></ul> |
| `reply_delay_remaining` | float | Indicates the reply cooldown remaining in minutes |

### `template_responses`
| Variable | Data Type | Description |
| -------- | ----------- | ----------- |
| `template_responses` | dict | Contains a dictionary that contains template responses for the bot to reply with |
| `reply_ending` | str | The ending message template that the bot appends to the end of every reply |


