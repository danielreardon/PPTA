#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  4 14:53:00 2019

@author: dreardon

Runs basic white, red, and DM noise model for all pulsars in datadir
"""

import os, json, sys
import numpy as np
sys.path.insert(0, "/fred/oz002/dreardon/ppta_dr3/PPTA")
from enterprise_ppta.ppta_model_functions import *
from enterprise_ppta.ppta_utils import *
import glob
from enterprise.pulsar import Pulsar
import matplotlib.pyplot as plt

datadir = "/fred/oz002/dreardon/ppta_dr3/pipeline/dr3/enterprise/data"
parfiles = sorted(glob.glob(datadir + '/' + str(sys.argv[1]) + '*.par'))
timfiles = sorted(glob.glob(datadir + '/' + str(sys.argv[1]) + '*.tim'))

psrs = []
for p, t in zip(parfiles, timfiles):
    print("loading...", p, t)
    psr = Pulsar(p, t, ephem='DE436')
    psrs.append(psr)

nmodels = 1
mod_index = np.arange(nmodels)

    
for psr in psrs:
    print("Running single psr analysis for: ", psr.name)
    pta = dict.fromkeys(mod_index)
    #plt.errorbar(psr.toas/86400, psr.residuals*1e6, psr.toaerrs*1e6, fmt='.')
    # Create a single pulsar noise model, comparing band noise vs. no band noise, for each pulsar
    dm_expdip = True if psr.name == 'J1713+0747' else False
    #pta[0] = models.model_singlepsr_noise(psr, psd='powerlaw', red_var=False, white_vary=True, dm_var=True, dm_psd='powerlaw', dm_expdip=dm_expdip, dm_expdip_tmin=54500, dm_expdip_tmax=54900)  # DM only
    #pta[1] = models.model_singlepsr_noise(psr, psd='powerlaw', red_var=True, white_vary=True, dm_var=False, dm_psd='powerlaw', dm_expdip=dm_expdip, dm_expdip_tmin=54500, dm_expdip_tmax=54900)  # Red only
    #pta[2] = models.model_singlepsr_noise(psr, psd='powerlaw', red_var=True, white_vary=True, dm_var=True, dm_psd='powerlaw', dm_expdip=dm_expdip, dm_expdip_tmin=54500, dm_expdip_tmax=54900)  # Red and DM
    #pta[3] = models.model_singlepsr_noise(psr, psd='powerlaw', red_var=True, white_vary=True, dm_var=False, dm_psd='powerlaw', red_select='band', dm_expdip=dm_expdip, dm_expdip_tmin=54500, dm_expdip_tmax=54900)  # Band only
    pta[0] = model_singlepsr_noise(psr, psd='powerlaw', inc_ecorr=True, red_var=True, white_vary=True, dm_var=True, dm_psd='powerlaw', dm_expdip=dm_expdip, dm_expdip_tmin=54500, dm_expdip_tmax=54900)  # Band and DM
    super_model = hypermodel.HyperModel(pta)
    # Setup a sampler instance.
    # This will add some fanicer stuff than before, like prior draws, 
    # and custom sample groupings.
    outdir = datadir +"/chains/singlePsrNoise/" + psr.name
    sampler = super_model.setup_sampler(outdir=outdir, resume=False)
    # sampler for N steps
    #if psr.name == 'J0437-4715':
    #    N = int(1e7)
    #else:
    #    N = int(1e6)
    N = int(1e6)
    x0 = super_model.initial_sample()
    print(super_model.params)
    # SCAM = Single Component Adaptive Metropolis
    # AM = Adaptive Metropolis
    # DE = Differential Evolution
    ## You can keep all these set at default values
    sampler.sample(x0, N, SCAMweight=30, AMweight=15, DEweight=50, )
    
    chain = np.loadtxt(outdir + '/chain_1.txt')
    burn = int(0.25*chain.shape[0])
    pars = np.loadtxt(outdir + '/pars.txt', dtype=np.unicode_)

    #pp = model_utils.PostProcessing(chain, pars)
    #pp.plot_trace()
    
    #Now, save noise files
    make_noise_files(psr.name,chain[burn:,:], pars,outdir = datadir+'/noiseFiles/')

    chain_burn = chain[burn:,:]    
    ind_model = list(pars).index('nmodel')        
    #Posterior odds ratio
    print(model_utils.odds_ratio(chain_burn[:, ind_model], models=[0,1]))
