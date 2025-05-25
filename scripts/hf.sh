#!/bin/bash

#SBATCH --mail-user=dren.fazlija@l3s.de
#SBATCH --mail-type=ALL                          # Eine Mail wird bei Job-Start/Ende versendet
#SBATCH --job-name=hf_falcon7b            # Name unter dem der Job in der Job-History gespeichert wird
#SBATCH --nodes=1                                # Number of nodes to request
#SBATCH --gpus=0                                # Number of GPUs per job
#SBATCH -t 0-24:00                               # time limit: (D-HH:MM)


# Running DeepSeek-R1-Distill-Qwen-32B model
#python huggingface.py --inputs ../experiments/2025/main_run_seed_02/inputs/main_run_seed_02.csv --continue_at 3232 --api_key_path /home/dren.fazlija/.api_keys/openai.json --model deepseek-ai/DeepSeek-R1-Distill-Qwen-32B --temperature 0.6

# Running Llama-3.3.-70B-Instruct
#python huggingface.py --inputs ../experiments/2025/main_run_seed_02/inputs/main_run_seed_02.csv  --continue_at 1800 --api_key_path /home/dren.fazlija/.api_keys/openai.json

# Running DeepSeek-R1
#python huggingface.py --inputs ../experiments/2025/main_run/inputs/main_run.csv  --continue_at 0 --api_key_path /home/dren.fazlija/.api_keys/openai.json --model deepseek-ai/DeepSeek-R1 --temperature 0.6

# Running meta-llama/Llama-3.2-3B-Instruct
#python huggingface.py --inputs ../experiments/2025/main_run_seed_02/inputs/main_run_seed_02.csv  --continue_at 2832 --api_key_path /home/dren.fazlija/.api_keys/openai.json --model meta-llama/Llama-3.2-3B-Instruct

# Running tiiuae/falcon-7b-instruct
python huggingface.py --inputs ../experiments/2025/main_run_seed_01/inputs/main_run_seed_01.csv  --continue_at 0 --api_key_path /home/dren.fazlija/.api_keys/openai.json --model tiiuae/falcon-7b-instruct