# import libraries and settings
import os
from os import listdir
from os.path import isfile, join

import numpy as np
from numpy.random import random, seed
import pandas as pd

import torch
from torch import nn, optim
import torch.nn.functional as F
from torch.utils.data import Dataset, TensorDataset, DataLoader

import pytorch_lightning as pl
from pytorch_lightning import LightningModule, Trainer

import transformers
from transformers import BertModel, BertTokenizer, AdamW, get_linear_schedule_with_warmup

# change directory and import SentimentClassifier
cwd = os.getcwd()
os.chdir('BERT_Train on a down-stream task')
from SentimentClassifier import BERT_SentimentClassifier
os.chdir(cwd)

class ScoreSentiment_Reviews(object):
    def __init__(self, companies, reviews):
        self.companies = companies
        self.reviews = reviews

    def run(self, sentiment_path, periods):
        self.sentimentMonthly(sentiment_path)

    def sentimentMonthly(self, sentiment_path, _return=False):
        reviews = self.tokenizer(
            list(self.reviews.Review),
            return_tensors='pt',
            padding=True
        )
        labels = torch.ones_like(torch.tensor(self.reviews.Review)).unsqueeze(0)
        outputs = bert(**reviews, labels=labels)
        logits = outputs[1].detach().numpy()
        self.reviews.ReviewSentiment = [self._positiveProbability(logits_n) for logits_n in logits]
        self.reviews.to_excel(sentiment_path)

    def _positiveProbability(self, logits):
        return np.exp(logit[0]) / np.exp(logits).sum()



"""


tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
bert = BertForSequenceClassification.from_pretrained('bert-base-uncased')

X = np.array(['They are really great!', 'The company is far from being superb.', 'I like working there.'])

inputs = tokenizer(X, return_tensors="pt", padding=True)
labels = torch.tensor([1,0,1]).unsqueeze(0)  # Batch size 1
outputs = bert(**inputs, labels=labels)
outputs[1].detach().numpy()

inputs = tokenizer("Hello, my dog is cute", return_tensors="pt")
labels = torch.tensor([1]).unsqueeze(0)  # Batch size 1
outputs = bert(**inputs, labels=labels)
logits = outputs[1]


from transformers import BertTokenizer, BertForQuestionAnswering
import torch

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForQuestionAnswering.from_pretrained('bert-base-uncased')

QA = 'How are you? I am fine.'

inputs = tokenizer(QA, return_tensors="pt")
start_positions = torch.tensor([1])
end_positions = torch.tensor([6])

outputs = model(**inputs, start_positions=start_positions, end_positions=end_positions)

loss, start_scores, end_scores = outputs[:3]
"""