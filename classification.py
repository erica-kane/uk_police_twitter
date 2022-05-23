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
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score
from sklearn.linear_model import LogisticRegression
import seaborn as sns
import matplotlib.pyplot as plt
import eli5
from sklearn.preprocessing import FunctionTransformer
from sentence_transformers import SentenceTransformer
from xgboost import XGBClassifier

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

# Create x without stop words
x_train_nsw = train['pre_pro_tweet']
x_test_nsw = test['pre_pro_tweet']

# Create y
y_train = train['tweet_class']
y_test = test['tweet_class']


# Logistic Regression - with tfidf (88 with stop words, 85 without)
classifier_logit = LogisticRegression()
model_logit = make_pipeline(vectorizer, classifier_logit)
model_logit.fit(x_train, y_train)
predicted_categories_logit = model_logit.predict(x_test)
accuracy_score(y_test, predicted_categories_logit)

# Save test tweets for logit confusion matrix
test_with_base_logit = test[['base_text','tweet_class']]
test_with_base_logit['pred_class'] = predicted_categories_logit
test_with_base_logit.to_csv('logit_test_labels.csv')
# Save tweets which are classified incorrectly 
test_with_base_logit[test_with_base_logit['pred_class']!= test_with_base_logit['tweet_class']].to_csv('logit_incorrect_labels.csv')


# Naive Bayes model - with tfidf (85 with stop words, 85 without)
vectorizer = TfidfVectorizer()
classifier_nb = MultinomialNB()
model_nb = make_pipeline(vectorizer, classifier_nb)
model_nb.fit(x_train, y_train)
predicted_categories_nb = model_nb.predict(x_test)
accuracy_score(y_test, predicted_categories_nb)
precision_score(y_test, predicted_categories_nb, average='macro')
recall_score(y_test, predicted_categories_nb, average='macro')


# Logistic regression - with embeddings (85 with stop words, 84 without)
senttrans = SentenceTransformer('all-MiniLM-L6-v2')
embedder = FunctionTransformer(lambda item: senttrans.encode(item, convert_to_numpy=True, show_progress_bar=False))
model_senttrans_logit = make_pipeline(embedder, LogisticRegression())
model_senttrans_logit.fit(list(x_train), y_train)
pred_cat_senttrans_logit = model_senttrans_logit.predict(list(x_test))
accuracy_score(y_test, pred_cat_senttrans_logit)

# XGBoost - with embeddings (85 with stop words, 84 without)
embedder = FunctionTransformer(lambda item: senttrans.encode(item, convert_to_numpy=True, show_progress_bar=False))
model_senttrans_xgb = make_pipeline(embedder, XGBClassifier(objective='multi:softmax'))
model_senttrans_xgb.fit(list(x_train), (y_train - 1).astype(int))
pred_cat_senttrans_xgb = model_senttrans_xgb.predict(list(x_test))
accuracy_score((y_test - 1).astype(int), pred_cat_senttrans_xgb)


# Optional plotting 
class_names = ['Providing information','Engagement', 'Intelligence gathering']
mat = confusion_matrix(y_test, predicted_categories)
sns.heatmap(mat.T, square = True, annot=True, fmt = "d", xticklabels = class_names, yticklabels = class_names)
plt.xlabel("true labels")
plt.ylabel("predicted label")
plt.show()


# Classify and save entire dataset - regression with tf-idf
tweets_without_labels = all_tweets[all_tweets['tweet_class']== 0]
tweets_without_labels["tweet_class"] = model_logit.predict(tweets_without_labels['base_text'])

final_tweets = all_tweets.copy()
final_tweets.update(tweets_without_labels["tweet_class"])
final_tweets['tweet_class'].value_counts()

final_tweets[final_tweets['tweet_class']!=100.0].to_csv('final_tweets.csv')
