#!/usr/bin/tcsh

foreach psr (`cat psrs.list`)
#foreach psr (`echo "J1024-0719"`)

	rm -f $psr.bash
        touch $psr.bash

	echo "#\!/bin/bash" >> $psr.bash
	echo "#SBATCH --job-name=noise_1020_$psr" >> $psr.bash
	echo "#SBATCH --output=$PWD/job_output/noise_1020_$psr.out" >> $psr.bash
	echo "#SBATCH --ntasks=1" >> $psr.bash
	echo "#SBATCH --time=24:00:00" >> $psr.bash
	echo "#SBATCH --mem-per-cpu=16g" >> $psr.bash
	echo "#SBATCH --tmp=1G" >> $psr.bash
	echo 'srun cp -r $TEMPO2 $JOBFS/tempo2' >> $psr.bash
	echo 'srun cp -r $TEMPO2_CLOCK_DIR $JOBFS/tempo2_clock_dir' >> $psr.bash
	echo 'srun export TEMPO2=$JOBFS/tempo2' >> $psr.bash
	echo 'srun export TEMPO2_CLOCK_DIR=$JOBFS/tempo2_clock_dir' >> $psr.bash
	echo "srun python singlePsrNoise.py $psr" >> $psr.bash

	sbatch $psr.bash
end
