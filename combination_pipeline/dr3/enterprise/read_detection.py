#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  9 12:19:18 2019

@author: dreardon
"""

import sys
sys.path.insert(0, "/home/dreardon/software/enterprise_extensions/")
from enterprise_extensions import model_utils
import numpy as np
import matplotlib.pyplot as plt

#dirname = '/fred/oz002/dreardon/dr2_subband/enterprise/data/chains/singlePsrLimits/'
#dirname = '/fred/oz002/dreardon/enterprise/data/dark_matter/chains/singlePsrNoise/'
#dirname += str(sys.argv[1])
dirname = '/fred/oz002/dreardon/dr2_subband/enterprise/data/chains/detectGWB/'

chain = np.loadtxt(dirname + '/chain_1.txt')
pars = np.loadtxt(dirname + '/pars.txt', dtype=np.unicode_)
pp = model_utils.PostProcessing(chain, pars)
pp.plot_trace()
plt.show()
#plt.savefig(dirname + '/trace.png')

#pp = model_utils.PostProcessing(chain, pars)

# Plot histgram for GW amplitude
burn = int(0.25*chain.shape[0])
chain_burn = chain[burn:,:]

ind_model = list(pars).index('nmodel')
ind_gwamp = list(pars).index('gw_log10_A')

# ORF = None
#plt.hist(chain_burn[chain_burn[:, ind_model] < 0.5, ind_gwamp], bins=40);

# ORF = Hellings & Downs
plt.hist(chain_burn[chain_burn[:, ind_model] > 0.5, ind_gwamp], bins=40);
plt.show()

# Plot histogram for GWB model selection
plt.hist(chain_burn[:, ind_model], bins=2);
plt.show()

#Savage-Dickey Bayes factor
print(model_utils.bayes_fac(chain_burn[chain_burn[:, ind_model] < 0.5, ind_gwamp], ntol=1))

#Posterior odds ratio
print(model_utils.odds_ratio(chain_burn[:, ind_model], models=[0,1]))
