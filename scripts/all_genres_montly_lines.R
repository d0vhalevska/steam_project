
library(tidyverse, quietly = TRUE)
path <- "datasets/generated/"
filename <- "genres_count_yearly"

df<-read_csv(path%>%paste(filename,sep='')%>%paste(".csv",sep=''))
df$date <- with(df, as.Date(sprintf("%d-%02d-01", year, month), format="%Y-%m-%d"))

p = df %>% ggplot(mapping = aes(x = date, y = count, log="y",group = 1)) +
  geom_line() + facet_wrap(vars(genre),drop=TRUE)+
  scale_y_log10() +
  scale_x_date(date_breaks = "1 year", date_labels =  "%Y")+
  theme(axis.text.x = element_text(angle = 70))
ggsave("plots/all.png", plot = p, height = 50, width = 50, dpi=100, unit= 'in',limitsize=FALSE)
  