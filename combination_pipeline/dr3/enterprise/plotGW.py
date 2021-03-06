#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  9 12:19:18 2019

@author: dreardon
"""

import sys
import os.path
sys.path.insert(0, "/home/dreardon/software/enterprise_extensions/")
from enterprise_extensions import model_utils
import numpy as np
import matplotlib.pyplot as plt
from acor import acor

if len(sys.argv) > 1:
    dirname = '/fred/oz002/dreardon/dr2_subband/enterprise/data/chains/singlePsrLimits' + str(sys.argv[2])
    #dirname = '/fred/oz002/dreardon/dr2_subband/enterprise/data/chains/singlePsrNoise/'
    dirname += str(sys.argv[1])
    try:
        if os.path.getctime(dirname + "/chain_1.0.txt") < os.path.getctime(dirname + "/chain_1.txt"):
            chain = np.loadtxt(dirname + "/chain_1.txt")
        else:
            chain = np.loadtxt(dirname + "/chain_1.0.txt")
    except:
        try:
            chain = np.loadtxt(dirname + "/chain_1.txt")
        except:
            chain = np.loadtxt(dirname + "/chain_1.0.txt")
    #try:
    #    chain = np.loadtxt(dirname + "/chain_1.0.txt")
    #except:
    #    chain = np.loadtxt(dirname + "/chain_1.txt")
else:
    dirname = '/fred/oz002/dreardon/dr2_subband/enterprise/data/chains/limit_1020/'
    #dirname = '/fred/oz002/dreardon/dr2_subband/enterprise/data/chains/limit_1020_hd/'
    #dirname = '/fred/oz002/dreardon/dr2_subband/enterprise/data/chains/limit_1020_noSaturn/'
    chain = np.loadtxt(dirname + "/chain_1.0.txt")

burn = int(0.25*chain.shape[0])
pars = np.loadtxt(dirname +'/pars.txt', dtype=np.unicode_)
pp = model_utils.PostProcessing(chain, pars)
#pp.plot_trace()
#plt.show()

# Plot GW amplitude posterior
try:
    ind = list(pars).index('gw_log10_A')
except:
    try:
        ind = list(pars).index('common_log10_A')
    except:
        ind = list(pars).index('gwhd_log10_A')
thin = int(acor(chain[burn:,ind])[0])

#plt.hist(chain[burn::thin,ind], bins=40, alpha = 0.2, density=True);
#plt.show()
#ul = model_utils.ul(chain[burn::thin, ind], q=95.0)
#ul = model_utils.ul(chain[burn:, ind], q=95.0)
#print(ul)

#exit()

if len(sys.argv) <= 1:
    dirname = '/fred/oz002/dreardon/dr2_subband/enterprise/data/chains/detectGWB_1020_only/'
else:
    exit()

try:
    chain = np.loadtxt(dirname + "/chain_1.0.txt")
except:
    chain = np.loadtxt(dirname + "/chain_1.txt")
#try:
#    chain = np.loadtxt(dirname + "/chain_1.txt")
#except:
#    chain = np.loadtxt(dirname + "/chain_1.0.txt")
burn = int(0.25*chain.shape[0])
pars = np.loadtxt(dirname +'/pars.txt', dtype=np.unicode_)
pp = model_utils.PostProcessing(chain, pars)
#pp.plot_trace()
#plt.show()
#ind = list(pars).index('nmodel')
#plt.hist(chain[burn:,ind], bins=40, alpha = 0.2, density=True);
#plt.title('nmodel: 0 uncorrelated, 1 dipole, 2 hd')
#plt.show()

# Plot GW amplitude posterior
#ind = list(pars).index('common_log10_A')
#plt.hist(chain[burn:,ind], bins=40, alpha = 0.2, density=True);
#plt.title('common, uncorrelated')
#plt.show()
#ul = model_utils.ul(chain[burn:, ind], q=95.0)
#print(ul)

#ind = list(pars).index('monopole_log10_A')
#plt.hist(chain[burn:,ind], bins=40, alpha = 0.2, density=True);
#plt.title('monopole')
#plt.show()

#ind = list(pars).index('dipole_log10_A')
#plt.hist(chain[burn:,ind], bins=40, alpha = 0.2, density=True);
#plt.title('dipole')
#plt.show()

#ind = list(pars).index('gwhd_gamma')
#plt.hist(chain[burn:,ind], bins=40, alpha = 0.2, density=True);
#plt.title('GW Hellings + Downs, gamma')
#plt.show()

ind = list(pars).index('gwhd_log10_A')
plt.hist(chain[burn:,ind], bins=40, alpha = 0.2, density=True);
plt.title('GW Hellings + Downs, amp')
plt.show()


# Plot histgram for GW amplitude
chain_burn = chain[burn:,:]
#chain_burn = pp.chain

ind_model = list(pars).index('nmodel')
ind_gwamp = ind

#Savage-Dickey Bayes factor
print(model_utils.bayes_fac(chain_burn[chain_burn[:, ind_model] < 0.5, ind_gwamp], ntol=1))

#Posterior odds ratio
#print("dipole odds")
#print(model_utils.odds_ratio(chain_burn[:, ind_model], models=[0,1]))
#print("HD odds")
#print(model_utils.odds_ratio(chain_burn[:, ind_model], models=[0,1]))
#print("monopole odds")
#print(model_utils.odds_ratio(chain_burn[:, ind_model], models=[0,3]))

   
