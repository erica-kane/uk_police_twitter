library(data.table)
cleantweets = read_csv('cleantweet.csv')

cleantweets = select(cleantweets, -'X1')

cleantweets$date = as.Date(cleantweets$date)

cleantweets %>%
  group_by(date, police_force) %>%
  summarise(Count = n()) %>%
  ggplot(aes(x = date, y = Count, color = police_force)) + 
  geom_line(aes(color = police_force), size = 0.2, alpha = 0.2) +
  scale_color_manual(values = c('cadetblue3', 'blue', 'deepskyblue', 'dodgerblue', 'dodgerblue4')) +
  geom_smooth(size = 0.5, span = 0.5) +
  geom_vline(xintercept=as.numeric(as.Date('2020-05-25'))) +
  theme_minimal() 


cleantweets %>%
  group_by(date, police_force) %>%
  summarise(Count = n()) %>%
  ggplot(aes(x = date, y = Count)) + 
  facet_grid(rows = vars(police_force)) +
  geom_line(aes(color = police_force), size = 0.4, alpha = 0.5) +
  scale_color_manual(values = c('cadetblue3', 'blue', 'deepskyblue', 'dodgerblue', 'dodgerblue4')) +
  geom_smooth(size = 0.2, color = 'gray22', alpha = 0.1) +
  geom_vline(xintercept=as.numeric(as.Date('2020-05-25')), alpha = 0.4, size = 0.2, color = 'gray22', linetype = 'dashed') +
  theme_minimal() 
