#!/bin/bash
#SBATCH --job-name=timing_J1909-3744
#SBATCH --output=/fred/oz002/dreardon/ppta_dr3/pipeline//jobs/J1909-3744.out
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
#SBATCH --mem-per-cpu=20g
cd /fred/oz002/dreardon/ppta_dr3/pipeline/
./reduce_dr2.sh J1909-3744
./time_dr2.sh J1909-3744
./combine.sh J1909-3744
