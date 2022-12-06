import os
import json
import requests
from dotenv import load_dotenv
from typing import List

load_dotenv()

def resp_fetcher(word):

    dkey = os.getenv('DICT_KEY')
    url = f'https://dictionaryapi.com/api/v3/references/collegiate/json/{word}'
    params = {'key' : dkey}
    resp = requests.get(url, params = params)

    resp = resp.json()[0]


    defs = resp['def'][0]['sseq']
    word_type = resp['fl']
    short_def = resp['shortdef'] # list of str

    dt_defis = map(lambda x : x[0]['sense']['dt'], defs)

    meaning, examples = map(lambda y : (y[0][0][1], y[0][1][1]), dt_defis) # (list of strs, list of dicts)

    examples = map(lambda x : x['t'], examples)

    print(meaning)
    print('\n')
    print(examples)











