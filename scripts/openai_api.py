import pandas as pd
from pathlib import Path
import json
import openai
from utils import get_openai_credentials
from time import sleep
import re
import os
import argparse
from tqdm import tqdm

# Argument parsing
parser = argparse.ArgumentParser(description='Process OpenAI API batches.')
parser.add_argument('--sub_batches', type=int, default=None, help='Number of sub-batches to create')
parser.add_argument('--start_index', type=int, default=0, help='Index to start processing from')
parser.add_argument('--inputs', type=str, default='../runs/seed_0/inputs/main_run.csv', help='Path to the input file')
parser.add_argument('--api_key_path', type=str, required=True, help='Path to the API key JSON file')
args = parser.parse_args()

experimentpath = []
inputs = args.inputs

inputs = Path(inputs)
pattern = r'----- USER QUERY -----\n([\s\S]*?)\n----- END USER QUERY -----\n'
pat = re.compile(pattern)

df = pd.read_csv(inputs, sep=chr(30))
if Path('../mock_data/to_drop.txt').exists():
    to_drop = Path('../mock_data/to_drop.txt').read_text().split('\n')
    print(f"Dropping ids from to_drop.txt! Amount: {len(to_drop)}")
    df = df[~df['id'].isin(to_drop)]

# Adjust the dataframe to start from the specified index
df = df.iloc[args.start_index:].reset_index(drop=True)

json_template = {
    "custom_id": None,
    "method": "POST",
    "url": "/v1/chat/completions",
    "body": {
        "model": "gpt-4o-2024-08-06", #"gpt-4o-mini-2024-07-18",
        "temperature": 0.0,
        "messages": [
            {
                "role": "system",
                "content": None
            },
            {
                "role": "user",
                "content": None
            }
        ]
    }
}

model_path = Path(inputs.parent / 'models/GPT-4o')
print(model_path)
if not model_path.exists():
    os.mkdir(model_path)

batch_input_path = model_path / 'batch_input.jsonl'
batch_output_path = model_path / 'batch_output.jsonl'
clean_ouput_path = model_path / 'batch_output.csv'

print(batch_input_path)
print(batch_output_path)
print(clean_ouput_path)

def create_batches(df, sub_batches):
    if sub_batches:
        batch_size = len(df) // sub_batches
        return [df[i:i + batch_size] for i in range(0, len(df), batch_size)]
    else:
        return [df]

batches = create_batches(df, args.sub_batches)

for batch_index, batch_df in enumerate(batches):
    if args.sub_batches:
        batch_input_path = model_path / f'batch_input_{batch_index}.jsonl'
        batch_output_path = model_path / f'batch_output_{batch_index}.jsonl'
        clean_ouput_path = model_path / f'batch_output_{batch_index}.csv'

    if not batch_input_path.exists():
        with open(batch_input_path, 'w') as f:
            for i, e in tqdm(batch_df.iterrows(), total=batch_df.shape[0], desc=f'Processing batch {batch_index}'):
                line = json_template.copy()
                line['custom_id'] = e['id']
                text = e['input']
                if re.findall(pat, text) == []:
                    print('No query found in:', e['id'])
                query = re.findall(pat, text)[0]
                assert len(query) > 0, 'Query empty'
                system_prompt = re.sub(r'----- USER QUERY -----\n(.*)\n----- END USER QUERY -----\n', '', text)

                line['body']['messages'][0]['content'] = system_prompt
                line['body']['messages'][1]['content'] = query
                if i == 0:
                    print('Example:', line)
                f.write(
                    json.dumps(line, separators=(',', ':'))
                )
                f.write('\n')

    api_path = Path(args.api_key_path)
    client = openai.Client(api_key=get_openai_credentials(api_path))
    fid = client.files.create(
        purpose='batch',
        file=batch_input_path,
    )

    client.files.wait_for_processing(fid.id, max_wait_seconds=60 * 60)

    batch = client.batches.create(
        completion_window='24h',
        endpoint='/v1/chat/completions',
        input_file_id=fid.id,
    )

    print(batch.id, batch.status)

    while (batch := client.batches.retrieve(batch.id)).status != 'completed':
        sleep(60)
    print('Batch completed')

    ofid = batch.output_file_id
    filename = client.files.retrieve(ofid)

    client.files.with_streaming_response.content(ofid)._request_func().stream_to_file(batch_output_path)
    print('Output saved to', batch_output_path)
    assert batch_output_path.exists(), 'Output file failed to save'
    client.files.delete(ofid)

    df = pd.read_json(batch_output_path, lines=True)
    pd.set_option('future.no_silent_downcasting', True)
    df['error'] = df['error'].fillna(False)

    def unpack_response(response):
        output = {}
        response = response['response']
        output['status_code'] = response['status_code']
        output['model'] = response['body']['model']
        output['choices'] = len(response['body']['choices']) # assert == 'stop'
        output['finish_reason'] = response['body']['choices'][0]['finish_reason']
        output['refusal'] = response['body']['choices'][0]['message']['refusal'] # assert == None
        output['output'] = response['body']['choices'][0]['message']['content']
        return output

    unpacked_df = df.apply(unpack_response, axis=1, result_type='expand')
    df = pd.concat([df, unpacked_df], axis=1)

    assert len(df[df['choices'] != 1]) == 0, 'Choices (output-array) != 1'
    assert len(df[df['finish_reason'] != 'stop']) == 0, 'Finish reason != stop'
    assert len(df[df['status_code'] != 200]) == 0, 'Status code != 200'
    assert df['refusal'].sum() == 0, 'We have refusals'

    df.drop(columns=['id', 'response'], inplace=True) # batch id is useless

    df = df.rename(columns={
        'custom_id': 'id'
    })
    pd.read_csv(inputs, sep=chr(30)).merge(df, on='id').drop(columns=['input']).to_csv(clean_ouput_path, index=False)
    print('Output saved to', clean_ouput_path)
