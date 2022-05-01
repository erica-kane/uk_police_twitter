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

blacklist = c("bristol", 'somerset', 'avon', 'bath', 'west yorkshire',"leeds")

# TF IDF
plot_tweets %>%
  # sample_n(100) %>%
  select(police_force, tweet_class, token_tweet_list) %>%
  unnest_longer(token_tweet_list) %>%
  filter(!startsWith(token_tweet_list, '#')) %>%
  filter(!startsWith(token_tweet_list, '@')) %>%
  filter(!token_tweet_list %in% blacklist) %>%
  count(police_force, tweet_class, token_tweet_list, sort=TRUE) %>%
  unite("force_class", police_force, tweet_class) %>%
  bind_tf_idf(token_tweet_list, force_class, n) %>%
  separate(force_class, c("police_force", "tweet_class"), sep="_") %>%
  group_by(police_force, tweet_class) %>%
  slice_max(tf_idf, n=10, with_ties=FALSE) %>%
  ggplot(aes(x = reorder(token_tweet_list, n), y = n, fill = police_force)) +
  facet_wrap(~police_force + tweet_class, scales="free") +
  scale_fill_manual(values = c('cadetblue3', 'blue', 'deepskyblue', 'dodgerblue', 'dodgerblue4')) +
  geom_col(colour='black', size = 0.3, alpha = 0.5) +
  xlab(NULL) +
  coord_flip() + 
  theme_minimal() +
  theme(legend.position = "none") +
  labs(x = 'Words with highest TF-IDF', y = 'Word frequency') 

# Replies per force (class of replies)
plot_tweets %>%
  filter(tweet_type == 'reply') %>%
  ggplot(aes(x = police_force)) +
  geom_bar(stat = 'count', fill = 'skyblue', color = 'grey') +
  geom_text(stat='count', aes(label=..count..), vjust=-0.5, color = 'grey') +
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

# Common # per force
plot_tweets %>%
  #sample_n(500) %>%
  unnest_longer(token_tweet_list) %>%
  group_by(police_force) %>%
  count(token_tweet_list, sort=TRUE) %>%
  filter(startsWith(token_tweet_list, '#')) %>%
  slice_max(n, n=20, with_ties=FALSE) %>%
  ggplot(aes(x = reorder(token_tweet_list, n), y = n, fill = police_force)) +
  facet_wrap(~police_force, scales="free") +
  scale_fill_manual(values = c('cadetblue3', 'blue', 'deepskyblue', 'dodgerblue', 'dodgerblue4')) +
  geom_col(colour='black', size = 0.3, alpha = 0.7) +
  xlab(NULL) +
  coord_flip() + 
  theme_minimal() +
  theme(legend.position = "none") +
  labs(x = 'Hashtags', y = 'Word frequency')

# Common @ per force
plot_tweets %>%
  #sample_n(500) %>%
  unnest_longer(token_tweet_list) %>%
  group_by(police_force) %>%
  count(token_tweet_list, sort=TRUE) %>%
  filter(startsWith(token_tweet_list, '@')) %>%
  slice_max(n, n=20, with_ties=FALSE) %>%
  ggplot(aes(x = reorder(token_tweet_list, n), y = n, fill = police_force)) +
  facet_wrap(~police_force, scales="free") +
  scale_fill_manual(values = c('cadetblue3', 'blue', 'deepskyblue', 'dodgerblue', 'dodgerblue4')) +
  geom_col(colour='black', size = 0.3, alpha = 0.7) +
  xlab(NULL) +
  coord_flip() + 
  theme_minimal() +
  theme(legend.position = "none") +
  labs(x = 'Mentions', y = 'Word frequency')

# Sentiment per force/class
ggplot(data = plot_tweets, aes(x = sentiment_value, fill = sentiment_label)) + 
  geom_histogram(aes(y = stat(density)), bins = 5, alpha = 0.7) + 
  facet_wrap(~ police_force, ncol = 1, scales="free") +
  scale_fill_manual(values = c("firebrick2", 'gold1', 'green3')) +
  labs(x = 'Sentiment score', y = 'Number of tweets', fill = 'Sentiment value') +
  theme_minimal()

# Engagement per force and category (retweet, like, quote)
plot_tweets %>%
  select(retweet_count, reply_count, like_count, quote_count, police_force, tweet_class) %>%
  pivot_longer(cols = retweet_count:quote_count) %>%
  group_by(police_force, tweet_class, name) %>%
  summarise(frequency = sum(value)) %>%
  mutate(frequency = frequency/sum(frequency)*100) %>%
  ggplot(aes(fill = name, x = police_force, y = frequency)) +
  geom_bar(position = 'dodge', stat = 'identity', alpha = 0.8) +
  facet_wrap(~ tweet_class, ncol = 1) +
  theme_minimal() +
  scale_fill_manual(values = c('skyblue1', 'blue', 'deepskyblue', 'dodgerblue'), labels = c('Likes', 'Quotes', 'Replies', 'Retweets'))+
  labs(x = 'Police force', y = 'Frequency of tweets', fill = 'Tweet metric') +
  ylim(0, 100)

# Confusion matrix - Naive Bayes
test_labels_nb = read_csv('nb_test_labels.csv')
test_labels_nb = select(test_labels_nb, -'X1')

test_labels_nb %>%
  select(tweet_class, pred_class) %>%
  count(tweet_class, pred_class) %>%
  ggplot(aes(factor(tweet_class), factor(pred_class), fill = n)) +
  geom_tile(color = "white", lwd = 0.2, linetype = 1) +
  scale_fill_gradient(low = "skyblue1", high = "blue4") +
  geom_text(aes(label = n), colour = "white") +
  theme_minimal()+
  theme(legend.position = "none", axis.text.y = element_text(angle = 90, hjust = 0.5)) +
  labs(x = '\nTweet class', y = 'Predicted class\n') + 
  scale_x_discrete(labels=c('1' = "Providing information", "2" = "Engagement", "3" = "Intelligence gathering")) +
  scale_y_discrete(labels=c('1' = "Providing information", "2" = "Engagement", "3" = "Intelligence gathering")) 

# Confusion matrix - Logit
test_labels_logit = read_csv('logit_test_labels.csv')
test_labels_logit = select(test_labels_logit, -'X1')

test_labels_logit %>%
  select(tweet_class, pred_class) %>%
  count(tweet_class, pred_class) %>%
  ggplot(aes(factor(tweet_class), factor(pred_class), fill = n)) +
  geom_tile(color = "white", lwd = 0.2, linetype = 1) +
  scale_fill_gradient(low = "skyblue1", high = "blue4") +
  geom_text(aes(label = n), colour = "white") +
  theme_minimal()+
  theme(legend.position = "none", axis.text.y = element_text(angle = 90, hjust = 0.5)) +
  labs(x = '\nTweet class', y = 'Predicted class\n') + 
  scale_x_discrete(labels=c('1' = "Providing information", "2" = "Engagement", "3" = "Intelligence gathering")) +
  scale_y_discrete(labels=c('1' = "Providing information", "2" = "Engagement", "3" = "Intelligence gathering")) 



