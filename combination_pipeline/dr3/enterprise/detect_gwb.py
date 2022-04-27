#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 06:15:24 2019

@author: dreardon

Computes odds ratio for a hellings and downs correlation in the data
"""

import json
import sys
import numpy as np
sys.path.insert(0, "/home/dreardon/software/enterprise_extensions/")
from enterprise_extensions import models, model_utils
from enterprise.pulsar import Pulsar
import matplotlib.pyplot as plt
import glob

datadir = "/fred/oz002/dreardon/dr2_subband/enterprise/data/"
parfiles = sorted(glob.glob(datadir + '/*1020.par'))
timfiles = sorted(glob.glob(datadir + '/*1020.tim'))

psrnames = ['J1909-3744', 'J0437-4715', 'J1713+0747', 'J2241-5236', 'J1744-1134', 'J2129-5721', 'J1600-3053', 'J1832-0836', 'J2145-0750', 'J1017-7156', 'J1125-6014', 'J1446-4701', 'J1545-4550', 'J0711-6830', 'J0613-0200', 'J1022+1001', 'J1857+0943', 'J1730-2304', 'J1603-7202', 'J2129-5721']

psrs = []
for p, t in zip(parfiles, timfiles):
    print("loading...", p, t)
    psr = Pulsar(p, t, ephem='DE436')
    if psr.name in psrnames:
        psrs.append(psr)
    
noisefiles = sorted(glob.glob(datadir+'/noiseFiles/*.json'))
params = {}
for nf in noisefiles:
    with open(nf, 'r') as fin:
        params.update(json.load(fin))

nmodels = 2
mod_index = np.arange(nmodels)

# Make dictionary of PTAs.
pta = dict.fromkeys(mod_index)
pta[0] = models.model_general(psrs, psd='powerlaw', noisedict=params, components=50, 
                      upper_limit=False, bayesephem=True, inc_saturn_orb=True,
                      dm_var=True, dm_type='gp', dm_psd='powerlaw', dm_annual=False)
#pta[1] = models.model_general(psrs, psd='powerlaw', noisedict=params, orf='dipole', components=50,
#                      upper_limit=False, bayesephem=True, inc_saturn_orb=True,
#                      dm_var=True, dm_type='gp', dm_psd='powerlaw', dm_annual=False)
pta[1] = models.model_general(psrs, psd='powerlaw', noisedict=params, orf='hd', components=50, 
                      gamma_common=4.33, upper_limit=False, bayesephem=True, inc_saturn_orb=True,
                      dm_var=True, dm_type='gp', dm_psd='powerlaw', dm_annual=False)
#pta[3] = models.model_general(psrs, psd='powerlaw', noisedict=params, orf='monopole', components=50,
#                      gamma_common=None, upper_limit=False, bayesephem=True, inc_saturn_orb=True,
#                      dm_var=True, dm_type='gp', dm_psd='powerlaw', dm_annual=False)

#print(pta.params)
super_model = model_utils.HyperModel(pta)
print(super_model.params)

outdir = datadir + "/chains/detectGWB_1020_hd/"
sampler = super_model.setup_sampler(resume=False, outdir=outdir)

# sampler for N steps
N = int(1e8)
x0 = super_model.initial_sample()

# sample
sampler.sample(x0, N, SCAMweight=30, AMweight=15, DEweight=50, )

exit()

chain = np.loadtxt(outdir + '/chain_1.txt')
burn = int(0.25*chain.shape[0])
pars = np.loadtxt(outdir + '/pars.txt', dtype=np.unicode_)

pp = model_utils.PostProcessing(chain, pars)

# Plot histgram for GW amplitude
chain_burn = chain[burn:,:]

ind_model = list(pars).index('nmodel')
ind_gwamp = list(pars).index('gw_log10_A')

# ORF = None
#plt.hist(chain_burn[chain_burn[:, ind_model] < 0.5, ind_gwamp], bins=40);

# ORF = Hellings & Downs
plt.hist(chain_burn[chain_burn[:, ind_model] > 0.5, ind_gwamp], bins=40);
plt.show()

# Plot histogram for GWB model selection
plt.hist(chain_burn[:, ind_model], bins=40);
plt.show()

#Savage-Dickey Bayes factor
print(model_utils.bayes_fac(chain_burn[chain_burn[:, ind_model] < 0.5, ind_gwamp], ntol=1))

#Posterior odds ratio
print(model_utils.odds_ratio(chain_burn[:, ind_model], models=[0,2]))
