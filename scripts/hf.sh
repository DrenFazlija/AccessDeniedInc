#!/bin/bash

#SBATCH --mail-user=<your-email>
#SBATCH --mail-type=ALL                          
#SBATCH --job-name=<job-name>            
#SBATCH --nodes=1                                
#SBATCH --gpus=0                                
#SBATCH -t 0-24:00                               


# Running DeepSeek-R1-Distill-Qwen-32B model
#python huggingface.py --inputs ../runs/seed_0/inputs/main_run.csv --continue_at 0 --api_key_path ../.api_keys/keys.json --model deepseek-ai/DeepSeek-R1-Distill-Qwen-32B --temperature 0.6

# Running Llama-3.3.-70B-Instruct
#python huggingface.py --inputs ../runs/seed_0/inputs/main_run.csv  --continue_at 0 --api_key_path ../.api_keys/keys.json --model meta-llama/Llama-3.3-70B-Instruct

# Running meta-llama/Llama-3.2-3B-Instruct
#python huggingface.py --inputs ../runs/seed_0/inputs/main_run.csv  --continue_at 0 --api_key_path ../.api_keys/keys.json --model meta-llama/Llama-3.2-3B-Instruct
