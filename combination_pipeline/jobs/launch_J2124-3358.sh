#!/bin/bash
#SBATCH --job-name=timing_J2124-3358
#SBATCH --output=/fred/oz002/dreardon/ppta_dr3/pipeline//jobs/J2124-3358.out
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
#SBATCH --mem-per-cpu=20g
cd /fred/oz002/dreardon/ppta_dr3/pipeline/
./reduce_dr2.sh J2124-3358
./time_dr2.sh J2124-3358
./combine.sh J2124-3358
