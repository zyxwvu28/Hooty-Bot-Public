# HootyBot README Table of Contents
1. [About HootyBot (v1.1.7)](#About-HootyBot)
    1. [Purpose](#Purpose)
    2. [How does HootyBot work? (TLDR Version)](#1b)
    3. [Does HootyBot use machine learning or neural networks?](#1c)
    4. [Inspiration](#1d)
2. [Data and Privacy](#2)
    1. [Collection of Data](#2a)
    2. [Use of Data](#2b)
3. [Suggestions, Questions, Concerns, Comments?](#3) 
4. [Future Plans for HootyBot](#4)
5. [Version Logs](#5) 


## 1. About HootyBot (v1.1.7) <a name = "About-HootyBot"></a>

### Purpose <a name = "Purpose"></a>

Created by [u/zyxwvu28](https://www.reddit.com/user/zyxwvu28) (he/him), the purpose of [u/HootyBot](https://www.reddit.com/user/HootyBot) is to entertain the members of [r/TheOwlHouse](https://www.reddit.com/r/TheOwlHouse/) by providing a bot that will automatically respond to new posts and comments with something that Hooty might say. Hooty is a comic relief character from The Owl House, an animated TV show from the Disney Channel. 

I want this project to have community input in order to improve it. You can contribute in many ways including:
- Providing keyword-reply suggestions to [improve Hooty's vocabulary](https://forms.gle/67fM5hwX78DHaf6s6)
- [Providing your feedback](https://forms.gle/Ct6V5KxEHe3n73g57), even if it's negative (you can remain anonymous)
- Improve documentation of code on this repository by making a Pull Request
- Finding bugs and reporting them in Issues (If the bug is security/authentication related, please pm me on Reddit @ [u/zyxwvu28](https://www.reddit.com/user/zyxwvu28) instead)
- Suggest features either by submitting an Issue or a Pull Request

The code for this bot has been made open source in [this repository](https://github.com/zyxwvu28/Hooty-Bot-Public). You are free to use this code anyway you like, but it is provided 'as-is' (i.e. there is no warranty for this source code). 

DISCLAIMER: This project is in no way associated with any other profiles with the username "HootyBot" outside of Reddit (i.e. This project is not associated with the Twitter profile @HootyBot).

### How does HootyBot work? (TLDR Version)<a name = "1b"></a>
HootyBot constantly monitors the r/TheOwlHouse subreddit for new posts and comments (herein refered to as a 'message'). When it detects a message, it will iterate through a dataframe (saved as a .csv file) that contains the following hardcoded information: 
1. Keywords or conditions that HootyBot looks for, 
2. What to reply with if a keyword is detected in the message, and
3. Sensitive keywords to avoid so that HootyBot doesn't accidentally insult someone. 

HootyBot's search function checks if the keyword (or phrase) is a substring of the posted message, this search is NOT case-sensitive. 

### Does HootyBot use machine learning or neural networks? <a name = "1c"></a>
No. Unfortunately, I have almost zero knowledge in either of those fields, so I don't plan on using them any time soon to improve HootyBot. Everything that HootyBot does is equivalent to hardcoding in a bunch of if-else statements. HootyBot does not 'learn' from its interactions with users. However, the developer (u/zyxwvu28) does learn and keeps logs of all interactions that HootyBot makes with other users. I will be observing how people respond to HootyBot's interactions and will make modifications accordingly. My goal is to entertain people with this bot, possibly make you spit out that glass of water that are drinking right now.

### Inspiration <a name = "1d"></a>
I was inspired to start this project by the following two projects:
1. [u/\_SwiftWind\_](https://www.reddit.com/user/_SwiftWind_/) bot built by [u/anytarseir67](https://www.reddit.com/u/anytarseir67/) on [r/PrincessesOfPower](https://www.reddit.com/r/PrincessesOfPower/). This bot has been inactive since the end of January 2022, but it was funny seeing it respond to posts on the SheRa subreddit. Its functionality was quite limited, but nevertheless, it inspired me to build a Hooty version of the bot. Sadly, the user who created that didn't make their code open source, and I respect that choice, but it would've been nice if I had something to work off of instead of building everything from scratch.
2. [The Owl House Hiatus Tracker](https://xman2156.github.io/TOH/) built, managed, and constantly updated by [xman2156](https://github.com/xman2156), this website is the one-stop shop for quick information about the hiatuses of popular Disney shows (plus Arcane). This user made their code open source, and seeing a small community form around it inspired me to make my code open source.

## 2. Data and Privacy <a name = "2"></a>

In short, HootyBot collects and stores any text you make in posts or comments during the periods when it's online. It then uses the collected text data to generate its witty responses. HootyBot does not collect any data when it is offline. All this data is publicly available for anyone to view on Reddit, even if they do not have a Reddit account. I operate under the assumption that you're all ok with this data collection as you consented to Reddit collecting and publishing the exact same data, but I feel that it is important to state the data I've collected from you. I will not distribute or sell your data to any third-party. If you have any concerns or questions, refer to [Suggestions, Questions, Concerns, Comments?](#3). 

### Collection of Data <a name = "2a"></a>
In order to do its job, HootyBot collects and uses publicly available data from users of r/TheOwlHouse. When you created a Reddit account, you agreed to Reddit's terms and conditions, and data privacy policy. I just use the data that Reddit publicly provides. [Review Reddit's Privacy Policy here](https://www.redditinc.com/policies/privacy-policy)

To be specific, when HootyBot is online, it collects and stores the following data:
- All the posts you make on r/TheOwlHouse during periods when HootyBot is online\*
- All the comments you make on r/TheOwlHouse during periods when HootyBot is online\*
- The timestamp, url and id of the post/comments 
- Your username, if you create a post or comment

\*Caveat: I have been collecting random post and comment data during the first ~2-3 weeks of February 2022 to test my bot. I will delete this data after I'm confident that the live HootyBot generates enough data for me to troubleshoot without that preliminary pre-launch data. But again, I do not intend to distribute or sell this data to any third-party.

### Use of Data <a name = "2b"></a>
HootyBot scans the text data that it has collected for keywords. If it detects a pre-programmed keyword, it will reply to your message with a pre-programmed message of its own. 

## 3. Suggestions, Questions, Concerns, Comments? <a name = "3"></a>

Please fill out this form if you would like to suggest replies for HootyBot to make: [HootyBot Reply Suggestions](https://forms.gle/sjyffCsL2KYrsxJe8)

If you have a feature request, feel free to open an issue on this GitHub repository. Or if you're also knowledgable in programming, you can create a pull request. 

If you have any questions, feel free to send me a private message on Reddit: [u/zyxwvu28](https://www.reddit.com/user/zyxwvu28)

If you have any concerns, comments, compliments, insults, etc. fill out this form: [HootyBot Concerns and Comments](https://forms.gle/9QrHUuPSNuRChTMz9)

## 4. Future Plans for HootyBot <a name = "4"></a>

1. At the moment, HootyBot is incapable of advanced keyword searches (despite what the suggestion form implies). I intend to make that a feature in the near future.
2. I plan on injecting some of my own humour into this project and creating conversations that HootyBot can have with users. This will be a difficult task to program (so this will take longer). 
3. I will read all issues and pull requests for other feature requests. 
4. If there is enough demand, I may create more detailed documentation, or even a YouTube video detailing how I created HootyBot. But I will assume that most people who want to create their own TOH bot are skilled enough to read through my code and make one for themselves. If I'm wrong about this and you actually do want detailed documentation, or a YouTube tutorial, please let me know, the more people that want it, the more motivation I'll have to make it.

## 5. Version Logs <a name = "5"></a>
- v.1.0.1: 
    - HootyBot can do simple search queries to find posts/comments to respond to
- v.1.0.2: 
    - Changed the way data is input into HootyBot so that the entire system is more modular. 
    - Live changes to csvs now result in live changes to HootyBot's memory
- v1.0.3:
    - Added reply suggestions form to Hooty's reply ending
- v1.1.0 Beta:
    - Added advanced keyword searching functionality (currently being hosted on the advanced-word-search-parser branch of this repo)
- v1.1.1 Beta:
    - Added a minimum time between replies
- v1.1.2:
    - Subreddit mods and the bot creator now have remote access control over HootyBot via admin codes. Remote controls are limited to:
        - Pausing bot replies
        - Unpausing bot replies
        - And stopping the bot entirely
- v1.1.3:
    - Added ability for users to opt-out of receiving replies from HootyBot
- v1.1.4:
    - Fixed urls not showing up properly on old reddit. Shoutout to u/lurker_archon for identifying, and helping me fix this issue!
- v1.1.5:
    - Status message post now indicates the bot's reply delay
- v1.1.6:
    - Added probabilistic replies 
- v1.1.7:
    - Implemented a limiter for the bot replying to the same post multiple times
    - Bot is allowed to reply to a post 3 times before it gets rate limited
    - On it's 4th reply, it won't be allowed to reply to that post for 1 hour
    - Every subsequent reply doubles the delay
    - The "delay between replies" limiter overrules this limiter

HOOT HOOT!

![HootyBotProfilePic](https://user-images.githubusercontent.com/73264072/154608142-969ef356-1a2c-4fd8-b9bd-41ea4d9c431f.png)
