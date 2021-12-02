import pandas as pd
import pyreadr
import numpy as np

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
# create tokens column by tokenizing base text, lower case (tweet sensitive)


