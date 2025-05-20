#!/bin/bash
#SBATCH --job-name=fetch_data       # create a short name for your job
#SBATCH --account=mscbdt2024      # account name
#SBATCH --gpus=1                  # number of GPUs per node
#SBATCH --nodes=1                 # node count
#SBATCH --time=12:00:00           # total run time limit (HH:MM:SS)
#SBATCH --partition=normal        # partition (replace with actual partition name)

CONDA_BASE=/home/tychengal/miniconda3
source $CONDA_BASE/etc/profile.d/conda.sh

conda activate ip
python fetch_data.py -e -hr 24