# import libraries and settings
from os import listdir
from os.path import isfile, join

import numpy as np
from numpy.random import random, seed
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

class BERT_SentimentClassifier(LightningModule):
    """
    """
    def __init__(self, **kwargs):
        super(BERT_SentimentClassifier, self).__init__()
        self.data_path = kwargs['DATA_PATH']
        self.user_device = kwargs['DEVICE']
        
        self.bert = BertModel.from_pretrained(kwargs['PRE_TRAINED_MODEL_NAME'])
        self.dropout = nn.Dropout(p=kwargs['DROPOUT_PROB'])
        self.out = nn.Linear(self.bert.config.hidden_size, kwargs['N_CLASSES'])

        self.data_components = self._getDataComponents()
        if not self._checkIfFilesInPath():
            raise FileNotFoundError('Some files are missing in data path.\
                There must be all of the following four files:\
                    1. "INPUT_IDS.pt"\
                    2. "TOKEN_TYPE_IDS.pt"\
                    3. "ATTENTION_MASK.pt"\
                    4. "SENTMENT.pt"\
                    ')

    def forward(self, input_ids, attention_mask):
        pass
        """
        _, pooled_output = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        output = self.out(
            self.dropout(pooled_output)
        )
        return output # logits
        """

    def prepare_data(self):
        self._loadData() # load individual data components
        self._splitData() # split all components into train, val and test sets

    def train_dataloader(self):
        return DataLoader(
            dataset=(
                self.input_ids_train,
                self.token_type_ids_train,
                self.attention_mask_train,
                self.targets_train
            ), batch_size=64
        )

    def val_dataloader(self):
        return DataLoader(
            dataset=(
                self.input_ids_val,
                self.token_type_ids_val,
                self.attention_mask_val,
                self.targets_val
            ), batch_size=64
        )

    def test_dataloader(self):
        return DataLoader(
            dataset=(
                self.input_ids_test,
                self.token_type_ids_test,
                self.attention_mask_test,
                self.targets_test
            ), batch_size=64
        )

    def _checkIfFilesInPath(self):
        return all(
            [True if f in self._getFiles() else False for f in self.data_components.values()]
        )

    def _getFiles(self):
        files = [f for f in listdir(self.data_path) if isfile(join(self.data_path, f))]
        return files

    def _getDataComponents(self):
        return {
            'input_ids': 'INPUT_IDS.pt',
            'token_type_ids': 'TOKEN_TYPE_IDS.pt',
            'attention_mask': 'ATTENTION_MASK.pt',
            'targets': 'SENTIMENT.pt'
        }
    
    def _loadData(self):
        for data, file_path in self.data_components.items():
            exec(f"self.{data} = torch.load(join(self.data_path, file_path))", globals(), locals())
            if data == 'input_ids':
                exec(f"self.dim = self.{data}.shape[0]")
            # explicitly reshape
            exec(f"self.{data} = self.{data}.reshape(self.dim, -1)", locals())

    def _splitData(self):
        split = random(self.dim)
        # train
        for data in self.data_components.keys():
            exec(f"self.{data}_train = self.{data}[split <= 0.8]", locals())
        # val
        for data in self.data_components.keys():
            exec(f"self.{data}_val = self.{data}[(split > 0.8) & (split <= 0.9)]", locals())
        # test
        for data in self.data_components.keys():
            exec(f"self.{data}_test = self.{data}[split > 0.9]", locals())


### TEST ###
BERT_parameters = {
    'PRE_TRAINED_MODEL_NAME': 'bert-base-cased',
    'DROPOUT_PROB': 0.3,
    'N_CLASSES': 3,
    'DATA_PATH': '/mnt/c/Data/UCL/@MSc Project - Data and sources/Sentiment training/',
    'DEVICE': torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
}

clf = BERT_SentimentClassifier(**BERT_parameters)
clf.prepare_data()
clf.train_dataloader()