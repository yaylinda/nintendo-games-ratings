setwd("~/Developer/nintendo-games-ratings")

library(ggplot2)
library(ggthemes)
library(ggtext)
library(extrafont)
library(ggrepel)
library(stringr)
library(lubridate)
loadfonts()

data = read.csv("data.csv")
data = na.omit(data)

data$platform[which(data$platform == "WII")] = "Wii"
data$platform[which(data$platform == "WIIU")] = "Wii U"
data$platform[which(data$platform == "GC")] = "GameCube"
data$year = as.numeric(str_sub(data$date, start = -4))
data$day_of_week = weekdays(as.Date(data$date, format = "%b %d, %Y"))
data$month = strftime(as.Date(data$date, format = "%b %d, %Y"), "%B")
data$score_ratio = data$meta_score / (data$user_score * 10)
data$count = 1

#----------------------------------------------------------

ggplot(
  data, 
  aes(
    x = meta_score, 
    y = user_score, 
    color = platform
  )
) +
  geom_point() +
  geom_smooth(
    method = lm, 
    se = FALSE
  )

#----------------------------------------------------------

# Aggregate Count by Month & Platform

count_by_month_and_platform = aggregate(
  data$count,
  by = list(
    platform = data$platform,
    month = data$month
  ),
  sum
)

count_by_month_and_platform$month = factor(
  count_by_month_and_platform$month, 
  levels = c(
    "January", "February", "March", 
    "April", "May", "June", 
    "July", "August", "September", 
    "October", "November", "December"
  )
)

ggplot(
  count_by_month_and_platform, 
  aes(
    x = month, 
    y = platform, 
    fill = x
  )
) +
  geom_tile()

#----------------------------------------------------------












