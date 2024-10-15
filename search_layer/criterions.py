import os 
import sys
import pandas as pd
import requests

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_dir)

from integration_layer import *

url_combined = "https://bacen.sharepoint.com/sites/sumula/_api/web/lists/GetByTitle('CombinedParameters')/items"

df_combined = pd.DataFrame()

def fetch_json(url):
    access_token = generate_access_token()
    headers = generate_sharepoint_headers(access_token)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()


def filter_json(json_data, columns):
    records = json_data.get('d', {}).get('results', [])

    filtered = [
        {key: record[key] for key in columns if key in record}
        for record in records
    ]
    
    return filtered

def jsonify(url):
    global df_combined

    json_data = fetch_json(url)
    if "CombinedParameters" in url:
        df_combined = pd.DataFrame(filter_json(json_data, [
            'Termo', 'Key', 'SecondaryTerm', 'SecondaryKey', 
            'ExtraTerm1', 'ExtraKey1','ExtraTerm2', 'ExtraKey2',
            'ExtraTerm3', 'ExtraKey3','ExtraTerm4', 'ExtraKey4',
            'ExtraTerm5', 'ExtraKey5','ExtraTerm6', 'ExtraKey6',
            'NotTerm1','NotKey1','NotTerm2','NotKey2', 
            
            'TermoRegex', 'SecondaryTermRegex', 'ExtraTermRegex1',
            'ExtraTermRegex2','ExtraTermRegex3','ExtraTermRegex4',
            'ExtraTermRegex5','ExtraTermRegex6',
            'NotTermoRegex', 'NotTermoRegex2']))


jsonify(url_combined)


