#!/bin/bash
#SBATCH --job-name=timing_J1824-2452A
#SBATCH --output=/fred/oz002/dreardon/ppta_dr3/pipeline//jobs/J1824-2452A.out
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
#SBATCH --mem-per-cpu=20g
cd /fred/oz002/dreardon/ppta_dr3/pipeline/
./reduce_dr2.sh J1824-2452A
./time_dr2.sh J1824-2452A
./combine.sh J1824-2452A
