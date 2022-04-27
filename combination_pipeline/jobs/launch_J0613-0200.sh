#!/bin/bash
#SBATCH --job-name=timing_J0613-0200
#SBATCH --output=/fred/oz002/dreardon/ppta_dr3/pipeline//jobs/J0613-0200.out
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
#SBATCH --mem-per-cpu=20g
cd /fred/oz002/dreardon/ppta_dr3/pipeline/
./reduce_dr2.sh J0613-0200
./time_dr2.sh J0613-0200
./combine.sh J0613-0200
