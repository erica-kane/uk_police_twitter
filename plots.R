library(dplyr)
library(readr)
library(ggplot2)
library(tidytext)
library(purrr)
library(data.table)
library(tidyr)
library(stringr)
library(tokenizers)
library(tidytext)
library(qdap)
library(spacyr)
library(tm)
library(textstem)
library(lubridate, warn.conflicts = FALSE)
library(gdata)
library(wordcloud)

plot_tweets = read_csv('pre_pro_tweets.csv')
plot_tweets = select(plot_tweets, -'X1')

plot_tweets = plot_tweets[plot_tweets$tweet_class > 0, ] 
plot_tweets = plot_tweets[plot_tweets$tweet_class < 100, ] 
plot_tweets$tweet_class = as.factor(plot_tweets$tweet_class)
plot_tweets$date = as.Date(plot_tweets$date)

# Rename classes
plot_tweets$tweet_class = recode(plot_tweets$tweet_class, '1' = "Pushing information", '2' = "Engagement", '3' = "Intelligence gathering")

# Split token string 
split_tokens = function(tweet) {
  token_tweet = str_split(tweet, '_!_')[[1]]
  return(token_tweet)
}
plot_tweets$token_tweet_list = lapply(plot_tweets$new_token_tweet, split_tokens)

# Plot for Class per force 
ggplot(plot_tweets, aes(police_force)) + 
  geom_bar(stat = 'count', aes(fill = tweet_class), position = 'fill', color = 'grey') +
  scale_fill_brewer(name = 'Tweet class') +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, vjust = 0.65)) +
  labs(x = 'Police force', y = 'Percentage relative to force count') 


# Plots for use of classes per force over time 
# Line graph per week
plot_tweets %>%
  mutate(week=floor_date(date, unit="week")) %>%
  group_by(week, police_force, tweet_class) %>%
  summarise(Count = n()) %>%
  ggplot(aes(x = week, y = Count, color = tweet_class)) +
  scale_color_manual(values=c("lightskyblue1", 'blue4',"dodgerblue1")) +
  geom_line(size = 0.3) + 
  facet_wrap(~ police_force, ncol = 1, scales="free") +
  labs(x = 'Date', y = 'Tweet count (aggregated by week)', title = 'Police force tweet frequency per class', color = 'Tweet class') +
  theme_minimal()

# Line graph per month
plot_tweets %>%
  mutate(month=floor_date(date, unit="month")) %>%
  group_by(month, police_force, tweet_class) %>%
  summarise(Count = n()) %>%
  ggplot(aes(x = month, y = Count, color = tweet_class)) +
  scale_color_manual(values=c("dodgerblue1", 'gold', 'firebrick1')) +
  geom_line(size = 0.3) + 
  facet_wrap(~ police_force, ncol = 1, scales="free") +
  labs(x = 'Date', y = 'Tweet count (aggregated by month)', title = 'The use of classes per police force over time', color = 'Tweet class') +
  theme_minimal()

# Language per class 
plot_tweets%>%
  #sample_n(500) %>%
  unnest_longer(token_tweet_list) %>%
  group_by(police_force, tweet_class) %>%
  count(token_tweet_list, sort=TRUE) %>%
  slice_max(n, n=20) %>%
  ggplot(aes(token_tweet_list, n)) +
  facet_wrap(~police_force + tweet_class, scales="free") +
  geom_col(fill = "gray80", colour='black', size = 0.3) +
  xlab(NULL) +
  coord_flip() + 
  theme_minimal() +
  labs(x = 'Words', y = 'Word frequency', title = 'Word frequencies in USA and UK police force
tweets and replies')

# TF IDF

# Replies per force (class of replies)
plot_tweets %>%
  filter(tweet_type == 'reply') %>%
  ggplot(aes(x = police_force)) +
  geom_bar(stat = 'count', fill = 'skyblue', color = 'grey') +
  geom_text(stat='count', aes(label=..count..), vjust=1.6, color = 'white') +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, vjust = 0.65)) +
  labs(x = 'Police force', y = 'Number of replies') 

plot_tweets %>%
  filter(tweet_type == 'reply') %>%
  ggplot(aes(police_force)) + 
  geom_bar(stat = 'count', aes(fill = tweet_class), position = 'fill', color = 'grey') +
  scale_fill_brewer(name = 'Tweet class') +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, vjust = 0.65)) +
  labs(x = 'Police force', y = 'Percentage of replies') 

# Common # and @ per force
## Function to get non # words as NA
get_hash = function(word) {
 if (startsWith(word, '#') != TRUE) {
    return(NA) 
 } else {
   return(word)
 }
}

## Function to get non @ words as NA
get_mention = function(word) {
  if (startsWith(word, '@') != TRUE) {
    return(NA) 
  } else {
    return(word)
  }
}

## New data 
subset_tweets = plot_tweets %>%
  sample_n(500) %>%
  unnest_longer(token_tweet_list) %>%
  group_by(police_force, tweet_class) %>%
  count(token_tweet_list, sort=TRUE)

## Apply functions
subset_tweets$hashtags = lapply(subset_tweets$token_tweet_list, get_hash)
subset_tweets$mention = lapply(subset_tweets$token_tweet_list, get_mention)

## Plot # word cloud 
subset_tweets %>% 
  mutate(hashtags = sapply(hashtags, toString)) %>%
  mutate(hashtags = na_if(hashtags, "NA")) %>%
  drop_na() %>%
  slice_max(n, n=20) %>%

## Plot @ word cloud 
subset_tweets %>% 
  mutate(mention = sapply(mention, toString)) %>%
  mutate(mention = na_if(mention, "NA")) %>%
  drop_na() 


# Sentiment per force/class
ggplot(data = plot_tweets, aes(x = sentiment_value, fill = sentiment_label)) + 
  geom_histogram(aes(y = stat(density)), bins = 5, alpha = 0.8) + 
  facet_wrap(~ police_force, ncol = 1, scales="free") +
  scale_fill_manual(values = c("firebrick2", 'gold1', 'green3')) +
  labs(x = 'Sentiment score', y = 'Number of tweets', fill = 'Sentiment value') +
  theme_minimal()

# Engagement per force and category (retweet, like, quote)


# Heat map



