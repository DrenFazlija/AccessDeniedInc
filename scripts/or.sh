#!/bin/bash

#SBATCH --mail-user=dren.fazlija@l3s.de
#SBATCH --mail-type=ALL                          # Eine Mail wird bei Job-Start/Ende versendet
#SBATCH --job-name=grok-2           # Name unter dem der Job in der Job-History gespeichert wird
#SBATCH --nodes=1                                # Number of nodes to request
#SBATCH --gpus=0                                # Number of GPUs per job
#SBATCH -t 0-24:00                               # time limit: (D-HH:MM)

# Running x-ai/grok-2-1212 via OpenRouter
python openrouter_api.py --inputs ../experiments/2025/main_run_seed_02/inputs/main_run_seed_02.csv  --continue_at 0 --api_key_path /home/dren.fazlija/.api_keys/openai.json --model x-ai/grok-2-1212