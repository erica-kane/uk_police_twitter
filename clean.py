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
import demoji

all_tweets = pd.read_csv('tweets.csv')
all_tweets.head()

# Author IDs are 21857067 = GMP, 66967746 = MET, 23418457 = ASPolice
# 	20038272 = West Yorkshire, 18134929 = WM Police
all_tweets['police_force'] = all_tweets['author_id']
all_tweets['police_force'] = all_tweets['police_force'].replace([21857067, 66967746, 23418457, 20038272, 18134929], \
    ['GMP', 'MET', 'Avon and Somerset Police', 'West Yorkshire Police', 'West Midlands Police'])
all_tweets['police_force'].unique()

all_tweets = all_tweets.rename(columns={'created_at':'date', 'in_reply_to_user_id':'reply_id', 'id':'tweet_id'})


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
    
all_tweets['tweet_type'] = all_tweets.apply(tweet_type, axis=1)
    

# create base text column removing emojis and URL and 'RT' 

def create_base(string):
    if string.startswith('RT'):
        no_rt = string[3:]
        no_emoji = demoji.replace(no_rt)
        no_url = re.sub(r'http\S+', '', no_emoji)
        return no_url.strip()
    else:
        no_emoji = demoji.replace(string)
        no_url = re.sub(r'http\S+', '', no_emoji)
        return no_url.strip()

all_tweets['base_text'] = all_tweets['text'].apply(create_base)

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

all_tweets['token_tweet'] = all_tweets['base_text'].apply(token_tweet)

tweets = all_tweets[all_tweets.tweet_type != 'retweet'].reset_index(drop=True)

tweets.dropna(subset=["base_text"], inplace=True)

#tweets.to_csv('cleantweet.csv')

tweets.head()

# Deal with duplicate tweets 

# How many unique values are there 
# This tells us how many tweets are and aren't exact duplicates 
tweets['base_text'].duplicated().value_counts()

# Before classifying these duplicates it is useful to see how many times 
# they are duplicated 
# This line tells us how many times each tweet is tweeted and saves it as a dataframe
tweet_counts = pd.DataFrame(tweets['base_text'].value_counts())
# This line tells us how many times each number of duplications occurs 
# e.g. 563 tweets are duplicated once (i.e. exist twice)
tweet_counts[tweet_counts['base_text']>1].value_counts()

# Create a new dataset of just duplicated tweets 
all_dupes = tweets[tweets['base_text'].duplicated()]

# Save duplicated tweets as csv so you can hand code large chunks 
unique_dupes = pd.DataFrame(all_dupes['base_text'].unique())
unique_dupes['tweet_class'] = 0
unique_dupes = unique_dupes.rename(columns={0: "base_text"})
unique_dupes.to_csv('dupetweet.csv')

# Data has been manually edited outside of python and classes added

# Read data back in and match classification up to original data 
final_dupes = pd.read_csv('dupetweet_withclass.csv')
final_dupes = final_dupes.drop(['Unnamed: 0'], axis=1)
# Strip white space before and after a string 
def strip_tweet(value):
    return str(value).strip()
final_dupes['base_text'] = final_dupes['base_text'].apply(strip_tweet)

# Check for inconsistencies in how they have been read back in 
tweets['base_text'][147] == final_dupes['base_text'][1]
final_dupes['tweet_class'] = final_dupes['tweet_class'].replace(0, 1)
final_dupes['tweet_class'].value_counts()

# When joining back together, to check it has matched successfully check the amount of tweets 
# with a value other than 0 as their class matches the amount of duplicated tweets 
# Should be 5895
tweets.merge(final_dupes, left_on='base_text', right_on='base_text', how='left')









## Bokeh plot code


#from bokeh.plotting import figure, show, output_notebook
#from bokeh.transform import factor_cmap
#from bokeh.models import ColumnDataSource
#from bokeh.palettes import Spectral6
#output_notebook()

## Visualise these duplicated tweets 
#vectorizer = TfidfVectorizer()
#tfidf = vectorizer.fit_transform(dupe_tweets["base_text"])

#reducer = umap.UMAP(n_components=2, metric="hellinger")
#embeddings = reducer.fit_transform(tfidf)
#embeddings.shape

#datasource = ColumnDataSource({
    #"x": embeddings[:, 0],
    #"y": embeddings[:, 1],
    #'text': dupe_tweets["base_text"],
    #"force": dupe_tweets['police_force']
#})

#colours = factor_cmap('force', palette=Spectral6, factors=dupe_tweets['police_force'].unique()) 

#fig = figure(tooltips = [('Tweet', '@text')])
#fig.circle("x", "y", source=datasource, fill_color=colours, line_color=colours, legend_group="force")
#show(fig)