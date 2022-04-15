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

# 




