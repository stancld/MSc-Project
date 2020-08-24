"""
File: Preprocess_Data_main.py
Author: Daniel Stancl

utf-8
"""


# import libraries and settings
from argparse import ArgumentParser
import numpy as np
import pandas as pd
import torch
import transformers
from transformers import BertTokenizer

from Preprocess_Data import PrepareData

# parameters
parser = ArgumentParser()

parser.add_argument(
    '--pretrained_model_name',
    default='bert-base-cased'
)
parser.add_argument(
    '--data_path',
    default='/mnt/c/Data/UCL/@MSc Project - Data and sources/Sentiment training/Reviews_DF.csv'
)
parser.add_argument(
    '--torch_path',
    default='/mnt/c/Data/UCL/@MSc Project - Data and sources/Sentiment training/'
)
parser.add_argument(
    '--columns',
    default='positives | negatives | overall'
)
parser.add_argument(
    '--balanced',
    action='store_true'
)

parser.add_argument(
    '--train_set',
    action='store_true'
)

args = parser.parse_args()
args.columns = [column.strip() for column in args.columns.split('|')]


def main():
    data_loader = PrepareData(args.pretrained_model_name)
    data_loader.run(args.data_path, args.columns, args.torch_path, args.balanced, args.train_set)

if __name__=='__main__':
    main()