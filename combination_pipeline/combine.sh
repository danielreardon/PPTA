#!/usr/bin/tcsh

setenv psrname $1
source set_variables.sh

# Copy .tim file to dr3 directory and append UWL data
cp $data_dir/$psrname/$psrname.flagged.tim $pipeline_dir/dr3/$psrname.tim

if ($psrname == `echo "J0437-4715"`) then
        cat $pipeline_dir/dr3/$psrname.tim | grep -v "CPSR2" | grep -v "WBCORR" | grep -v "PDFB1" > $pipeline_dir/dr3/test.tim
        mv $pipeline_dir/dr3/test.tim $pipeline_dir/dr3/$psrname.tim
        
        sed '/^uwl_220207_051055/ s/./#&/' $pipeline_dir/uwl_tims/$psrname.tim > $pipeline_dir/uwl_tims/test.tim
        mv $pipeline_dir/uwl_tims/test.tim $pipeline_dir/uwl_tims/$psrname.tim
endif

cat $pipeline_dir/uwl_tims/$psrname.tim >> $pipeline_dir/dr3/$psrname.tim

# Copy .par file to dr3 directory and add Medusa JUMPs
cp $pipeline_dir/pars/$psrname.par $pipeline_dir/dr3/$psrname.par
echo "JUMP -MJD_59199_59233_UWL -1 0 1" >> $pipeline_dir/dr3/$psrname.par

setenv timname $pipeline_dir/dr3/$psrname.tim

# Add flags for JUMP from 59199 to 59223
awk '{if (($3 > 59199) && ($3 < 59223)) print $0, "-MJD_59199_59233_UWL -1"; else print $0}' $timname  > tmp.tim
# Delete data between 59335 and 59340
awk '{if (($3 > 59335) && ($3 < 59340)) print "# ", $0; else print $0}' tmp.tim  > tmp2.tim
mv tmp2.tim tmp.tim
# Add subband flags
sed '/.sbA/ s/$/ -group UWL_sbA/' tmp.tim > tmp2.tim
mv tmp2.tim tmp.tim
sed '/.sbB/ s/$/ -group UWL_sbB/' tmp.tim > tmp2.tim
mv tmp2.tim tmp.tim
sed '/.sbC/ s/$/ -group UWL_sbC/' tmp.tim > tmp2.tim
mv tmp2.tim tmp.tim
sed '/.sbD/ s/$/ -group UWL_sbD/' tmp.tim > tmp2.tim
mv tmp2.tim tmp.tim
sed '/.sbE/ s/$/ -group UWL_sbE/' tmp.tim > tmp2.tim
mv tmp2.tim tmp.tim
sed '/.sbF/ s/$/ -group UWL_sbF/' tmp.tim > tmp2.tim
mv tmp2.tim tmp.tim
sed '/.sbG/ s/$/ -group UWL_sbG/' tmp.tim > tmp2.tim
mv tmp2.tim tmp.tim
sed '/.sbH/ s/$/ -group UWL_sbH/' tmp.tim > tmp2.tim
mv tmp2.tim tmp.tim

mv tmp.tim $timname

