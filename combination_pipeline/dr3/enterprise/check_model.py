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
if len(sys.argv) > 1:
    dirname = '/fred/oz002/dreardon/dr2_subband/enterprise/data/chains/singlePsrNoise/'
    dirname += str(sys.argv[1])
else:
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

# Plot histogram for GWB model selection
plt.hist(chain_burn[:, ind_model], bins=2);
plt.show()

#Posterior odds ratio
print(model_utils.odds_ratio(chain_burn[:, ind_model], models=[0,1]))
