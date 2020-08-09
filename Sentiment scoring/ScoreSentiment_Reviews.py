import numpy as np
import pandas as pd
from transformers import BertTokenizer, BertForSequenceClassification
import torch

class ScoreSentiment_Reviews(object):
    def __init__(self, companies, reviews):
        self.companies = companies
        self.reviews = reviews

        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.bert = BertForSequenceClassification.from_pretrained('bert-base-uncased')

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