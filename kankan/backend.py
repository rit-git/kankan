import sys
sys.path.append('.')

import os
import openai
from openai.embeddings_utils import get_embedding, cosine_similarity

from vecscan import PyVectorScanner, PyVectorGroups
from array import array

import collections
import tqdm
import heapq

n_best = 10
thr=0.50
model_name = 'ada' 
todofuken_name = 'nagano'
openai.api_key=os.environ["OPENAI_API_KEY"]
vec_file_path = f'./dataset/sentvecs.{model_name}.kuchikomi_report.vec.{todofuken_name}'
raw_data_path = f'./dataset/jalan_kanko.csv.{todofuken_name}.csv'
query_file_path = './dataset/query_debug.txt'


def search_reviews(query_text, scanner, **kwargs):
    if model_name == 'ada':
        embedding = array('f', get_embedding(query_text, engine='text-embedding-ada-002'))
    ret = scanner.n_best_vecs(
        query_vec=embedding,
        n_best=100000,
        openmp=True,
        debug=True,
        threshold=thr
    )
    return ret

def print_kuchikomi_results(raw_data, scan_results):
    scan_results_len = scan_results.size()

    for i in range(min(n_best, scan_results_len)):
        idx, score = scan_results.get(i)
        print(raw_data[idx].strip() + ' ||| ' + str(score))
    print('')



def print_spot_results2(raw_data, scan_results):
    spot_result = {}
    full_odk_set = set()
    scan_results_len = scan_results.size()
    for i in range(scan_results_len):
        idx, score = scan_results.get(i)
        fields = raw_data[idx].strip().split(',')
        kuchikomi_id, odk_id, other = fields[0], fields[1], ','.join(fields[2:])
        if odk_id not in spot_result:
            spot_result[odk_id] = {'score': 0.0, 'kuchikomi': [], 'cnt': 0}
        if spot_result[odk_id]['cnt'] < n_best:
            spot_result[odk_id]['kuchikomi'].append((score, other))
            spot_result[odk_id]['score'] += score
            if spot_result[odk_id]['cnt'] > 0:
                spot_result[odk_id]['score'] /= 2
            spot_result[odk_id]['cnt'] += 1
        if spot_result[odk_id]['cnt'] == n_best:
            full_odk_set.add(odk_id)
            if len(full_odk_set) >= n_best:
                break

    if len(full_odk_set) == n_best:
        result_list = [spot_result[k] for k in full_odk_set]
    else:
        result_list = spot_result.values()
    result_list = heapq.nlargest(n_best, result_list, key=lambda x: x['score'])
    for spot_rank, kuchikomi_list in enumerate(result_list):
        print('Rank: {}, Score: {}'.format(spot_rank + 1, kuchikomi_list['score']))
        for kuchikomi in kuchikomi_list['kuchikomi']:
            print('{} ||| {}'.format(kuchikomi[0], kuchikomi[1]))

if __name__ == '__main__':
    query_list = []
    for line in open(query_file_path):
        line = line.strip()
        if len(line) > 0:
            query_list.append(line)
    
    scanner = PyVectorScanner(vec_file_path, '')
    raw_data = []

    for line_idx, line in enumerate(open(raw_data_path)):
        if line_idx == 0:
            continue
        else:
            raw_data.append(line)



    print('start searching...', file=sys.stderr)
    for query in query_list:
        print('*'*40)
        print(query)
        if model_name == 'ada':
            ret_lists = search_reviews(query, scanner)

        scan_results = ret_lists[0]
        print_spot_results2(raw_data, scan_results)

