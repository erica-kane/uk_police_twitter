import pandas as pd
import pyreadr
import numpy as np
import re
import nltk
import string 
import spacy
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer

# Read the data 
all_tweets = pd.read_csv('practice_tweets.csv')
all_tweets = all_tweets.drop(['Unnamed: 0'], axis=1)
tweets_with_labels = all_tweets[all_tweets['tweet_class']!= 0 ]

# Train test split
train, test = train_test_split(tweets_with_labels)

# Create x and y 
# x is the features and y is the labels
# You need both features and labels for the training and testing to be separate 
x_train = pd.DataFrame(train['base_text'])
x_test = pd.DataFrame(test['base_text'])
y_train = pd.DataFrame(train['tweet_class'])
y_test = pd.DataFrame(test['tweet_class'])









