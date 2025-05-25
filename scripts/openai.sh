#!/bin/bash

#SBATCH --mail-user=<your-email>
#SBATCH --mail-type=ALL                          
#SBATCH --job-name=<job-name>            
#SBATCH --nodes=1                                
#SBATCH --gpus=0                                
#SBATCH -t 0-24:00                               


python openai_api.py 