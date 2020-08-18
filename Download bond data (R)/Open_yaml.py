"""
File: Opne_yaml.py
Author: Daniel Stancl
"""

import yaml

def open_yaml(i_list):
    data = dict()
    for i in i_list:
        data_path = f"/mnt/c/Data/UCL/bonds_DATA_{i}.yaml"
        with open(data_path) as f:
            data[i] = yaml.load(f, Loader=yaml.FullLoader)
    return data

data=open_yaml([1,2,3])