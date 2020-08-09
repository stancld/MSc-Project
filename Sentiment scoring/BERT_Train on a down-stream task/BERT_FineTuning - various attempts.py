# settings
import transformers
from transformers import BertModel, BertTokenizer, AdamW, get_linear_schedule_with_warmup
import torch

from torch import nn, optim
from torch.utils.data import Dataset, DataLoader

import pandas as pd

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
PRE_TRAINED_MODEL_NAME = 'bert-base-cased'
#####


data = pd.read_csv('/mnt/c/Data/UCL/@MSc Project - Data and sources/Sentiment training/train.csv')
data = data[['positives', 'negatives', 'overall']]

data['review'] = data['positives'] + ' ' + data['negatives']
data = data[['review', 'overall']]


### rating to sentiment
def rating_to_sentiment(rating):
    if rating <= 2:
        return 0
    elif rating == 3:
        return 1
    else:
        return 2

data['sentiment'] = data['overall'].apply(lambda x: rating_to_sentiment(x))

# Data Pre-processing
tokenizer = BertTokenizer.from_pretrained(PRE_TRAINED_MODEL_NAME)

max_length = max(data['review'].apply(lambda x: len(x)))

X = pd.DataFrame(
    columns=['a', 'b', 'c']
)
data['review'][:2].apply(lambda x: sentence_to_ids(x))
b = X.apply(lambda x: x['input_ids'].numpy())
X['c'] = X['a'].apply(lambda x: x['attention_mask'])

torch.tensor(np.array(X[['b','c']]))

def sentence_to_ids(review):
    return tokenizer.encode_plus(
        review,
        max_length=512,
        truncation=True,
        add_special_tokens=True, # Add '[CLS]' and '[SEP]'
        return_token_type_ids=True,
        pad_to_max_length=True,
        return_attention_mask=True,
        return_tensors='pt',  # Return PyTorch tensors
    )


len()


x=data['review'][22]
tokenizer.encode_plus(
        x,
        max_length=64,
        truncation=True,
        add_special_tokens=True, # Add '[CLS]' and '[SEP]'
        return_token_type_ids=True,
        pad_to_max_length=True,
        return_attention_mask=True,
        return_tensors='pt',  # Return PyTorch tensors
)


X=torch.tensor(
    [[1,2,3], [2,3,4], [4,5,6]]
)

y = torch.tensor(
    [1,0,1]
)

torch.tensor((X, y))