## import libraries ###
library(Rblpapi)
library(tidyverse)

### set global variables and load data###
company_path <- "C:\\Data\\UCL\\companies_bonds.csv"
companies <- read.csv(company_path, sep = ';')

# filtr only s&p 500
listedOn = 'S&P 500'
companies <- companies[companies$ListedOn==listedOn,]
companies_list <- as.character(companies$Company)
symbol_list <- as.character(companies$Symbol)

### connection ###
blpConnect(host = getOption("blpHost", "localhost"),
           port = getOption("blpPort", 8194L), default = TRUE,
           appName = getOption("blpAppName", NULL))

### get the data!!! exciting ###
DATA = list()
DATA_company = list()
DATA_symbol = list()

for (i in 1:length(companies_list)){
  company <- companies_list[i]
  symbol <- symbol_list[i]
  
  input_query = paste(company, "<corp>", sep = " ")
  DATA[[company]] <- as.character(
    lookupSecurity(input_query)$security
  )
  DATA_company[[company]] <- rep(company, length(DATA[[company]]))
  DATA_symbol[[symbol]] <- rep(symbol, length(DATA[[company]]))
  Sys.sleep(0.5)
}

### save the data###
DATA_unlist <- unlist(DATA, use.names=FALSE)
DATA_company_unlist <- unlist(DATA_company, use.names=FALSE)
DATA_symbol_unlist <- unlist(DATA_symbol, use.names=FALSE)

df <- as.data.frame(cbind(DATA_unlist, DATA_company_unlist, DATA_symbol_unlist))

write.csv(df, 'C:\\Data\\UCL\\companies_bonds_list.csv')
