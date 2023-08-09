library(tidyverse, quietly = TRUE)
path = "datasets/generated/"
filename = "genres_count_yearly.csv"

df<-read_csv(path%>%paste(filename,sep=''))

p = df %>% 
ggplot() + aes(x = genre, y = count, group = year, fill = year, log = 'y') + geom_bar(stat="identity",position="dodge") + labs() + theme(axis.text.x = element_text(angle = 70),legend.position = "bottom") + labs(x = "Genre", y = "Mounthly mean playcount sum in 2017-2020") +scale_y_log10()
ggsave("plots/test.png", plot = p, height = 5, width = 50, unit = 'in', dpi = 500, limitsize = FALSE )

# top = df %>% group_by(genre) %>% summarise(count = mean(count)) %>% arrange(-count)
# top20 = top %>% slice_head(n=20)
