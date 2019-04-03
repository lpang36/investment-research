#read data
raw <- read.csv('basicSet.csv')
raw <- subset(raw, select=-X)

#generate adjusted periods
generate <- function(x) {
  numel <- length(raw$close)
  back <- raw$close[1:(numel-x)]
  front <- raw$close[(x+1):numel]
  return(c(rep(NA,x),(front-back)/back))
}

raw$close.day <- generate(1)
raw$close.week <- generate(7)
raw$close.month <- generate(30)

#save data
raw <- subset(raw, select=-close)
write.csv(raw,'periods.csv')