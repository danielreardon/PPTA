#!/bin/bash
#SBATCH --job-name=timing_J1939+2134
#SBATCH --output=/fred/oz002/dreardon/ppta_dr3/pipeline//jobs/J1939+2134.out
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
#SBATCH --mem-per-cpu=20g
cd /fred/oz002/dreardon/ppta_dr3/pipeline/
./reduce_dr2.sh J1939+2134
./time_dr2.sh J1939+2134
./combine.sh J1939+2134
