import sys
sys.path.append('.')

from fastapi import FastAPI
from pydantic import BaseModel
from array import array
import uvicorn
import os
import heapq

import openai
from openai.embeddings_utils import get_embedding

from vecscan.vecscan import PyVectorScanner

class KankanRequest(BaseModel):
    tdfk: str
    query: str

class KankanAPI(FastAPI):
    def __init__(self):
        super().__init__()
        openai.api_key=os.environ["OPENAI_API_KEY"]

        self.scanners = {}
        self.raw_data = {}
        self.vec_file_path_base = '/home/01052711/kankan/dataset/sentvecs.ada.kuchikomi_report.vec'
        self.raw_file_path_base = '/home/01052711/kankan/dataset/jalan_kanko.csv'
        self.n_best_hotel = 10
        self.n_best_kuchikomi = 10
        self.post("/api/search")(self.search)

    def search(self, req: KankanRequest):
        if req.tdfk not in self.scanners:
            self.scanners[req.tdfk] = PyVectorScanner(f'{self.vec_file_path_base}.{req.tdfk}', '')
            self.raw_data[req.tdfk] = []
            for line_idx, line in enumerate(open(f'{self.raw_file_path_base}.{req.tdfk}.csv')):
                if line_idx > 0:
                    self.raw_data[req.tdfk].append(line.strip())
        
        scan_results = self.scanners[req.tdfk].n_best_vecs(
            query_vec=array('f', get_embedding(req.query, engine='text-embedding-ada-002')),
            n_best=100000,
            openmp=True,
            debug=True,
            threshold=0.50
        )[0]

        spot_result = {}
        full_odk_set = set()
        scan_results_len = scan_results.size()
        for i in range(scan_results_len):
            idx, score = scan_results.get(i)
            fields = self.raw_data[req.tdfk][idx].strip().split(',')
            kuchikomi_id, odk_id, other = fields[0], fields[1], ','.join(fields[2:])
            if odk_id not in spot_result:
                spot_result[odk_id] = {'score': 0.0, 'kuchikomi': [], 'cnt': 0}
            if spot_result[odk_id]['cnt'] < self.n_best_kuchikomi:
                spot_result[odk_id]['kuchikomi'].append((score, other))
                spot_result[odk_id]['score'] += score
                if spot_result[odk_id]['cnt'] > 0:
                    spot_result[odk_id]['score'] /= 2
                spot_result[odk_id]['cnt'] += 1
            if spot_result[odk_id]['cnt'] == self.n_best_kuchikomi:
                full_odk_set.add(odk_id)
                if len(full_odk_set) >= self.n_best_hotel:
                    break

        if len(full_odk_set) == self.n_best_hotel:
            result_list = [spot_result[k] for k in full_odk_set]
        else:
            result_list = spot_result.values()
        result_list = heapq.nlargest(self.n_best_hotel, result_list, key=lambda x: x['score'])

        ret = {'hotel': []}
        for spot_rank, kuchikomi_list in enumerate(result_list):
            ret['hotel'].append(
                {
                    'rank': spot_rank + 1,
                    'score': kuchikomi_list['score'],
                    'kuchikomi': []
                }
            )
            for kuchikomi in kuchikomi_list['kuchikomi']:
                fields = kuchikomi[1].split(',')
                ret['hotel'][-1]['kuchikomi'].append(
                    {
                        'score': kuchikomi[0],
                        'rate': fields[0],
                        'title': fields[1],
                        'text': ','.join(fields[2:-5]),
                        'date': fields[-5] + '/' + fields[-4],
                        'name': fields[-3],
                        'address': fields[-2],
                        'ybn': fields[-1]
                    }
                )

        return ret
    
def main():
    app = KankanAPI()
    uvicorn.run(
        app,
        port=21344,
        root_path='/app/kankan'
    )

if __name__ == '__main__':
    main()