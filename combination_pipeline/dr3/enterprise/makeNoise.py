import json, sys, os
import numpy as np

def make_noise_files(psrname, chain, pars, outdir='noisefiles/'):
    x = {}
    for ct, par in enumerate(pars):
        x[par] = np.median(chain[:, ct])

    os.system('mkdir -p {}'.format(outdir))
    with open(outdir + '/{}_noise.json'.format(psrname), 'w') as fout:
        json.dump(x, fout, sort_keys=True, indent=4, separators=(',', ': '))


datadir = '/fred/oz002/dreardon/dr2_subband/enterprise/data/'
outdir = datadir + 'chains/singlePsrNoise_1020/' + str(sys.argv[1])

chain = np.loadtxt(outdir + '/chain_1.txt')
burn = int(0.25*chain.shape[0])
pars = np.loadtxt(outdir + '/pars.txt', dtype=np.unicode_)

#Now, save noise files
make_noise_files(str(sys.argv[1]),chain[burn:,:], pars,outdir = datadir+'/noiseFiles_1020/')
