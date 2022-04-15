library(data.table)
library(readr)
library(dplyr)
library(ggplot2)
library(lubridate)
plot_tweets = read_csv('plot_tweets.csv')

plot_tweets = select(plot_tweets, -'X1')

plot_tweets$date = as.Date(plot_tweets$date)

plot_tweets %>%
  mutate(week=floor_date(date, unit="week")) %>%
  group_by(week, police_force) %>%
  summarise(Count = n()) %>%
  ggplot(aes(x = week, y = Count, color = police_force)) +
  facet_wrap(~police_force, ncol = 1) +
  geom_line(size = 0.4, alpha = 0.5) +
  scale_color_manual(values = c('cadetblue3', 'blue', 'deepskyblue', 'dodgerblue', 'dodgerblue4')) +
  #geom_smooth(size = 0.2, color = 'gray22', alpha = 0.1) +
  geom_vline(xintercept=as.numeric(as.Date('2020-05-25')), alpha = 0.4, size = 0.2, color = 'gray22', linetype = 'dashed') +
  labs(x = 'Date', y = 'Tweet count (aggregated by week)', title = 'Police force tweet frequency', color = 'Police force') +
  theme_minimal() +
  theme(legend.position = 'none')


plot_tweets %>%
  mutate(week=floor_date(date, unit="week")) %>%
  group_by(week, police_force) %>%
  summarise(Count = n()) %>%
  ggplot(aes(x = week, y = Count, color = police_force)) +
  facet_wrap(~police_force, ncol = 1) +
  geom_point(size = 0.4, alpha = 0.5) +
  geom_smooth(size = 0.2, color = 'gray88', alpha = 0.1) +
  scale_color_manual(values = c('cadetblue3', 'blue', 'deepskyblue', 'dodgerblue', 'dodgerblue4')) +
  geom_vline(xintercept=as.numeric(as.Date('2020-05-25')), alpha = 0.4, size = 0.2, color = 'gray22', linetype = 'dashed') +
  labs(x = 'Date', y = 'Tweet count (aggregated by week)', title = 'Police force tweet frequency', color = 'Police force') +
  theme_minimal() +
  theme(legend.position = 'none')








