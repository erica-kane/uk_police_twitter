import pandas as pd
import nltk
from nltk.tokenize import TweetTokenizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string 
nltk.download('stopwords')

tweets = pd.read_csv('analysis_tweets.csv', index_col=0)

# redo token_tweet column
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

# lower case 
# tokenizing 
# stop word removal
# punctuation removal 
# stem 
# lemma

# lemma and stem 

# join string back together with '_new_token_'

# sentiment 
