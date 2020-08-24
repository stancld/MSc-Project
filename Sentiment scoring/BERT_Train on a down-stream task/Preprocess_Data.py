"""
File: Preprocess_Data.py
Author: Daniel Stancl

File description: Class for transforming raw reviews for BERT-edible input.

utf-8
"""


# import libraries and settings
import numpy as np
import pandas as pd
import torch
import transformers
from transformers import BertTokenizer

### MAIN ###
class PrepareData(object):

    def __init__(self, pretrained_model_name='bert-base-cased'):
        """
        """
        self.valid_columns = [
            ['Pros', 'Cons', 'Rating'],
            ['positives', 'negatives', 'overall'],
            ['positives', 'negatives', 'sentiment'],
            ['positives', 'negatives', 'rating'],
            ['review', 'sentiment'],
            ['review', 'rating'],
            ['Pros', 'Cons'],
            ['positives', 'negatives'] 
        ]

        self.tokenizer = BertTokenizer.from_pretrained(pretrained_model_name)
        self.tokenizer_items = [
            'input_ids', 'token_type_ids', 'attention_mask', 'sentiment'
        ]

        self.len_limit = 80

    def run(self, data_path, columns, torch_path, balanced=False, train_set=False):
        # sanity checks
        if not isinstance(columns, list):
            raise TypeError('columns must be a list')
        if columns not in self.valid_columns:
            raise ValueError('column names must follow one of the patterns defined in self.valid_columns')

        file_format = data_path.split('.')[-1]

        # load the data
        if file_format == 'csv':
            self.data = pd.read_csv(data_path)
        elif file_format in ['xls', 'xlsx']:
            self.data = pd.read_excel(data_path)
        self.data.replace(np.nan, '', inplace=True)

        # select columns, make concatenation and transform rating to sentiment if desired
        self.data = self.data[columns]
        self._transform_input_columns(columns)
        if train_set is True:
            self._drop_tooLongReviews()
            if balanced:
                self._make_balanced_data()
        self._transform_inputs()
        
        # save data as tensors to be simply loadable in PyTorch Lightning
        [self._convert_to_tensor_save(column, torch_path) for column in self.tokenizer_items]
    
    def _rating_to_sentiment(self, rating):
        if rating == '':
            return torch.tensor((1,)) # return neutral if no rating provided  
        elif int(rating) <= 2:
            return torch.tensor((0,))
        elif int(rating) == 3:
            return torch.tensor((1,))
        else:
            return torch.tensor((2,))

    def _sentence_to_ids(self, review):
        return self.tokenizer.encode_plus(
            review,
            max_length=self.len_limit, # ideally to be set after data exploration
            truncation=True,
            add_special_tokens=True, # Add '[CLS]' and '[SEP]'
            return_token_type_ids=True,
            pad_to_max_length=True,
            return_attention_mask=True,
            return_tensors='pt',  # Return PyTorch tensors
    )

    def _transform_input_columns(self, columns):
        if 'review' not in columns:
            self.data['review'] = "Pros: '" + self.data[columns[0]] + "'; Cons: '" + self.data[columns[1]] + "'"
        if 'sentiment' in columns:
            self.data['sentiment'] = self.data['sentiment'].apply(lambda sentiment: torch.tensor((sentiment,)))
        else: 
            self.data['sentiment'] = self.data[columns[-1]].apply(lambda rating: self._rating_to_sentiment(rating))
            

    def _drop_tooLongReviews(self):
        self.data['ok'] = self.data['review'].apply(lambda x: len(x.split()) <= (1.5*self.len_limit))
        self.data = self.data[self.data.ok==True]

    def _make_balanced_data(self):
        self.data['sentiment_item'] = self.data['sentiment'].apply(lambda x: x.item())
        class_count = (
            self.data
            .groupby('sentiment_item')
            .count()
            .review
        )
        class_countToBeDropped = class_count - class_count.min()
        for sentiment in class_countToBeDropped.index:
            self.data.drop(
                self.data[self.data['sentiment_item']==sentiment].sample(class_countToBeDropped[sentiment]).index,
                axis=0, inplace=True
            )
        self.data.drop('sentiment_item', axis=1, inplace=True)

    def _transform_inputs(self):
        self.data['INPUT_and_MASK'] = self.data['review'].apply(lambda review: self._sentence_to_ids(review))
        self.data['input_ids'] = self.data['INPUT_and_MASK'].apply(lambda x: x['input_ids'].reshape(1,-1))
        self.data['token_type_ids'] = self.data['INPUT_and_MASK'].apply(lambda x: x['token_type_ids'].reshape(-1,1))
        self.data['attention_mask'] = self.data['INPUT_and_MASK'].apply(lambda x: x['attention_mask'].reshape(1,-1))
    
    def _convert_to_tensor_save(self, column, torch_path):
        torch_data = torch.cat(
            tuple(self.data[column])
        )
        fpath = f"{torch_path}{column.upper()}.pt"
        torch.save(torch_data, fpath)