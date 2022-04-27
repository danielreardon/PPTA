#!/usr/bin/tcsh

foreach psr (`cat psrs.list`)

	echo $psr
	#python plotGW.py $psr /
	#python plotGW.py $psr _annualdm/
	python makeNoise.py $psr

end
