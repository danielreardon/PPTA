#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 05:54:04 2019

@author: dreardon

Calculates a combined GWB limit with or without Bayesephem for all pulsars in datadir
    can be cumulative or use all pulsars
"""

import json
import numpy as np
from acor import acor
from enterprise_extensions import models, model_utils
from enterprise.pulsar import Pulsar
import matplotlib.pyplot as plt
import glob
import copy

cumulative = False #set to true to run combined limit, adding in one pulsar at a time.
datadir = "/fred/oz002/dreardon/dr2_subband/enterprise/data"
bayesephem = False

if cumulative:
    parfiles = []
    timfiles = []
    ranking = ['J1909-3744', 'J1744-1134', 'J0437-4715', 'J1744-1134', 'J2241-5236', 'J1600-3053', 'J1017-7156']
    for psr in ranking:
        parfiles.append(datadir + '/' + psr + '.par')
        timfiles.append(datadir + '/' + psr + '.tim')
else:
    parfiles = sorted(glob.glob(datadir + '/*.par'))
    timfiles = sorted(glob.glob(datadir + '/*.tim'))

psrs = []
for p, t in zip(parfiles, timfiles):
    print("loading...", p, t)
    psr = Pulsar(p, t, ephem='DE436')
    psrs.append(psr)
    
noisefiles = sorted(glob.glob(datadir+'/noiseFiles/*.json'))
params = {}
for nf in noisefiles:
    with open(nf, 'r') as fin:
        params.update(json.load(fin))

if cumulative:
    nruns = len(psrs)
    #nruns = 10
else:
    nruns = 1 #just run once for all pulsars

for ii in range(0,nruns):
    if cumulative:
        print("Running upper limit for ", ii+1, " pulsars")
        psrsrun = psrs[0:ii+1]
    else:
        psrsrun = psrs
    ## Note that we all still have work to do! This function can do everything
    ## as the routine above, but will not add the DM exponential dip in J1713+0747.
    pta = models.model_general(psrsrun, psd='powerlaw', noisedict=params, components=30, 
                          gamma_common=4.33, upper_limit=True, bayesephem=bayesephem, 
                          dm_var=True, dm_type='gp', dm_psd='powerlaw', dm_annual=False)        
    
    print(pta.params)
    # Setup an instance of a HyperModel.
    # This class currently works with pulsars having unique noise model
    # descriptions for custom proposal distributoons and jumps.
    super_model = model_utils.HyperModel({0: pta})
    
    if cumulative:
        outdir = datadir + "/chains/combinedLimit/" + str(ii) + "_psrs/"
    else:
        outdir = datadir + "/chains/combinedLimit/"
    if bayesephem:
        outdir += 'bayesephem/'
    sampler = super_model.setup_sampler(resume=False, outdir=outdir)
    
    # sampler for N steps
    N = int(1e6) if not bayesephem else int(1e8)
    x0 = super_model.initial_sample()
    
    # sample
    sampler.sample(x0, N, SCAMweight=30, AMweight=15, DEweight=50, )
    
    # Read in chains and parameters
    
    #chain = np.loadtxt(outdir + '/chain_1.txt')
    #burn = int(0.25*chain.shape[0])
    #pars = np.loadtxt(outdir + '/pars.txt', dtype=np.unicode_)
    
    #pp = model_utils.PostProcessing(chain, pars)
    
    # Plot GW amplitude posterior
    #ind = list(pars).index('gw_log10_A')
    #plt.hist(chain[burn:,ind], bins=40, alpha = 0.2, density=True);
    
    # Compute upper limit
    print(model_utils.ul(chain[burn:, ind], q=95.0))
    
#ulArray = []
#ulerrArray = []
#for ii in range(0,nruns):
#    if cumulative:
#        outdir = datadir + "/chains/combinedLimit/" + str(ii) + "_psrs/"
#    else:
#        outdir = datadir + "/chains/combinedLimit/"
#        
#    chain = np.loadtxt(outdir + '/chain_1.txt')
#    pars = np.loadtxt(outdir + '/pars.txt', dtype=np.unicode_)
#    burn = int(0.25*chain.shape[0])
#    
#    #pp = model_utils.PostProcessing(chain, pars)
#    #pp.plot_trace()
#
#    # Plot GW amplitude posterior
#    ind = list(pars).index('gw_log10_A')
#    thin = int(acor(chain[burn:,ind])[0])
#    
#    plt.hist(chain[burn::thin,ind], bins=40, alpha = 0.2, density=True);
#    ul = model_utils.ul(chain[burn::thin, ind], q=95.0)
#    ulArray.append(ul[0])
#    ulerrArray.append(ul[1])
#    #Print upper limit
#    print("Upper limit for ",str(ii+1)," pulsars = ",ul)
#
#plt.show()
#
#plt.scatter(range(1,nruns+1),ulArray)
#plt.fill_between(range(1,nruns+1), np.subtract(ulArray,ulerrArray), np.add(ulArray,ulerrArray))
#plt.yscale('log')
#plt.xlabel('Npsr')
#plt.ylabel('gw_log10_A')
#plt.grid(b=True,axis='y',which='both')
#plt.show()
