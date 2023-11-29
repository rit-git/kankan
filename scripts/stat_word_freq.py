import csv
import collections
from transformers import BertJapaneseTokenizer
import tqdm

data_path = '/home/01052711/kankan/dataset/jalan_kanko.csv.tokyo.csv'

tokenizer = BertJapaneseTokenizer.from_pretrained('cl-tohoku/bert-base-japanese')
ctr = collections.defaultdict(int)
with open(data_path) as f:
    reader = csv.DictReader(f)
    for row in tqdm.tqdm(reader):
        for word in tokenizer.tokenize(row['kuchikomi_report']):
            ctr[word] += 1

for name, cnt in sorted(ctr.items(), key=lambda x: x[1], reverse=True):
    print(name + '\t' + str(cnt))