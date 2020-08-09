# import libraries and settings
import numpy as np
import pandas as pd

import torch
from torch import nn, optim
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

import pytorch_lightning as pl
from pytorch_lightning import LightningModule, Trainer

import transformers
from transformers import BertModel, BertTokenizer, AdamW, get_linear_schedule_with_warmup

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
PRE_TRAINED_MODEL_NAME = 'bert-base-cased'

### MAIN ###
class PrepareData(object):

    def __init__(self, **kwargs):
        """
        """
        self.valid_columns = [
            ['positive', 'negative', 'sentiment'],
            ['positive', 'negative', 'rating'],
            ['review', 'sentiment'],
            ['review', 'rating']
        ]

        self.tokenizer = BertTokenizer.from_pretrained(kwargs['PRE_TRAINED_MODEL_NAME'])

    def run(self, data_path, columns):
        # sanity checks
        if not isinstance(columns, list):
            raise TypeError('columns must be a list')
        if columns not in self.valid_columns:
            raise ValueError('column names must follow one of the patterns defined in self.valid_columns')

        file_format = data_path.split('.')[-1]

        # load the data
        if file_format == 'csv':
            data = pd.read_csv(data_path)
        elif file_format in ['xls', 'xlsx']:
            data = pd.read_excel(data_path)
        
        # select columns, make concatenation and transform rating to sentiment if desired
        data = data[columns]
        if 'positive' in columns:
            data['review'] = data['positive'] + ' ' + data['negative']
        if 'rating' in columns:
            data['sentiment'] = data['rating'].apply(lambda rating: self._rating_to_sentiment(rating))

        # tranform inputs
        data['INPUT_and_MASK'] = data['review'].apply(lambda review: self._sentence_to_ids(review))
        data['input_ids'] = data['INPUT_and_MASK'].apply(lambda x: x['input_ids'])
        data['attention_mask'] = data['INPUT_and_MASK'].apply(lambda x: x['attention_mask'])


    
    def _rating_to_sentiment(self, rating):
        if rating <= 2:
            return 0
        elif rating == 3:
            return 1
        else:
            return 2

    def _sentence_to_ids(self, review):
        return self.tokenizer.encode_plus(
            review,
            max_length=512,
            truncation=True,
            add_special_tokens=True, # Add '[CLS]' and '[SEP]'
            return_token_type_ids=False,
            pad_to_max_length=True,
            return_attention_mask=True,
            return_tensors='pt',  # Return PyTorch tensors
    )
            