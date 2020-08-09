# import libraries and settings
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
            ['positives', 'negatives', 'overall'],
            ['positives', 'negatives', 'sentiment'],
            ['positives', 'negatives', 'rating'],
            ['review', 'sentiment'],
            ['review', 'rating']
        ]

        self.tokenizer = BertTokenizer.from_pretrained(pretrained_model_name)
        self.tokenizer_items = [
            'input_ids', 'token_type_ids', 'attention_mask', 'sentiment'
        ]

    def run(self, data_path, columns, torch_path):
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

        # select columns, make concatenation and transform rating to sentiment if desired
        self.data = self.data[columns]
        self._transform_input_columns(columns)
        self._transform_inputs()
        
        # save data as tensors to be simply loadable in PyTorch Lightning
        [self._convert_to_tensor_save(column, torch_path) for column in self.tokenizer_items]
    
    def _rating_to_sentiment(self, rating):
        if rating <= 2:
            return torch.tensor((0,))
        elif rating == 3:
            return torch.tensor((1,))
        else:
            return torch.tensor((2,))

    def _sentence_to_ids(self, review):
        return self.tokenizer.encode_plus(
            review,
            max_length=512,
            truncation=True,
            add_special_tokens=True, # Add '[CLS]' and '[SEP]'
            return_token_type_ids=True,
            pad_to_max_length=True,
            return_attention_mask=True,
            return_tensors='pt',  # Return PyTorch tensors
    )

    def _transform_input_columns(self, columns):
        if 'positives' in columns:
            self.data['review'] = self.data['positives'] + ' ' + self.data['negatives']
        if 'rating' in columns:
            self.data['sentiment'] = self.data['rating'].apply(lambda rating: self._rating_to_sentiment(rating))
        elif  'overall' in columns:
            self.data['sentiment'] = self.data['overall'].apply(lambda rating: self._rating_to_sentiment(rating))
        else:
            self.data['sentiment'] = self.data['sentiment'].apply(lambda sentiment: torch.tensor((sentiment,)))

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