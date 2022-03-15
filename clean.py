import pandas as pd
import pyreadr
import numpy as np
import re
import nltk
import demoji
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
import string 
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
import umap

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

#tweets.to_csv('plot_tweets.csv')

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
tweets['base_text'][91] == final_dupes['base_text'][1]
final_dupes['tweet_class'].value_counts()

# When joining back together, to check it has matched successfully check the amount of tweets 
# with a value other than 0 as their class matches the amount of duplicated tweets 
# Should be 7548
cls_twt = tweets.merge(final_dupes, left_on='base_text', right_on='base_text', how='left')
(cls_twt['tweet_class'].fillna(0)).value_counts()

# It doesn't add to 7548, adds to 7438. Check below by making new dataset with only values not 
# equal to 0 
cls_twt_dupe = (cls_twt[(cls_twt['tweet_class'].fillna(0))!= 0])
len(cls_twt_dupe)
# Values which are duplicated are more than values equal to 0 
# Duplicted tweets in the original data match duplicated in the new data, but 
# tweets with class != 0 do not equate to that amount
len(tweets['base_text'][tweets['base_text'].duplicated(keep=False)])
len(cls_twt['base_text'][cls_twt['base_text'].duplicated(keep=False)])
len(cls_twt_dupe)
# Look at these tweets which are duplicated but do not have classes
# Make data frame of the base text of all tweets which are class not 0 from their
cls_twt_dupe1 = pd.DataFrame(cls_twt_dupe['base_text'])
# Make data frame of the base text of all tweets which are duplicated 
cls_twt_dupe2 = pd.DataFrame(cls_twt['base_text'][cls_twt['base_text'].duplicated(keep=False)])
# reset index so the index value is it's own column
cls_twt_dupe1.reset_index(level=0, inplace=True)
cls_twt_dupe2.reset_index(level=0, inplace=True)
# Save differences in indexes to a new list object
indexes = list(set(cls_twt_dupe2['index'].tolist()) - set(cls_twt_dupe1['index'].tolist()))
# Use list object to index on data and look at the tweets which are duplicated but don't have a class
hell_twts = (cls_twt.loc[indexes, ['base_text']])
# How many of these tweets are unique?
len(hell_twts['base_text'].unique())

# Code the duplicate tweets that don't have a class
# Change blanks to 100
for value in indexes:
    if cls_twt['base_text'][value] == '':
        cls_twt['tweet_class'][value] = 100

for value in indexes:
    if cls_twt['base_text'][value] == 'Three simple actions we must all do to keep on protecting each other \n￼\n Keep washing your hands regularly\n￼\n Wear a face covering in enclosed spaces\n￼\n Stay at least 2 metres apart\n\nKeep up to date with the guidance:' or cls_twt['base_text'][value] == 'There are simple but effective ways in which we can all help prevent the spread of coronavirus:\n￼Wash your hands\nWear a face covering\n￼Make space\nMore info here: \n#HandsFaceSpace #SafeGM' or cls_twt['base_text'][value] == 'There are simple but effective ways we can all help prevent the spread of coronavirus:\n\n Wash your hands\n￼\n Wear a face covering\n￼\n Make space\n\nMore info here: \n\n#HandsFaceSpace #SafeGM' or cls_twt['base_text'][value] == 'There are simple but effective ways in which we can all help prevent the spread of coronavirus:\n￼Wash your hands\n￼Wear a face covering\n￼Make space\nMore info here: \n#HandsFaceSpace #SafeGM':
        cls_twt['tweet_class'][value] = 1.0
    
cls_twt['tweet_class'].value_counts(dropna=False)
# Now it adds to 7548

# Drop any row with empty string in base text 
cls_twt = cls_twt[cls_twt.base_text != '']
cls_twt = cls_twt[cls_twt.tweet_class != 100.0]

# Drop any rows in which base_text is just words with @ at the start 
def drop_mention(base_text):
    word_list = []
    for word in base_text.split():
        if not word.startswith('@'):
            word_list.append(word)
    if not word_list:
        return False
    else:
        return True

cls_twt = cls_twt[cls_twt["base_text"].apply(drop_mention)]
cls_twt['tweet_class'] = cls_twt['tweet_class'].fillna(0)

# Save data to trial naive bayes model 
#cls_twt.to_csv('practice_tweets.csv')

# See how many tweets are from each force in non-labelled tweets 
((cls_twt[cls_twt['tweet_class'] == 0.0])['police_force'].value_counts(normalize=True)*100).round(2)
# you want 1/4 of the unlabelled tweets to label, which is 25% of 35709
(35709/100)*25
# 8927 tweets to label of which 
# 22% West Midlands Police - 1964
# 21% GMP - 1875
# 20% Avon and Somerset Police - 1785
# 19% MET - 1696
# 18% West Yorkshire Police - 1607

# Create the data set 
no_cls = cls_twt[cls_twt['tweet_class'] == 0.0]

wmp = no_cls[no_cls['police_force']== 'West Midlands Police'].sample(n=1964, random_state=1)
gmp = no_cls[no_cls['police_force']== 'GMP'].sample(n=1875, random_state=1)
asp = no_cls[no_cls['police_force']== 'Avon and Somerset Police'].sample(n=1785, random_state=1)
met = no_cls[no_cls['police_force']== 'MET'].sample(n=1696, random_state=1)
wyp = no_cls[no_cls['police_force']== 'West Yorkshire Police'].sample(n=1607, random_state=1)

unlabeled = pd.concat([wmp, gmp, asp, met, wyp])

unlabeled[['base_text', 'tweet_class']].to_csv('unlabeled_training.csv')

# Example of how git works 


# cls_twt is full data with duplicates labelled 
# no_cls is just non duplicate tweets (i.e. those without classes)
# Unlabelled is a sample of the non duplicate tweets to be hand classified
# after you label you can read back in labeled, this is test/training set
# Then index no_cls on the labelled tweets and save everything that's ublabeled 
# These 2 new data sets should add to 35709

# Once the data is all classfied it can be joined back with the duplicate tweets 