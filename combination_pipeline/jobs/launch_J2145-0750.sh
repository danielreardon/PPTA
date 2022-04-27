#!/bin/bash
#SBATCH --job-name=timing_J2145-0750
#SBATCH --output=/fred/oz002/dreardon/ppta_dr3/pipeline//jobs/J2145-0750.out
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
#SBATCH --mem-per-cpu=20g
cd /fred/oz002/dreardon/ppta_dr3/pipeline/
./reduce_dr2.sh J2145-0750
./time_dr2.sh J2145-0750
./combine.sh J2145-0750
