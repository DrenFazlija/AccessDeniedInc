#!/bin/bash

#SBATCH --mail-user=dren.fazlija@l3s.de
#SBATCH --mail-type=ALL                          # Eine Mail wird bei Job-Start/Ende versendet
#SBATCH --job-name=openai_4o             # Name unter dem der Job in der Job-History gespeichert wird
#SBATCH --nodes=1                                # Number of nodes to request
#SBATCH --gpus=0                                # Number of GPUs per job
#SBATCH -t 0-24:00                               # time limit: (D-HH:MM)


python openai_api.py 