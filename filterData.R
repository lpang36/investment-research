#read data
allData <- read.csv('alldata.csv')
summary(allData)

#filter data
allData$date <- as.Date(allData$date)
dateFilter <- subset(allData,date>as.Date('2008-01-01'))
stocksFiltered <- data.frame(ticker=dateFilter$ticker,
                     date=dateFilter$date,
                     volume = dateFilter$adj_volume,
                     open = dateFilter$adj_open,
                     high = dateFilter$adj_high,
                     low = dateFilter$adj_low,
                     close = dateFilter$adj_close)
summary(stocksFiltered)
basicSet <- data.frame(ticker=dateFilter$ticker,
                       volume=dateFilter$adj_volume,
                       close=dateFilter$adj_close)

#save data
write.csv(stocksFiltered,'stocksFiltered.csv')
write.csv(basicSet,'basicSet.csv')