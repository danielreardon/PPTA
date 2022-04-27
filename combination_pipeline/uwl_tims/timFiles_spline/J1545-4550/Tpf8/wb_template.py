from __future__ import print_function
from ppspline import *
import os, sys

pulname = sys.argv[1]
obs = sys.argv[2]							# dummy archive to write model to (cp original.fits new.fits && pam -m -T -p new.fits) with a desired freq resolution and bandwidth
modelfile = '%s-fit.spl'%pulname					# model of the profile evolution
outfile = '%s-wb_template.fit'%pulname				# name of the outfile

dp = DataPortrait(obs)
shape = dp.arch.get_data().shape
freqs = np.array(dp.freqs).squeeze()
try:
    model = read_spline_model(modelfile, freqs=freqs, nbin=shape[3])                        # evaluate model for a given array of frequencies (taken from obs), model[0] - model name, model[1] - profiles
    weights = np.ones((1,len(freqs)))				
except TypeError: # single-frequency
    model = read_spline_model(modelfile, freqs=[freqs], nbin=shape[3])                        # evaluate model for a given array of frequencies (taken from obs), model[0] - model name, model[1] - profiles
    weights = np.ones((1, 1))

# reshaping and filling data array with model info, shape of obs (1,1,3328,1024) 	
data = np.zeros(shape)								
model2 = np.reshape(model[1],(shape[2],shape[3]))			 

for isub in range(dp.nsub):
	for ipol in range(dp.npol):
		data[isub,ipol] = model2

# write model to an archive:
# data		- numpy array of the same shape as the obs archive containing model data
# dp.arch   - dummy archive to write to
# DM 		- header DM for the output file
# dmc       - indicate whether the archive is dispersion corrected or not

unload_new_archive(data,dp.arch,outfile=outfile,DM=0,dmc=0,weights=weights)

#unload_new_archive(np.array([[model[1][:;0;:]]),dp.arch,outfile='template.fits',DM=0,dmc=0,weights=weights) # might help skipping the reshaping part:
