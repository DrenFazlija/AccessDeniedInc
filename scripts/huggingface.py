import pandas as pd
from pathlib import Path
import json
import re
from time import sleep
from huggingface_hub import InferenceClient
from tqdm import tqdm
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some inputs.')
    parser.add_argument('--inputs', type=str, required=True, help='Path to the input CSV file')
    parser.add_argument('--continue_at', type=int, default=0, help='Line number to continue processing from')
    parser.add_argument('--api_key_path', type=str, required=True, help='Path to the API key JSON file')
    parser.add_argument('--to_drop', type=str, default='../mock_data/to_drop.txt', help='Path to the to_drop.txt file')
    parser.add_argument('--model', type=str, default='meta-llama/Llama-3.3-70B-Instruct', help='Model name')
    parser.add_argument('--temperature', type=float, default=0.0, help='Temperature for the model')
    parser.add_argument('--input_batch_exists', type=bool, default=False, help='Whether the input batch exists')

    args = parser.parse_args()

    experimentpath = []
    inputs = args.inputs

    inputs = Path(inputs)
    pattern = r'----- USER QUERY -----\n([\s\S]*?)\n----- END USER QUERY -----\n'
    pat = re.compile(pattern)

    df = pd.read_csv(inputs, sep=chr(30))
    if Path(args.to_drop).exists():
        to_drop = Path(args.to_drop).read_text().split('\n')
        print(f"Dropping ids from to_drop.txt! Amount: {len(to_drop)}")
        df = df[~df['id'].isin(to_drop)]

    json_template = {
        "custom_id": None,
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": args.model,
            "temperature": args.temperature,
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

    model_name = args.model.split('/')[1]
    model_path = Path(inputs.parent / f'models/{model_name}')
    print(model_path)

    batch_input_path = model_path / 'batch_input.jsonl'
    batch_output_path = model_path / 'batch_output.jsonl'
    clean_ouput_path = model_path / 'batch_output.csv'

    if not model_path.exists():
        model_path.mkdir(parents=True)
    
    print('Getting the batch input from', batch_input_path)


    if not args.input_batch_exists:
        with open(batch_input_path, 'w') as f:
            for i, e in tqdm(df.iterrows(), total=len(df)):
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

    print('Saving the batch output to', batch_output_path)
    print('Saving the clean output to', clean_ouput_path)

    from huggingface_hub import InferenceClient
    from utils import get_hf_credentials

    api_key = get_hf_credentials(args.api_key_path)

    client = InferenceClient(api_key=api_key)

    continue_at = args.continue_at
    with open(batch_input_path, 'r') as f:
        for i, line in enumerate(tqdm(f, total=sum(1 for _ in open(batch_input_path)))):
            if i < continue_at:
                continue
            request = json.loads(line)
            response = client.chat.completions.create(
                model=request['body']['model'],
                messages=request['body']['messages']
            )
            response['id'] = request['custom_id']  # Add the id to the response
            with open(batch_output_path, 'a') as out_f:
                out_f.write(json.dumps(response, separators=(',', ':')))
                out_f.write('\n')

    print('Output saved to', batch_output_path)
    assert batch_output_path.exists(), 'Output file failed to save'

    df = pd.read_json(batch_output_path, lines=True)
    pd.set_option('future.no_silent_downcasting', True)

    def unpack_response(response):
        output = {}
        #response = None
        #output['status_code'] = 200
        output['model'] = response['model']
        output['choices'] = len(response['choices']) if isinstance(response['choices'], list) else 0
        output['finish_reason'] = response['choices'][0].get('finish_reason', None) if isinstance(response['choices'], list) else None
        output['output'] = response['choices'][0]['message']['content'] if isinstance(response['choices'], list) else None
        return output


    unpacked_df = df.apply(unpack_response, axis=1, result_type='expand')
    df = pd.concat([df, unpacked_df], axis=1)

    pd.read_csv(inputs, sep=chr(30)).merge(df, on='id').drop(columns=['input']).to_csv(clean_ouput_path, index=False)
    print('Output saved to', clean_ouput_path)