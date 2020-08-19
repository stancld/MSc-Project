### SET HYPERARAMETER ###
bond_path <- 'C:\\Data\\UCL\\companies_bonds_EURO_list_1.csv'
output_path <- 'C:\\Data\\UCL\\bonds_EURO_DATA.yaml'
#########################

## import libraries ###
library(Rblpapi)
library(rlist)

### set global variables and loda data###
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

list.save(DATA, output_path)