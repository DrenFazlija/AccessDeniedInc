#!/bin/bash

#SBATCH --mail-user=<your-email>
#SBATCH --mail-type=ALL                          
#SBATCH --job-name=<job-name>            
#SBATCH --nodes=1                                
#SBATCH --gpus=0                                
#SBATCH -t 0-24:00                               

# Running x-ai/grok-2-1212 via OpenRouter
python openrouter_api.py --inputs ../runs/seed_0/inputs/main_run.csv  --continue_at 0 --api_key_path ../.api_keys/keys.json --model x-ai/grok-2-1212