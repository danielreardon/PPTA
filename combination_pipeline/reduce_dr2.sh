#!/usr/bin/tcsh

setenv psrname $1
source set_variables.sh

cd $data_dir/$psrname/

### Use MeerGuard to re-zap dr2 profiles, using self-standarding, and reduce channels

if ($psrname == `echo "J0437-4715"`) then
    setenv inputext `echo "dzt8f32"`
    setenv outputext `echo "dzTif8"`
    setenv nchn `echo "8"`
else
    setenv inputext `echo "dzt8f32"`
    setenv outputext `echo "dzTpf4"`
    setenv nchn	`echo "4"`
endif

foreach obs (`ls -1 $data_dir/$psrname/*.$inputext`)
    # python $meerguard/clean_archive.py -a $obs -c 5 -s 5 -o $obs.zap
    setenv dm `grep $psrname $pipeline_dir/psr_dms.txt | awk '{print $2}'`
    pam -d $dm -m $obs.zap
    pam --setnchn $nchn -Fp -e $outputext $obs.zap
    pam -E $pipeline_dir/pars/$psrname.par -m $obs.$outputext
    pam -m -T $obs.$outputext
end

cd $pipeline_dir
