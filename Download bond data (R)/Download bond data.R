## import libraries ###
library(Rblpapi)
library(rlist)

### set global variables and loda data###
bond_path <- 'C:\\Data\\UCL\\companies_bonds_list_1.csv'
bonds_df <- read.csv(bond_path)


### connection ###
blpConnect(host = getOption("blpHost", "localhost"),
           port = getOption("blpPort", 8194L), default = TRUE,
           appName = getOption("blpAppName", NULL)
)

### options ###
field_names <- c("PX_BID", "PX_ASK", "BLOOMBERG_MID_G_SPREAD")
start_date <- as.Date("2015-01-01")
opt <- c("periodicitySelection"="MONTHLY")

bonds = as.character(bonds_df$Bond_corrected)

DATA <- bdh(securities = bonds,
            fields = field_names,
            start.date = start_date,
            options=opt
)

as.data.frame(unlist(DATA))

list.save(DATA3, 'C:\\Data\\UCL\\bonds_DATA_3.yaml')