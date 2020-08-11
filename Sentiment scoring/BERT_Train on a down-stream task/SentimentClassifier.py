# import libraries and settings
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
### MAIN ###

class BERT_SentimentClassifier(LightningModule):
    """
    """
    def __init__(self, **kwargs):
        super(BERT_SentimentClassifier, self).__init__()   
        self.save_hyperparameters()
        self.bert = BertModel.from_pretrained(kwargs['PRE_TRAINED_MODEL_NAME'])
        self.dropout = nn.Dropout(p=kwargs['DROPOUT_PROB'])
        self.out = nn.Linear(self.bert.config.hidden_size, kwargs['N_CLASSES'])

        self.batch_size = kwargs['BATCH_SIZE']
        self.n_epochs = kwargs['N_EPOCHS']
        self.num_workers = kwargs['NUM_WORKERS']
        self.learning_rate = kwargs['LEARNING_RATE']

        self.data_path = kwargs['DATA_PATH']
        self.data_components = self._getDataComponents()

        if not self._checkIfFilesInPath():
            raise FileNotFoundError('Some files are missing in data path.\
                There must be all of the following three files:\
                    1. "INPUT_IDS.pt"\
                    2. "ATTENTION_MASK.pt"\
                    3. "SENTIMENT.pt"\
                    ')

    def forward(self, input_ids, attention_mask):
        _, pooled_output = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        output = self.out(
            self.dropout(pooled_output)
        )
        return output # logits

    def prepare_data(self):
        self._loadData() # load individual data components
        self._splitData() # split all components into train, val and test sets
        self._generateDatasets()

    def train_dataloader(self):
        return DataLoader(
            dataset=self.train_data,
            batch_size=self.batch_size,
            num_workers=self.num_workers
        )

    def val_dataloader(self):
        return DataLoader(
            dataset=self.val_data,
            batch_size=self.batch_size,
            num_workers=self.num_workers
        )

    """
    def test_dataloader(self):
        return DataLoader(
            dataset=(
                self.input_ids_test,
                self.token_type_ids_test,
                self.attention_mask_test,
                self.targets_test
            ), batch_size=self.batch_size
        )
    """

    def configure_optimizers(self):
        optimizer = AdamW(self.parameters(), lr=self.learning_rate, correct_bias=False)
        num_training_steps = (self.input_ids_train.shape[0] // self.batch_size) * self.n_epochs
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=0,
            num_training_steps=num_training_steps
        )
        return [optimizer], [scheduler]

    def training_step(self, batch, batch_idx):
        input_ids, attention_mask, target = batch
        output = self.forward(input_ids, attention_mask)
        loss = F.cross_entropy(output, target)
        return {'loss': loss}

    def validation_step(self, batch, batch_idx):
        input_ids, attention_mask, target = batch
        output = self.forward(input_ids, attention_mask)
        loss = F.cross_entropy(output, target)
        pred = output.argmax(dim=1, keepdim=True)
        correct = pred.eq(target.view_as(pred)).sum().item()
        return {'val_loss': loss, 'correct': correct}

    def training_epoch_end(self, outputs):
        avg_loss = torch.stack([x['loss'] for x in outputs]).mean()
        tensorboard_logs = {'train_loss': avg_loss}
        return {'avg_train_loss': avg_loss, 'log': tensorboard_logs}

    def validation_epoch_end(self, outputs):
        avg_loss = torch.stack([x['val_loss'] for x in outputs]).mean()
        accuracy = sum([x['correct'] for x in outputs]) / (self.batch_size * len([x['correct'] for x in outputs]))
        tensorboard_logs = {'val_loss': avg_loss, 'accuracy': accuracy}
        return {'avg_val_loss': avg_loss, 'accuracy': accuracy, 'log': tensorboard_logs}
    
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
            'attention_mask': 'ATTENTION_MASK.pt',
            'targets': 'SENTIMENT.pt'
        }
    
    def _loadData(self):
        for data, file_path in self.data_components.items():
            exec(f"self.{data} = torch.load(join(self.data_path, file_path))", globals(), locals())
            if data == 'input_ids':
                exec(f"self.dim = self.{data}.shape[0]")
            # explicitly reshape
            if data == 'targets':
                exec(f"self.{data} = self.{data}.reshape(self.dim)", locals())
            else:
                exec(f"self.{data} = self.{data}.reshape(self.dim, -1)", locals())

    def _splitData(self):
        split = random(self.dim)
        # train
        for data in self.data_components.keys():
            exec(f"self.{data}_train = self.{data}[:32]", locals())
            'exec(f"self.{data}_train = self.{data}[split <= 0.8]", locals())'
        # val
        for data in self.data_components.keys():
            exec(f"self.{data}_val = self.{data}[32:64]", locals())
            'exec(f"self.{data}_val = self.{data}[(split > 0.8) & (split <= 0.9)]", locals())'
        # test
        for data in self.data_components.keys():
            exec(f"self.{data}_test = self.{data}[split > 0.9]", locals())

    def _generateDatasets(self):
        self.train_data = TensorDataset(self.input_ids_train, self.attention_mask_train, self.targets_train)
        self.val_data = TensorDataset(self.input_ids_val, self.attention_mask_val, self.targets_val)
        