import pandas as pd
import pyreadr
import numpy as np
import re
import nltk
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
import string 
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
import umap

from bokeh.plotting import figure, show, output_notebook
from bokeh.models import ColumnDataSource
from bokeh.transform import factor_cmap
from bokeh.palettes import Spectral6
output_notebook()

emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  
        u"\U0001F300-\U0001F5FF"  
        u"\U0001F680-\U0001F6FF"  
        u"\U0001F1E0-\U0001F1FF"  
        u"\U0001F1F2-\U0001F1F4"  
        u"\U0001F1E6-\U0001F1FF"  
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

# create tokens column by tokenizing base text, lower case (tweet sensitive), remove stop words and punctuation

tk = TweetTokenizer()
stopword_set = set(stopwords.words('english'))
punctuation_set = set(string.punctuation)

def token_tweet(string):
    lower_string = string.lower()
    token_string = tk.tokenize(lower_string)
    token_string_without_sw = [word for word in token_string if not word in stopword_set]
    token_string_without_punc = [word for word in token_string_without_sw if not word in punctuation_set]
    return token_string_without_punc

tweets['token_tweet'] = tweets['base_text'].apply(token_tweet)

nort = tweets[tweets.tweet_type != 'retweet'].reset_index(drop=True)

nort.dropna(subset=["base_text"], inplace=True)

#nort.to_csv('cleantweet.csv')

nort.head()

# Deal with duplicate tweets 

# How many unique values are there 
# This tells us how many tweets are and aren't exact duplicates 
nort['base_text'].duplicated().value_counts()

# Before classifying these duplicates it is useful to see how many times 
# they are duplicated 
# This line tells us how many times each tweet is tweeted and saves it as a dataframe
duplicates = pd.DataFrame(nort['base_text'].value_counts())
# This line tells us how many times each number of duplications occurs 
# e.g. 563 tweets are duplicated once (i.e. exist twice)
duplicates[duplicates['base_text']>1].value_counts()

# Create a new dataset of just duplicated tweets 
dupe_tweets = nort[nort['base_text'].duplicated()]


# Visualise these duplicated tweets 
vectorizer = TfidfVectorizer()
tfidf = vectorizer.fit_transform(dupe_tweets["base_text"])

reducer = umap.UMAP(n_components=2, metric="hellinger")
embeddings = reducer.fit_transform(tfidf)
embeddings.shape

datasource = ColumnDataSource({
    "x": embeddings[:, 0],
    "y": embeddings[:, 1],
    'text': dupe_tweets["base_text"],
    "force": dupe_tweets['police_force']
})

colours = factor_cmap('force', palette=Spectral6, factors=dupe_tweets['police_force'].unique()) 

fig = figure(tooltips = [('Tweet', '@text')])
fig.circle("x", "y", source=datasource, fill_color=colours, line_color=colours, legend_group="force")
show(fig)


# Save duplicated tweets as csv so you can hand code large chunks 
single_dupe_tweets = pd.DataFrame(dupe_tweets['base_text'].unique())
single_dupe_tweets['tweet_class'] = 0
single_dupe_tweets = single_dupe_tweets.rename(columns={0: "base_text"})
single_dupe_tweets.to_csv('dupetweet.csv')

# Read data back in and match classification up to original data 

dupe_tweets_class = pd.read_csv('dupetweet_withclass.csv')
dupe_tweets_class = dupe_tweets_class.drop(['Unnamed: 0'], axis=1)

# Check for inconsistencies in how they have been read back in 
dupe_tweets_class['base_text'][1]
nort['base_text'][147]
# Reading back in has removed leading white spaces - you can remove these 
nort['base_text'][147].lstrip() == dupe_tweets_class['base_text'][1].lstrip()

# When joining back together, to check it has matched successfully check the amount of tweets 
# with a value other than 0 as their class matches the amount of duplicated tweets 
# Should be 5750


#sampletweet = nort.sample(n=100)
#sampletweet.to_csv('sampletweet.csv')


