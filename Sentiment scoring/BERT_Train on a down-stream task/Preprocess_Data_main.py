# import libraries and settings
import pandas as pd
import torch
import transformers
from transformers import BertTokenizer

from Preprocess_Data import PrepareData

# parameters
pretrained_model_name = 'bert-base-cased'
data_path = '/mnt/c/Data/UCL/@MSc Project - Data and sources/Sentiment training/train.csv'
columns = ['positives', 'negatives', 'overall']
torch_path = '/mnt/c/Data/UCL/@MSc Project - Data and sources/Sentiment training/'

def main():
    data_loader = PrepareData(pretrained_model_name)
    data_loader.run(data_path, columns, torch_path)

if __name__=='__main__':
    main()
