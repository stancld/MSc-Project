"""
File: Extract bond names.py
Author: Daniel Stancl

utf-8
"""
##########################
### SET HYPERPARAMETER ###
##########################
data_path = "/mnt/c/Data/UCL/companies_bonds_EURO_list.csv"
output_path = "/mnt/c/Data/UCL/companies_bonds_EURO_list_1.csv"
##########################
##########################

# Import libraries
import re
import pandas as pd

# load the data
data = pd.read_csv(data_path, index_col=0)
data.columns = ['Bond', 'Company', 'Symbol']
data.head()

# extract only corporate bonds
def generate_string(symbol):
    string = f"{symbol} (.+?) (.+?)/(.+?)/(.+?)<corp>"
    return string

bond_indicator = [re.search(generate_string(symbol), bond)!=None for symbol, bond in zip(data.Symbol, data.Bond)]
data_filtered = data[bond_indicator]

# change the bond name to be in aligned with the terminology of Bloomberg - <corp> to CORP
data_filtered['Bond'] = data_filtered['Bond'].apply(lambda x: re.sub('<corp>', ' CORP', x))

# correct decimals
def correct_decimals(bond):
    try:
        decimal =  re.search(r"<(.+?)/(.+?)+>", bond).group(0)
        parsed_decimal = re.findall("<(.+?)/(.+?)+>", decimal)[0]
        correct_decimal = str( int(parsed_decimal[0]) / int(parsed_decimal[1]) )[1:] # omit zero before .
        
        return re.sub(r"<(.+?)/(.+?)+>", correct_decimal, bond) # return corrected bond name
    except:
        return bond

data_filtered['Bond_corrected'] = data_filtered['Bond'].apply(lambda x: correct_decimals(x))

# save the data
data_filtered.to_csv(output_path, index=False)