import pandas as pd
import pyreadr
import numpy as np
import re
import nltk
import string 
import spacy
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import confusion_matrix, accuracy_score
import seaborn as sns
import matplotlib.pyplot as plt

# Read the data 
all_tweets = pd.read_csv('analysis_tweets.csv')
all_tweets = all_tweets.drop(['Unnamed: 0'], axis=1)
tweets_with_labels = all_tweets[all_tweets['tweet_class']!= 0][all_tweets['tweet_form'] == 'non duplicate']
tweets_with_labels = tweets_with_labels[tweets_with_labels['tweet_class']!=100.0]

# Adjust so that the sample is less skewed to class 1
tweets_with_labels['tweet_class'].value_counts()
tweets_with_labels = tweets_with_labels.drop(tweets_with_labels[tweets_with_labels['tweet_class'] == 1.0].sample(n=3242).index)
tweets_with_labels = tweets_with_labels.drop(tweets_with_labels[tweets_with_labels['tweet_class'] == 3.0].sample(n=287).index)

# Train test split
train, test = train_test_split(tweets_with_labels)

# Create x and y 
# x is the features and y is the labels
# You need both features and labels for the training and testing to be separate 
x_train = train['base_text']
x_test = test['base_text']
y_train = train['tweet_class']
y_test = test['tweet_class']

# Make the model
model = make_pipeline(TfidfVectorizer(), MultinomialNB())
model.fit(x_train, y_train)
predicted_categories = model.predict(x_test)
accuracy_score(y_test, predicted_categories)

class_names = ['Providing information','Engagement', 'Intelligence gathering']

mat = confusion_matrix(y_test, predicted_categories)
sns.heatmap(mat.T, square = True, annot=True, fmt = "d", xticklabels = class_names, yticklabels = class_names)
plt.xlabel("true labels")
plt.ylabel("predicted label")
plt.show()

# Save test tweets 
test_with_base = test[['base_text','tweet_class']]
test_with_base['pred_class'] = predicted_categories
test_with_base.to_csv('test_labels.csv')
# Save tweets which are classified incorrectly 
test_with_base[test_with_base['pred_class']!= test_with_base['tweet_class']].to_csv('incorrect_labels.csv')













