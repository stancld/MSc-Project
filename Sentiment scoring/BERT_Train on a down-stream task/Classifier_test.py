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

from SentimentClassifier import BERT_SentimentClassifier

### TEST ###
BERT_parameters = {
    'PRE_TRAINED_MODEL_NAME': 'bert-base-cased',
    'BATCH_SIZE': 32,
    'DROPOUT_PROB': 0.3,
    'N_CLASSES': 3,
    'N_EPOCHS': 3,
    'DATA_PATH': '/mnt/c/Data/UCL/@MSc Project - Data and sources/Sentiment training/',
}

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

clf = BERT_SentimentClassifier(**BERT_parameters)

trainer = Trainer()
trainer.fit(clf)