#!/bin/bash
#SBATCH --job-name=timing_J1732-5049
#SBATCH --output=/fred/oz002/dreardon/ppta_dr3/pipeline//jobs/J1732-5049.out
#SBATCH --ntasks=1
#SBATCH --time=16:00:00
#SBATCH --mem-per-cpu=20g
cd /fred/oz002/dreardon/ppta_dr3/pipeline/
./reduce_dr2.sh J1732-5049
./time_dr2.sh J1732-5049
