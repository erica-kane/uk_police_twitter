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
from sklearn.linear_model import LogisticRegression
import seaborn as sns
import matplotlib.pyplot as plt
import eli5

# Read the data 
all_tweets = pd.read_csv('pre_pro_tweets.csv')
all_tweets = all_tweets.drop(['Unnamed: 0'], axis=1)

# Unsplit tokenized column
def split_tweet(tweet):
    str_tweet = str(tweet)
    split_tweet = str_tweet.split('_!_')
    joined_tweet = ' '.join(split_tweet)
    return joined_tweet

all_tweets['pre_pro_tweet'] = all_tweets['new_token_tweet'].apply(split_tweet)

# Get tweets with labels only and drop 100 
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

# Make Naive Bayes model
vectorizer = TfidfVectorizer()
classifier_nb = MultinomialNB()
model_nb = make_pipeline(vectorizer, classifier_nb)
model_nb.fit(x_train, y_train)
predicted_categories_nb = model_nb.predict(x_test)
accuracy_score(y_test, predicted_categories_nb)

# Save test tweets for NB confusion matrix
test_with_base_nb = test[['base_text','tweet_class']]
test_with_base_nb['pred_class'] = predicted_categories_nb
test_with_base_nb.to_csv('nb_test_labels.csv')
# Save tweets which are classified incorrectly 
test_with_base_nb[test_with_base_nb['pred_class']!= test_with_base_nb['tweet_class']].to_csv('nb_incorrect_labels.csv')

# Logistic Regression 
classifier_logit = LogisticRegression()
model_logit = make_pipeline(vectorizer, classifier_logit)
model_logit.fit(x_train, y_train)
predicted_categories_logit = model_logit.predict(x_test)
accuracy_score(y_test, predicted_categories_logit)
eli5.show_weights(classifier_logit, vec=vectorizer, top=10)

# Save test tweets for NB confusion matrix
test_with_base_logit = test[['base_text','tweet_class']]
test_with_base_logit['pred_class'] = predicted_categories_logit
test_with_base_logit.to_csv('logit_test_labels.csv')
# Save tweets which are classified incorrectly 
test_with_base_logit[test_with_base_logit['pred_class']!= test_with_base_logit['tweet_class']].to_csv('logit_incorrect_labels.csv')




# SentenceTransformer - 84%
from sklearn.preprocessing import FunctionTransformer
from sentence_transformers import SentenceTransformer
senttrans = SentenceTransformer('all-MiniLM-L6-v2')
embedder = FunctionTransformer(lambda item: senttrans.encode(item, convert_to_numpy=True, show_progress_bar=False))
model_senttrans_logit = make_pipeline(embedder, LogisticRegression())
model_senttrans_logit.fit(list(x_train), y_train)
pred_cat_senttrans_logit = model_senttrans_logit.predict(list(x_test))
accuracy_score(y_test, pred_cat_senttrans_logit)

# XGBoost - 83%
from xgboost import XGBClassifier
embedder = FunctionTransformer(lambda item: senttrans.encode(item, convert_to_numpy=True, show_progress_bar=False))
model_senttrans_xgb = make_pipeline(embedder, XGBClassifier(objective='multi:softmax'))
model_senttrans_xgb.fit(list(x_train), (y_train - 1).astype(int))
pred_cat_senttrans_xgb = model_senttrans_xgb.predict(list(x_test))
accuracy_score((y_test - 1).astype(int), pred_cat_senttrans_xgb)

class_names = ['Providing information','Engagement', 'Intelligence gathering']
mat = confusion_matrix(y_test, predicted_categories)
sns.heatmap(mat.T, square = True, annot=True, fmt = "d", xticklabels = class_names, yticklabels = class_names)
plt.xlabel("true labels")
plt.ylabel("predicted label")
plt.show()




