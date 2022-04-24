import pandas as pd
import spacy
from spacytextblob.spacytextblob import SpacyTextBlob
import re
import random

tweets = pd.read_csv('analysis_tweets.csv', index_col=0)

nlp = spacy.load("en_core_web_md")
nlp.add_pipe("merge_entities")
nlp.add_pipe('spacytextblob')
nlp.tokenizer.token_match = re.compile("^#\w+$").match

black_list = set(['|'])

def clean_tweet(tweet):
    cleaned_tokens = []
    doc = nlp(tweet)
    for x in doc:
        if not x.is_stop and not x.is_space and not x.is_punct and x.text not in black_list:
            cleaned = x.lemma_.lower()
            cleaned_tokens.append(cleaned)
    return cleaned_tokens

def prep_tweet(tweet):
    cleaned = clean_tweet(tweet)
    joined = "_!_".join(cleaned)
    return joined

tweets["new_token_tweet"] = tweets["base_text"].apply(prep_tweet)

# sentiment 
from transformers import pipeline
sentiment_pipeline = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")

data = list(tweets['base_text'])
sentiment_scores = sentiment_pipeline(data)

# Create sentiment label 
sentiment_labels = []

for value in sentiment_scores:
    sentiment_labels.append(value.get('label'))

tweets['sentiment_label'] = sentiment_labels

# Create sentiment score 
sentiment_score = []

for value in sentiment_scores:
    sentiment_score.append(value.get('score'))

tweets['sentiment_score'] = sentiment_score

# Make new variable with edited sentiment score
def get_sent_score(row):
    sen_lab = row['sentiment_label']
    if  sen_lab == 'Positive':
        return row['sentiment_score']
    elif sen_lab == 'Neutral':
        return 0
    elif sen_lab == 'Negative':
        return row['sentiment_score']*-1

tweets['sentiment_value'] = tweets.apply(get_sent_score, axis=1)

# Save data for classification
tweets.to_csv('pre_pro_tweets.csv')

tweets