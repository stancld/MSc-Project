"""
File: PortfolioConstructio_main.py
Author: Daniel Stancl

utf-8
"""
###########################
### SET HYPERPARAMETERS ###
###########################
company_path = '/mnt/c/Data/UCL/@MSc Project - Data and sources/Sentiment results/companies_filtered.csv'
bond_dataset_path = '/mnt/c/Data/UCL/@MSc Project - Data and sources/List of bonds/Bond_dataset_new.csv'
source_data_path = '/mnt/c/Data/UCL/@MSc Project - Data and sources/Sentiment results/'
output_path = '/mnt/c/Data/UCL/@MSc Project - Data and sources/Sentiment results/Portfolios/New'

kwargs = {
    'ratings': True,
    'reviews': True,
    'short_term': True,
    'long_term': True,
    'diff': True  
}
###########################
###########################

# import libraries
import os
from os import listdir
from os.path import isfile, join

import numpy as np
import pandas as pd

from PortfolioConstruction import PortfolioConstruction

############
### MAIN ###
############
constructor = PortfolioConstruction(company_path, bond_dataset_path, 'S&P 500')
# run sentiment portfolio
###constructor.run(source_data_path, output_path, False, False, **kwargs)

# run momentum portfolio
constructor.run(source_data_path, output_path, True, False, **kwargs)

# run low-risk portfolio
##constructor.run(source_data_path, output_path, False, True, **kwargs)
