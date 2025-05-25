from tqdm import tqdm
import json
from numpy import random
import re
import base64
import requests
from typing import Union

def timenow():
    import datetime
    return datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S')

def get_langfuse_credentials():
    try:
        with open('.env/langfuse.json') as f:
            credentials = json.load(f)
        return credentials.get('langfuse_secret_key'), credentials.get('langfuse_public_key')
    except FileNotFoundError:
        raise FileNotFoundError("langfuse.json not found. Ensure the file exists in the .env directory.")
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON in langfuse.json")

def get_openai_credentials(file_path):
    try:
        with open(file_path) as f:
            credentials = json.load(f)
        return credentials['openai_api_key']
    except KeyError:
        raise KeyError("Missing 'openai_api_key' in openai.json.")
    except (FileNotFoundError, json.JSONDecodeError):
        raise ValueError("Invalid or missing .env/openai.json.")

def get_hf_credentials(file_path):
    try:
        with open(file_path) as f:
            credentials = json.load(f)
        return credentials['huggingface_api']
    except KeyError:
        raise KeyError("Missing 'huggingface_api' in openai.json.")
    except (FileNotFoundError, json.JSONDecodeError):
        raise ValueError("Invalid or missing file_path.")
    
def get_l3s_credentials(file_path):
    try:
        with open(file_path) as f:
            credentials = json.load(f)
        return credentials['l3s']
    except KeyError:
        raise KeyError("Missing 'l3s' in openai.json.")
    except (FileNotFoundError, json.JSONDecodeError):
        raise ValueError("Invalid or missing file_path.")

def get_interweb_credentials(file_path):
    try:
        with open(file_path) as f:
            credentials = json.load(f)
        return credentials['interweb']
    except KeyError:
        raise KeyError("Missing 'interweb' in openai.json.")
    except (FileNotFoundError, json.JSONDecodeError):
        raise ValueError("Invalid or missing file_path.")

def get_xai_credentials(file_path):
    try:
        with open(file_path) as f:
            credentials = json.load(f)
        return credentials['grok2']
    except KeyError:
        raise KeyError("Missing 'grok2' in openai.json.")
    except (FileNotFoundError, json.JSONDecodeError):
        raise ValueError("Invalid or missing file_path.")
    
def get_deepseek_credentials(file_path):
    try:
        with open(file_path) as f:
            credentials = json.load(f)
        return credentials['deepseek']
    except KeyError:
        raise KeyError("Missing 'deepseek' in openai.json.")
    except (FileNotFoundError, json.JSONDecodeError):
        raise ValueError("Invalid or missing file_path.")

def get_friendli_credentials(file_path):
    try:
        with open(file_path) as f:
            credentials = json.load(f)
        return credentials['friendli']
    except KeyError:
        raise KeyError("Missing 'friendli' in openai.json.")
    except (FileNotFoundError, json.JSONDecodeError):
        raise ValueError("Invalid or missing file_path.")
    
def get_openrouter_credentials(file_path):
    try:
        with open(file_path) as f:
            credentials = json.load(f)
        return credentials['openrouter']
    except KeyError:
        raise KeyError("Missing 'openrouter' in openai.json.")
    except (FileNotFoundError, json.JSONDecodeError):
        raise ValueError("Invalid or missing file_path.")

def eval_rag(model, vectorstore, debug=False, basestr=None, numtests=50, k=15, search_type='similarity'):
    first = False
    at = []
    not_found = []

    num_documents = len(vectorstore._collection.get().get('documents', []))
    if num_documents == 0:
        raise ValueError("Vectorstore is empty.")

    tests = random.choice(range(0, num_documents), size=numtests, replace=False)
    retriever = vectorstore.as_retriever(search_type='similarity', search_kwargs={'k': k})

    if not hasattr(retriever, 'invoke'):
        raise AttributeError("Retriever does not have an 'invoke' method.")

    for idoc in tqdm(tests):
        data = vectorstore._collection.get()['documents'][idoc]
        row = vectorstore._collection.get()['metadatas'][idoc]['row']
        info = extract_info(data, 'first_name', 'last_name')

        if first:
            print(f"info:\n{idoc}\n{info}\nsearch for: first_name: {info['first_name']} last_name: {info['last_name']} {basestr}")
            first = False

        retrieved = retriever.invoke(f"first_name: {info['first_name']}\n last_name: {info['last_name']}\n" + (basestr or ""))

        for i, d in enumerate(retrieved):
            i += 1
            if d.metadata['row'] == row:
                at.append(i)
                break
        else:
            not_found.append((idoc, row))
            if debug:
                print(f"{info['first_name']} {info['last_name']} not found")

    print(f'{search_type} search, with basestr: {basestr if basestr else "None"}')
    print('mean: ', sum(at) / len(at) if len(at) > 0 else 0,
          "in top 10: ", (len([a for a in at if a < 10])))
    print((f"median: {sorted(at)[len(at) // 2]}" if len(at) > 0 else ''))
    print(f"not found: {len(not_found)}/{len(tests)}\n", not_found)

def extract_info(data, *keys):
    pattern = re.compile(rf"({'|'.join(keys)}):\s*(.+)")
    matches = pattern.findall(data)
    return {key: value for key, value in matches}

class LangfuseClient:
    def __init__(self, secret_key=None, public_key=None, host='localhost:3000'):
        if secret_key is None or public_key is None:
            secret_key, public_key = get_langfuse_credentials()
        self.secret_key = secret_key
        self.public_key = public_key
        self.host = host

    def fetch_traces(self):
        credentials = f"{self.public_key}:{self.secret_key}"
        encoded_credentials = base64.b64encode(credentials.encode('ascii')).decode('ascii')

        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json'
        }
        response = requests.get(f'{self.host}/api/public/traces', headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f'Error fetching traces: {response.status_code} {response.text}')

def langfuse_callback_handler(secret_key=None, public_key=None, host='http://localhost:3000', debug=False, metadata=None, silent=True):
    if secret_key is None or public_key is None:
        secret_key, public_key = get_langfuse_credentials()

    import langfuse.callback
    if not silent:
        print(f"using langfuse callback handler with secret_key: {secret_key}, public_key: {public_key}, host: {host}, debug: {debug}, metadata: {metadata if metadata else {'time': timenow()}}")

    return langfuse.callback.CallbackHandler(
        secret_key=secret_key,
        public_key=public_key,
        host=host,
        debug=debug,
        metadata=metadata if metadata else {"time": timenow()}
    )

def jconv(input: Union[dict, list, str, int, float, bool, None], top=False):
    if top:
        if not isinstance(input, (list, dict)):
            raise ValueError("Input must be a list or dict when top=True.")

    if isinstance(input, (str, int, float, bool, type(None))):
        return [("", input)]

    if isinstance(input, list):
        out = []
        for v in input:
            out.extend(jconv(v))
        return out

    if isinstance(input, dict):
        out = []
        for k, v in input.items():
            nested = jconv(v)
            out.extend([(k + ("-" + nk if nk else ""), nv) for nk, nv in nested])
        return out

    raise TypeError(f"Unsupported input type: {type(input).__name__}")
