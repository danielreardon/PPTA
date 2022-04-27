#!/usr/bin/tcsh

setenv data_dir /fred/oz002/dreardon/ppta_dr3/pptaDataCollection/profiles/
setenv pipeline_dir /fred/oz002/dreardon/ppta_dr3/pipeline/

foreach psr (`ls -1 J* | cut -d'.' -f1`)
	cp $psr.par temp.par
	cat temp.par | grep -v "START" | grep -v "FINISH" | grep -v "FD[123456789]" | grep -v "TN" | grep -v "CLK_CORR_CHAIN" | grep -v "DM[12_ ]" | grep -v "GAUS" | grep -v "EXP" | grep -v "FDJU" | grep -v "UWL_Medusa" | grep -v "NE_SW" | grep -v "fptm" | grep -v "afb" | grep -v "AFB" | grep -v "cpsr2" > $psr.par
	echo "JUMP -f UWL_Medusa 0 1" >> $psr.par
	setenv dm `grep $psr $pipeline_dir/psr_dms.txt | awk '{print $2}'` 
	echo "DM $dm 1" >> $psr.par

	cp $psr.par $data_dir/$psr/
end

rm temp.par
