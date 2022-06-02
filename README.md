# uk_police_twitter

## Introuction

This repository contains the code used for data extraction, cleaning, classification, analysis, and plotting. The data files are also contained in the repository.

## Files and data 

Files are run in a linear manner as outlined below:

- [collection.R](collection.R) - this R script extracts the data through Twitter's API and produces
    - [tweets.rds](tweets.rds)
    - [tweets.csv](tweets.csv)
- [clean.py](clean.py) - this Python script deals with URLs and emojis, adding tweet_type and tweet_form. It produces
    - [plot_tweets.csv](plot_tweets.csv) - this data file contains all tweets with extra variables (tweet type)
    - [total_tweet_plot.R](total_tweet_plot.R)- this R script uses plot_tweets.csv to look at tweet counts per force and type
    - [dupetweet.csv](dupetweet.csv) - unique duplicate tweets 
    - [dupetweet_withclass.csv](dupetweet_withclass.csv) - unique duplicated tweets with class 
    - [unlabeled_training.csv](unlabeled_training.csv) - test and training data
    - [labeled_training.csv](labeled_training.csv) - test and training data with class
    - [analysis_tweets.csv](analysis_tweets.csv) - labelled and unlabelled data joined 
- [text_pre_pro.py](text_pre_pro.py) - this Python script tokenizes, removes stop words, and lemmatizes tweets
    - [pre_pro_tweets.csv](pre_pro_tweets.csv) - all tweets with pre processing 
- [classification.py](classification.py) - this Python script runs all classifiers and computes their accuracy scores
    - [logit_incorrect_labels.csv](logit_incorrect_labels.csv) - incorrectly classified tweets 
    - [logit_test_labels](logit_test_labels) - test data with labels to plot confusion matrix
    - [final_tweets.csv](final_tweets.csv) - all tweets with labels (hand labelled and from classifier)
- [plots.R](plots.R) - R script to create all figures, tables, and graphs 


Click [here](https://github.com/erica-kane/uk_police_twitter) to return to the repository.
