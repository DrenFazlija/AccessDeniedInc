import pandas as pd

batch_output_path = '../runs/seed_0/inputs/models/gemini-2.5-flash-preview-05-20/batch_output.jsonl'
clean_ouput_path = '../runs/seed_0/inputs/models/gemini-2.5-flash-preview-05-20/batch_output.csv'
inputs = '../runs/seed_0/inputs/main_run.csv'


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