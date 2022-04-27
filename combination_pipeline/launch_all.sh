#!/usr/bin/tcsh

source set_variables.sh

foreach psr (`cat psrnames.txt | grep -v '^#'`)
	rm -f jobs/launch_$psr.sh
	echo '#\!/bin/bash' > jobs/launch_$psr.sh
	echo '#SBATCH --job-name=timing_'"$psr" >> jobs/launch_$psr.sh
	echo '#SBATCH --output='"$pipeline_dir"'/jobs/'"$psr"'.out' >> jobs/launch_$psr.sh
	echo '#SBATCH --ntasks=1' >> jobs/launch_$psr.sh
	echo '#SBATCH --time=24:00:00' >> jobs/launch_$psr.sh
	echo '#SBATCH --mem-per-cpu=20g' >> jobs/launch_$psr.sh

	echo 'cd '"$pipeline_dir" >> jobs/launch_$psr.sh
	echo './reduce_dr2.sh '"$psr" >> jobs/launch_$psr.sh
	echo './time_dr2.sh '"$psr" >> jobs/launch_$psr.sh
        echo './combine.sh '"$psr" >> jobs/launch_$psr.sh

	sbatch jobs/launch_$psr.sh
end

