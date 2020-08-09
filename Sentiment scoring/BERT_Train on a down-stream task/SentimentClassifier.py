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

class BERT_SentimentClassifier(LightningModule):
    """
    """
    def __init__(self, **kwargs):
        super(BERT_SentimentClassifier, self).__init__()
        self.bert = BertModel.from_pretrained(kwargs['PRE_TRAINED_MODEL_NAME'])
        self.dropout = nn.Dropout(p=kwargs['DROPOUT_PROB'])
        self.out = nn.Linear(self.bert.config.hidden_size, kwargs['N_CLASSES'])

        self.data_path = kwargs['DATA_PATH']

    def forward(self, input_ids, attention_mask):
        _, pooled_output = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        output = self.out(
            self.dropout(x)
        )
        return output # logits

    def prepare_data(self):

