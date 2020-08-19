"""
File: PortfolioConstructio_main.py
Author: Daniel Stancl

utf-8
"""
###########################
### SET HYPERPARAMETERS ###
###########################
company_path = '/mnt/c/Data/UCL/@MSc Project - Data and sources/Sentiment results/companies_filtered.csv'
bond_dataset_path = '/mnt/c/Data/UCL/@MSc Project - Data and sources/List of bonds/Bond_dataset.csv'
source_data_path = '/mnt/c/Data/UCL/@MSc Project - Data and sources/Sentiment results/'
output_path = '/mnt/c/Data/UCL/@MSc Project - Data and sources/Sentiment results/Portfolios/'

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
a=PorfolioConstruction(company_path, bond_dataset_path)
# run sentiment portfolio
a.run(source_data_path, output_path, False, **kwargs)
# run momentu portfolio
a.run(source_data_path, output_path, True, **kwargs)
