import pandas as pd
import pyreadr
import numpy as np
import re
import nltk
from nltk.tokenize import TweetTokenizer

emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U0001F1F2-\U0001F1F4"  # Macau flag
        u"\U0001F1E6-\U0001F1FF"  # flags
        u"\U0001F600-\U0001F64F"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U0001F1F2"
        u"\U0001F1F4"
        u"\U0001F620"
        u"\u200d"
        u"\u2640-\u2642"
        "]+", flags=re.UNICODE)

tweets = pd.read_csv('tweets.csv')
tweets.head()

# Author IDs are 21857067 = GMP, 66967746 = MET, 23418457 = ASPolice
# 	20038272 = West Yorkshire, 18134929 = WM Police
tweets['police_force'] = tweets['author_id']
tweets['police_force'] = tweets['police_force'].replace([21857067, 66967746, 23418457, 20038272, 18134929], \
    ['GMP', 'MET', 'Avon and Somerset Police', 'West Yorkshire Police', 'West Midlands Police'])
tweets['police_force'].unique()

tweets = tweets.rename(columns={'created_at':'date', 'in_reply_to_user_id':'reply_id', 'id':'tweet_id'})


# Make 'type' retweet, tweet, or reply
    # new column 'type' - convert NaN to 'tweet'
    # Convert any value which isn't tweet to 'reply' UNLESS 
    # the value matches author ID - then it's 'tweet'
    # Convert any value which has an RT at the beginning of 'text
    # to RT

def tweet_type(row):
    if row['text'].startswith('RT'):
        return 'retweet'
    elif row['reply_id'] == row['author_id']:
        return 'tweet'
    elif not np.isnan(row['reply_id']):
        return 'reply'
    else:
        return 'tweet'
    
tweets['tweet_type'] = tweets.apply(tweet_type, axis=1)
    

# create base text column removing emojis and URL and 'RT' 

def create_base(string):
    if string.startswith('RT'):
        no_rt = string[3:]
        no_emoji = emoji_pattern.sub(r'', no_rt)
        no_url = re.sub(r'http\S+', '', no_emoji)
        return no_url
    else:
        no_emoji = emoji_pattern.sub(r'', string)
        no_url = re.sub(r'http\S+', '', no_emoji)
        return no_url

tweets['base_text'] = tweets['text'].apply(create_base)

# create tokens column by tokenizing base text, lower case (tweet sensitive)

tk = TweetTokenizer()

def token_tweet(string):
    lower_string = string.lower()
    token_string = tk.tokenize(lower_string)
    return token_string

tweets['token_tweet'] = tweets['base_text'].apply(token_tweet)

