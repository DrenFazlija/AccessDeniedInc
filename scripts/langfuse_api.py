
import datetime
import pandas as pd
from utils import get_langfuse_credentials
import requests
from requests.auth import HTTPBasicAuth
import json
import csv
import sys


def langts_to_ts(langts):
    """
    Convert a langts to a timestamp
    """
    # langts = "2024-08-04T12:37:37.194Z"
    zulu_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    zulu_time = datetime.datetime.strptime(langts, zulu_format)
    zulu_time = zulu_time.replace(tzinfo=datetime.timezone.utc)
    return zulu_time.timestamp()

def flatten_dict(d):
    items = []
    if not isinstance(d, dict):
        return d

    # assuming d is k-v pair
    for k, v in d.items():
        if isinstance(v, dict):
            flattened = flatten_dict(v)
            items.extend([(f"{k}.{_k}", _v) for _k, _v in flattened])
        else:
            items.append((k, v))
    return items

def export_traces(timestamp, output_file):
    # last_run_str = '2024-08-10T12-29-01'
    last_run_str = timestamp
    last_run = datetime.datetime.strptime(last_run_str, "%Y-%m-%dT%H-%M-%S")
    last_run = last_run.timestamp()

    langfuse_secret_key, langfuse_public_key = get_langfuse_credentials()



    out = []

    
    for i in range(1, sys.maxsize):
        assert i >= 1
        traces = requests.get('http://localhost:3000/api/public/traces', params={
                        'limit': 100, 'page':i}, auth=HTTPBasicAuth(langfuse_public_key, langfuse_secret_key))
        if traces.status_code != 200:
            break
        traces = traces.json()
        traces = traces['data']
        filtered = list(filter(
            lambda x: langts_to_ts(x['timestamp']) >= last_run, traces
            ))
        if len(filtered) == 0:
            break
        out.extend(filtered)
    print("Traces:", len(out))

    backup = out.copy()
    flattened = [dict(flatten_dict(x)) for x in out]
    df = pd.DataFrame(flattened)
    # df['metadata.tag'] from float to int
    # df['metadata.tag'] = df['metadata.tag'].astype('Int64')
    # print(df.columns)

    cols = ['id', 'timestamp', 'output'] + [c for c in df.columns if c.startswith('metadata') or c.startswith('input') or c.startswith('truth')]
    print(len(df))
    df[cols].to_csv(output_file, quoting=csv.QUOTE_ALL, escapechar='\\', columns=cols, index=False)
    return df
