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
    dirname = '/fred/oz002/dreardon/dr2_subband/enterprise/data/chains/limit_huge/'

chain = np.loadtxt(dirname + '/chain_1.0.txt')
pars = np.loadtxt(dirname + '/pars.txt', dtype=np.unicode_)
pp = model_utils.PostProcessing(chain, pars)
pp.plot_trace()
plt.show()
#plt.savefig(dirname + '/trace.png')
