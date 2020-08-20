"""
File: CreatePools.py
Author: Daniel Stancl

Description: The script which creates a pool available to invest.

utf-8
"""
###########################
### SET HYPERPARAMETERS ###
###########################
data_path = '/mnt/c/Data/UCL/bonds_DATA.yaml'
bond_path = '/mnt/c/Data/UCL/companies_bonds_list_1.csv'
output_path = '/mnt/c/Data/UCL/@MSc Project - Data and sources/List of bonds/Bond_dataset_new.csv'

###########################
###########################

# Import libraries
import os
from os import listdir
from os.path import isfile, join

import re
import numpy as np
import pandas as pd
import yaml

##############
#### MAIN ####
##############

# open yaml - i.e. R output
def open_yaml(data_path):
    with open(data_path) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    return data

data=open_yaml(data_path)

"""
DATA = {}
for i in range(1, 4):
    data_path = f'/mnt/c/Data/UCL/bonds_DATA_{i}.yaml'
    DATA[i] = open_yaml(data_path)
DATA_new = {**DATA[1], **DATA[2], **DATA[3]}
with open('/mnt/c/Data/UCL/bonds_DATA.yaml', 'w') as outfile:
    yaml.dump(DATA_new, outfile, default_flow_style=False)
"""

# open data containing company|symbol|bond
bonds_df = pd.read_csv(bond_path)

def parse_bond_DATA(data, bonds_df, bonds_name):
    DATA = []
    
    for i, bond in enumerate(bonds_df[bonds_name]):
        
        element = data[bond]
        
        if type(element['date']) == list:
            for j in range(len(element['date'])):
                DATA_element = {
                    'Bond': bond,
                    'Month_Interest_rate': np.round(100 * ( (1 + float(bond.split()[1])/100)**(1/12) - 1), 3),
                    'Company': bonds_df.loc[i, 'Company'],
                    'Symbol': bonds_df.loc[i, 'Symbol'],
                    'Date': element['date'][j],
                    'Ask_price': element['PX_ASK'][j],
                    'Bid_price': element['PX_BID'][j],
                    'Spread': element['BLOOMBERG_MID_G_SPREAD'][j]
                }
                DATA.append(DATA_element)
        
        else:
            DATA_element = {
                'Bond': bond,
                'Month_Interest_rate': np.round(100 * ( (1 + float(bond.split()[1])/100)**(1/12) - 1), 3),
                'Company': bonds_df.loc[i, 'Company'],
                'Symbol': bonds_df.loc[i, 'Symbol'],
                'Date': element['date'],
                'Ask_price': element['PX_ASK'],
                'Bid_price': element['PX_BID'],
                'Spread': element['BLOOMBERG_MID_G_SPREAD']
            }
            DATA.append(DATA_element)
    return pd.DataFrame(DATA)

DF = parse_bond_DATA(data, bonds_df, 'Bond_corrected')
DF['Date'] = DF['Date'].apply(lambda x: int(x))

## correct dates ##
date_converter = pd.read_excel(
    '/mnt/c/Data/UCL/@MSc Project - Data and sources/List of bonds/date_converter.xlsx'
)

def converter(date_converter, date_id):
    idx = date_converter[date_converter.DateID==date_id].Date.index[0]
    return date_converter.iloc[idx, 1]

DF['Date'] = DF['Date'].apply(lambda x: converter(date_converter, x))

## extract maturity and TTM
DF['Maturity'] = pd.to_datetime(
    DF['Bond'].apply(lambda x: x.split()[2])
)

DF['TTM'] = (DF['Maturity'] - DF['Date']).apply(lambda x: np.round(x.days/365, 2))

# drop bonds with negative TTM (wtf)
DF = DF[DF.TTM >= 0]

## save ##
DF.to_csv(
    output_path,
    index=False
)