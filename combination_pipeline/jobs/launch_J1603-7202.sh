#!/bin/bash
#SBATCH --job-name=timing_J1603-7202
#SBATCH --output=/fred/oz002/dreardon/ppta_dr3/pipeline//jobs/J1603-7202.out
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
#SBATCH --mem-per-cpu=20g
cd /fred/oz002/dreardon/ppta_dr3/pipeline/
./reduce_dr2.sh J1603-7202
./time_dr2.sh J1603-7202
./combine.sh J1603-7202
