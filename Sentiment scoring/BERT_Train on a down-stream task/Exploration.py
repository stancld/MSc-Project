import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv('/mnt/c/Data/UCL/@MSc Project - Data and sources/Sentiment training/train.csv')

data['review'] = data['positives'] + ' ' + data['negatives']

(data['review'].apply(lambda x: len(x.split())) > 300).mean()


lengths.sort_values(ascending=False)[:300]