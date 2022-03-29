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

# Split into 4 datasets for police forces 
wyp_labels = tweets_with_labels[tweets_with_labels['police_force'] == 'West Yorkshire Police']
asp_labels = tweets_with_labels[tweets_with_labels['police_force'] == 'Avon and Somerset Police']
wmp_labels = tweets_with_labels[tweets_with_labels['police_force'] == 'West Midlands Police']
met_labels = tweets_with_labels[tweets_with_labels['police_force'] == 'MET']
gmp_labels = tweets_with_labels[tweets_with_labels['police_force'] == 'GMP']

# Train test split
train_wyp, test_wyp = train_test_split(wyp_labels)
train_asp, test_asp = train_test_split(asp_labels)
train_wmp, test_wmp = train_test_split(wmp_labels)
train_met, test_met = train_test_split(met_labels)
train_gmp, test_gmp = train_test_split(gmp_labels)

# Create x and y 
# x is the features and y is the labels
# You need both features and labels for the training and testing to be separate 
x_train_wyp = train_wyp['base_text']
x_test_wyp = test_wyp['base_text']
y_train_wyp = train_wyp['tweet_class']
y_test_wyp = test_wyp['tweet_class']

x_train_asp = train_asp['base_text']
x_test_asp = test_asp['base_text']
y_train_asp = train_asp['tweet_class']
y_test_asp = test_asp['tweet_class']

x_train_wmp = train_wmp['base_text']
x_test_wmp = test_wmp['base_text']
y_train_wmp = train_wmp['tweet_class']
y_test_wmp = test_wmp['tweet_class']

x_train_met = train_met['base_text']
x_test_met = test_met['base_text']
y_train_met = train_met['tweet_class']
y_test_met = test_met['tweet_class']

x_train_gmp = train_gmp['base_text']
x_test_gmp = test_gmp['base_text']
y_train_gmp = train_gmp['tweet_class']
y_test_gmp = test_gmp['tweet_class']

# Make the model
model_wyp = make_pipeline(TfidfVectorizer(), MultinomialNB())
model_wyp.fit(x_train_wyp, y_train_wyp)
predicted_categories_wyp = model_wyp.predict(x_test_wyp)
accuracy_score(y_test_wyp, predicted_categories_wyp)

model_asp = make_pipeline(TfidfVectorizer(), MultinomialNB())
model_asp.fit(x_train_asp, y_train_asp)
predicted_categories_asp = model_asp.predict(x_test_asp)
accuracy_score(y_test_asp, predicted_categories_asp)

model_wmp = make_pipeline(TfidfVectorizer(), MultinomialNB())
model_wmp.fit(x_train_wmp, y_train_wmp)
predicted_categories_wmp = model_wmp.predict(x_test_wmp)
accuracy_score(y_test_wmp, predicted_categories_wmp)

model_met = make_pipeline(TfidfVectorizer(), MultinomialNB())
model_met.fit(x_train_met, y_train_met)
predicted_categories_met = model_met.predict(x_test_met)
accuracy_score(y_test_met, predicted_categories_met)

model_gmp = make_pipeline(TfidfVectorizer(), MultinomialNB())
model_gmp.fit(x_train_gmp, y_train_gmp)
predicted_categories_gmp = model_gmp.predict(x_test_gmp)
accuracy_score(y_test_gmp, predicted_categories_gmp)

class_names = ['Providing information','Engagement', 'Intelligence gathering']

mat = confusion_matrix(y_test_wyp, predicted_categories_wyp)
sns.heatmap(mat.T, square = True, annot=True, fmt = "d", xticklabels = class_names, yticklabels = class_names)
plt.xlabel("true labels")
plt.ylabel("predicted label")
plt.show()

# First drop tweets with 100, then create 5 separate classifiers per force
# Makes more sense to classify based on similar styles 

test_with_base = test[['base_text','tweet_class']]
test_with_base['pred_class'] = predicted_categories
test_with_base[test_with_base['pred_class']!= test_with_base['tweet_class']]













