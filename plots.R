library(dplyr)
library(readr)
library(ggplot2)

plot_tweets = read_csv('analysis_tweets.csv')
plot_tweets = select(plot_tweets, -'X1')

plot_tweets = plot_tweets[plot_tweets$tweet_class > 0, ] 
plot_tweets = plot_tweets[plot_tweets$tweet_class < 100, ] 
plot_tweets$tweet_class = as.factor(plot_tweets$tweet_class)
plot_tweets$date = as.Date(plot_tweets$date)

plot_tweets$tweet_class = recode(plot_tweets$tweet_class, '1' = "Pushing information", '2' = "Engagement", '3' = "Intelligence gathering")

ggplot(plot_tweets, aes(police_force)) + 
  geom_bar(stat = 'count', aes(fill = tweet_class), position = 'fill', color = 'grey') +
  scale_fill_brewer(name = 'Tweet class') +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, vjust = 0.65)) +
  labs(x = 'Police force', y = 'Percentage relative to force count') 

plot_tweets %>%
  mutate(week=floor_date(date, unit="week")) %>%
  group_by(week, police_force, tweet_class) %>%
  summarise(Count = n()) %>%
  ggplot(aes(x = week, y = Count, color = tweet_class)) +
  geom_line() + 
  facet_wrap(~ police_force, ncol = 1) +
  labs(x = 'Date', y = 'Tweet count (aggregated by week)', title = 'Police force tweet frequency per class', color = 'Tweet class') +
  theme_minimal()

plot_tweets %>%
  mutate(week=floor_date(date, unit="week")) %>%
  group_by(week, police_force, tweet_class) %>%
  summarise(Count = n()) %>%
  ggplot(aes(x=week, fill=tweet_class)) +
  geom_histogram(position="identity", alpha=0.2, bins = 50) +
  facet_wrap(~ police_force, ncol = 1) +
  labs(x = 'Date', y = 'Tweet count (aggregated by week)', title = 'Police force tweet frequency per class', color = 'Tweet class') +
  theme_minimal()
  
plot_tweets %>%
  mutate(week=floor_date(date, unit="week")) %>%
  group_by(week, police_force, tweet_class) %>%
  summarise(Count = n()) %>%
  ggplot(aes(x=week)) + 
  geom_density(aes(fill=tweet_class), alpha = 0.2)+ 
  facet_wrap( ~ police_force, ncol = 1)+ 
  theme_minimal()




