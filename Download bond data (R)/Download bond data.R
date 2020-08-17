## import libraries ###
library(Rblpapi)

### set global variables ###

### connection ###
blpConnect(host = getOption("blpHost", "localhost"),
           port = getOption("blpPort", 8194L), default = TRUE,
           appName = getOption("blpAppName", NULL))

### options ###
field_names <- c("PX_BID", "PX_ASK")
start_date <- as.Date("2018-01-01")
opt <- c("periodicitySelection"="MONTHLY")


bonds = c(
  "ABT 2.55 03/15/2022 CORP",
  "ABT 4.9 11/30/2046 CORP",
  "ABBV 3.2 11/06/2022 CORP",
  "ABBV 4.25 11/21/2049 144A CORP"
)



test <- bdh(securities = bonds,
       fields = field_names,
       start.date = start_date,
       options=opt)

lookupSecurity('ABT <corp>')