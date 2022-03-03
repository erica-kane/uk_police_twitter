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
  geom_line(aes(color = police_force), size = 0.2, alpha = 0.6) +
  scale_color_manual(values = c('cadetblue3', 'blue', 'deepskyblue', 'dodgerblue', 'dodgerblue4')) +
  #geom_smooth(size = 0.5, span = 0.5) +
  geom_vline(xintercept=as.numeric(as.Date('2020-05-25'))) +
  theme_minimal() 

plot_tweets %>%
  mutate(week=floor_date(date, unit="week")) %>%
  group_by(week, police_force) %>%
  summarise(Count = n()) %>%
  ggplot(aes(x = week, y = Count)) +
  facet_grid(rows = vars(police_force)) +
  geom_line(size = 0.4, alpha = 0.5) +
  #scale_color_manual(values = c('cadetblue3', 'blue', 'deepskyblue', 'dodgerblue', 'dodgerblue4')) +
  #geom_smooth(size = 0.2, color = 'gray22', alpha = 0.1) +
  geom_vline(xintercept=as.numeric(as.Date('2020-05-25')), alpha = 0.4, size = 0.2, color = 'gray22', linetype = 'dashed') +
  labs(x = 'Date', y = 'Tweet count (aggregated by week)', title = 'Police force tweet frequency', color = 'Police force') +
  theme_minimal() 

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





