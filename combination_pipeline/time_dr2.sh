#!/usr/bin/tcsh

setenv psrname $1
source set_variables.sh

cd $data_dir/$psrname/
cp $pipeline_dir/wb_template.py $data_dir/$psrname
cp $pipeline_dir/wb_models/$psrname-fit.spl $data_dir/$psrname
rm -f all.tim
touch all.tim

if ($psrname == `echo "J0437-4715"`) then
	setenv ext `echo "dzTif8"`
else
	setenv ext `echo "dzTpf4"`
endif

foreach obs (`ls -1 *.$ext`)
	echo "$obs"

	# Get frequency range of archive
        setenv freq `psrstat -c "freq" $obs | cut -d'=' -f2`
	setenv bw `psrstat -c "bw" $obs | cut -d'=' -f2`
	setenv nbin `psrstat -c "nbin" $obs | cut -d'=' -f2 | sed 's/-//'`
        setenv minfreq `awk -v x="$freq" -v y="$bw" 'BEGIN {print x - y/2}'`
        setenv maxfreq `awk -v x="$freq" -v y="$bw" 'BEGIN {print x + y/2}'`
        echo "Using template from $minfreq to $maxfreq with $nbin phase bins"

	if (-e $minfreq.$maxfreq.$nbin.std) then
    		echo "$minfreq.$maxfreq.$nbin.std: template exists"
	else
		echo "Generating template"
        	python wb_template.py $psrname $obs
        	pam --DD -m $psrname-wb_template.fit
        	pam -m -D $psrname-wb_template.fit
        	cp $psrname-wb_template.fit $minfreq.$maxfreq.$nbin.std
  	endif
	
	# Time archive with cropped template
	echo "Timing sub-bands"
	pat -A FDM -f "tempo2 IPTA" -C "snr gof chan" -s $minfreq.$maxfreq.$nbin.std -P $obs >> all.tim	
	
end

echo "FORMAT 1" > $psrname.tim
echo "MODE 1" >> $psrname.tim
grep -v "FORMAT" all.tim | grep -v "MODE" >> $psrname.tim
echo "LOGIC -snr < 20 REJECT" > snr.select

cd $pipeline_dir
python add_flags.py $pipeline_dir/dr2_tims/$psrname.tim $data_dir/$psrname/$psrname.tim

