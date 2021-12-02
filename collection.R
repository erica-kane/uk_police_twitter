library(academictwitteR)

# US tweets from 26 May - 31 August
#get_all_tweets(
#  users = c("metpoliceuk", "gmpolice", "ASPolice", "WestYorksPolice", 'WMPolice'),
#  start_tweets = "2019-01-01T00:00:00Z",
#  end_tweets = "2021-11-01T00:00:00Z",
#  file = "tweets.rds",
#  n = 100000)

all_tweets <- readRDS('tweets.rds')

all_tweets2 = all_tweets %>% 
  bind_cols(all_tweets$public_metrics %>% 
              as_tibble)

all_tweets3 = all_tweets2 %>%
  bind_cols(all_tweets2$entities %>%
              as_tibble)

tweets = all_tweets3[, c('id', 'author_id', 'created_at', 'text', 'in_reply_to_user_id', 
                         'retweet_count', 'reply_count', 'like_count', 'quote_count')]

# 'mentions', 'hashtags', 'urls' were going to be extracted but it didn't work
# tweets$mentions[[1]][[3]]
# tweets$hashtags[[2]][[3]]

write_csv(tweets, 'tweets.csv')

