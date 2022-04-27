#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 09:02:29 2019

@author: dreardon

Calculates single psr limits for all pulsars in datadir
"""

import json, sys
import numpy as np
sys.path.insert(0, "/home/dreardon/software/enterprise/")
sys.path.insert(0, "/home/dreardon/software/enterprise_extensions/")
from enterprise_extensions import models, model_utils
from enterprise.pulsar import Pulsar
import glob
import copy
from acor import acor
import matplotlib.pyplot as plt

datadir = "/fred/oz002/dreardon/dr2_subband/enterprise/data"
parfiles = sorted(glob.glob(datadir + '/' + str(sys.argv[1]) + '*1020.par'))
timfiles = sorted(glob.glob(datadir + '/' + str(sys.argv[1]) + '*1020.tim'))

psrs = []
for p, t in zip(parfiles, timfiles):
    print("loading...", p, t)
    psr = Pulsar(p, t, ephem='DE436')
    psrs.append(psr)

noisefiles = sorted(glob.glob(datadir+'/noiseFiles/' + str(sys.argv[1]) + '*.json'))
params = {}
for nf in noisefiles:
    with open(nf, 'r') as fin:
        params.update(json.load(fin))
print(params)        
#psrs_ppta = []
#for psr in psrs:
#    print(psr.name)
#    mask_pta = psr._flags['pta'] == 'PPTA'
#    psr_copy = copy.deepcopy(psr)
#    model_utils.mask_filter(psr_copy, mask_pta)
#    if not psr_copy.toas.any():
#        print("psr has no PPTA data")
#    else:
#        psrs_ppta.append(psr_copy)
        
for psr in psrs:
    psritr = [psr]
    print("Running single psr analysis for: ", psr.name)
    # Create a single pulsar upper limit.
    #red_select = 'band' if psr.name == 'J0437-4715' else None
    pta = models.model_general(psritr, psd='powerlaw', noisedict=params, components=50, 
                               gamma_common=4.33, upper_limit=True, bayesephem=False, 
                               dm_var=True, dm_type='gp', dm_psd='powerlaw', dm_annual=True)

    print(pta.params)
    super_model = model_utils.HyperModel({0: pta})
    # Setup a sampler instance.
    # This will add some fanicer stuff than before, like prior draws, 
    # and custom sample groupings.
    outdir = datadir +"/chains/singlePsrLimits_annualdm/" + psritr[0].name
    sampler = super_model.setup_sampler(outdir=outdir, resume=False)
    #sampler = model_utils.setup_sampler(pta,outdir=outdir, resume=False)
    # sampler for N steps
    N = int(2e6)
    x0 = super_model.initial_sample()
    
    # SCAM = Single Component Adaptive Metropolis
    # AM = Adaptive Metropolis
    # DE = Differential Evolution
    ## You can keep all these set at default values
    sampler.sample(x0, N, SCAMweight=30, AMweight=15, DEweight=50, )
    
    #chain = np.loadtxt(outdir + '/chain_1.txt')
    #burn = int(0.25*chain.shape[0])
    #pars = np.loadtxt(outdir + '/pars.txt', dtype=np.unicode_)

    #pp = model_utils.PostProcessing(chain, pars)
    #pp.plot_trace()
    
#for psr in psrs:
#    psrname = psr.name
#    chain = np.loadtxt(datadir + "/chains/singlePsrLimits/" + psrname + "/chain_1.txt")
#    burn = int(0.5*chain.shape[0])
#    pars = np.loadtxt(datadir + "/chains/singlePsrLimits/" + psrname +'/pars.txt', dtype=np.unicode_)
    #pp = model_utils.PostProcessing(chain, pars)
    #pp.plot_trace()

    # Plot GW amplitude posterior
#    ind = list(pars).index('gw_log10_A')
#    thin = int(acor(chain[burn:,ind])[0])
    
    #plt.hist(chain[burn::thin,ind], bins=40, alpha = 0.2, density=True);
#    ul = model_utils.ul(chain[burn::thin, ind], q=95.0)
#    print(psrname, ul)
   
