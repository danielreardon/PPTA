import functools
from collections import OrderedDict
import numpy as np
import types
from enterprise import constants as const
from enterprise.signals import (deterministic_signals, gp_signals, parameter,
                                selections, signal_base, utils, white_signals)
from enterprise.signals.signal_base import LogLikelihood
from enterprise_extensions import deterministic
from enterprise_extensions import dropout as do
from enterprise_extensions import model_utils
from enterprise_extensions.blocks import (bwm_block, bwm_sglpsr_block,
                                          chromatic_noise_block,
                                          common_red_noise_block,
                                          dm_noise_block, red_noise_block)
from enterprise_extensions.chromatic.solar_wind import solar_wind_block
from enterprise_extensions.timing import timing_block
from enterprise.signals import gp_bases as gpb
from enterprise.signals import gp_priors as gpp
from enterprise_extensions import deterministic as ee_deterministic

def white_noise_block(vary=False, inc_ecorr=False, gp_ecorr=False,
                      efac1=False, select='backend', tnequad=False, name=None):
    """
    Returns the white noise block of the model:
        1. EFAC per backend/receiver system
        2. EQUAD per backend/receiver system
        3. ECORR per backend/receiver system
    :param vary:
        If set to true we vary these parameters
        with uniform priors. Otherwise they are set to constants
        with values to be set later.
    :param inc_ecorr:
        include ECORR, needed for NANOGrav channelized TOAs
    :param gp_ecorr:
        whether to use the Gaussian process model for ECORR
    :param efac1:
        use a strong prior on EFAC = Normal(mu=1, stdev=0.1)
    :param tnequad:
        Whether to use the TempoNest definition of EQUAD. Defaults to False to
        follow Tempo, Tempo2 and Pint definition.
    """

    if select == 'backend':
        # define selection by observing backend
        backend = selections.Selection(selections.by_backend)
        # define selection by nanograv backends
        backend_ng = selections.Selection(selections.nanograv_backends)
        # backend_ch = selections.Selection(channelized_backends)
    else:
        # define no selection
        backend = selections.Selection(selections.no_selection)

    # white noise parameters
    if vary:
        if efac1:
            efac = parameter.Normal(1.0, 0.1)
        else:
            efac = parameter.Uniform(0.01, 10.0)
        equad = parameter.Uniform(-8.5, -5)
        if inc_ecorr:
            ecorr = parameter.Uniform(-8.5, -5)
    else:
        efac = parameter.Constant()
        equad = parameter.Constant()
        if inc_ecorr:
            ecorr = parameter.Constant()

    # white noise signals
    if tnequad:
        efeq = white_signals.MeasurementNoise(efac=efac,
                                              selection=backend, name=name)
        efeq += white_signals.TNEquadNoise(log10_tnequad=equad,
                                           selection=backend, name=name)
    else:
        efeq = white_signals.MeasurementNoise(efac=efac, log10_t2equad=equad,
                                              selection=backend, name=name)

    if inc_ecorr:
        if gp_ecorr:
            if name is None:
                ec = gp_signals.EcorrBasisModel(log10_ecorr=ecorr,
                                                selection=backend)
            else:
                ec = gp_signals.EcorrBasisModel(log10_ecorr=ecorr,
                                                selection=backend, name=name)

        else:
            ec = white_signals.EcorrKernelNoise(log10_ecorr=ecorr,
                                                selection=backend,
                                                name=name)
    # combine signals
    if inc_ecorr:
        s = efeq + ec
    elif not inc_ecorr:
        s = efeq

    return s

def model_singlepsr_noise(psr, tm_var=False, tm_linear=False,
                          tmparam_list=None,
                          red_var=True, psd='powerlaw', red_select=None,
                          noisedict=None, tm_svd=False, tm_norm=True,
                          white_vary=True, components=30, upper_limit=False,
                          is_wideband=False, use_dmdata=False, tnequad=False,
                          dmjump_var=False, gamma_val=None, dm_var=False,
                          dm_type='gp', dmgp_kernel='diag', dm_psd='powerlaw',
                          dm_nondiag_kernel='periodic', dmx_data=None,
                          dm_annual=False, gamma_dm_val=None,
                          dm_dt=15, dm_df=200,
                          chrom_gp=False, chrom_gp_kernel='nondiag',
                          chrom_psd='powerlaw', chrom_idx=4, chrom_quad=False,
                          chrom_kernel='periodic',
                          chrom_dt=15, chrom_df=200,
                          dm_expdip=False, dmexp_sign='negative',
                          dm_expdip_idx=2,
                          dm_expdip_tmin=None, dm_expdip_tmax=None,
                          num_dmdips=1, dmdip_seqname=None,
                          dm_cusp=False, dm_cusp_sign='negative',
                          dm_cusp_idx=2, dm_cusp_sym=False,
                          dm_cusp_tmin=None, dm_cusp_tmax=None,
                          num_dm_cusps=1, dm_cusp_seqname=None,
                          inc_ecorr=False, dm_dual_cusp=False, dm_dual_cusp_tmin=None,
                          dm_dual_cusp_tmax=None, dm_dual_cusp_sym=False,
                          dm_dual_cusp_idx1=2, dm_dual_cusp_idx2=4,
                          dm_dual_cusp_sign='negative', num_dm_dual_cusps=1,
                          dm_dual_cusp_seqname=None,
                          dm_sw_deter=False, dm_sw_gp=False,
                          swgp_prior=None, swgp_basis=None,
                          coefficients=False, extra_sigs=None,
                          psr_model=False, factorized_like=False,
                          Tspan=None, fact_like_gamma=13./3, gw_components=10,
                          fact_like_logmin=None, fact_like_logmax=None,
                          select='backend', tm_marg=False, dense_like=False):
    """
    Single pulsar noise model.
    :param psr: enterprise pulsar object
    :param tm_var: explicitly vary the timing model parameters
    :param tm_linear: vary the timing model in the linear approximation
    :param tmparam_list: an explicit list of timing model parameters to vary
    :param red_var: include red noise in the model
    :param psd: red noise psd model
    :param noisedict: dictionary of noise parameters
    :param tm_svd: boolean for svd-stabilised timing model design matrix
    :param tm_norm: normalize the timing model, or provide custom normalization
    :param white_vary: boolean for varying white noise or keeping fixed
    :param components: number of modes in Fourier domain processes
    :param dm_components: number of modes in Fourier domain DM processes
    :param upper_limit: whether to do an upper-limit analysis
    :param is_wideband: whether input TOAs are wideband TOAs; will exclude
           ecorr from the white noise model
    :param use_dmdata: whether to use DM data (WidebandTimingModel) if
           is_wideband
    :param gamma_val: red noise spectral index to fix
    :param dm_var: whether to explicitly model DM-variations
    :param dm_type: gaussian process ('gp') or dmx ('dmx')
    :param dmgp_kernel: diagonal in frequency or non-diagonal
    :param dm_psd: power-spectral density of DM variations
    :param dm_nondiag_kernel: type of time-domain DM GP kernel
    :param dmx_data: supply the DMX data from par files
    :param dm_annual: include an annual DM signal
    :param gamma_dm_val: spectral index of power-law DM variations
    :param dm_dt: time-scale for DM linear interpolation basis (days)
    :param dm_df: frequency-scale for DM linear interpolation basis (MHz)
    :param chrom_gp: include general chromatic noise
    :param chrom_gp_kernel: GP kernel type to use in chrom ['diag','nondiag']
    :param chrom_psd: power-spectral density of chromatic noise
        ['powerlaw','tprocess','free_spectrum']
    :param chrom_idx: frequency scaling of chromatic noise
    :param chrom_kernel: Type of 'nondiag' time-domain chrom GP kernel to use
        ['periodic', 'sq_exp','periodic_rfband', 'sq_exp_rfband']
    :param chrom_quad: Whether to add a quadratic chromatic term. Boolean
    :param chrom_dt: time-scale for chromatic linear interpolation basis (days)
    :param chrom_df: frequency-scale for chromatic linear interpolation basis (MHz)
    :param dm_expdip: inclue a DM exponential dip
    :param dmexp_sign: set the sign parameter for dip
    :param dm_expdip_idx: chromatic index of exponential dip
    :param dm_expdip_tmin: sampling minimum of DM dip epoch
    :param dm_expdip_tmax: sampling maximum of DM dip epoch
    :param num_dmdips: number of dm exponential dips
    :param dmdip_seqname: name of dip sequence
    :param dm_cusp: include a DM exponential cusp
    :param dm_cusp_sign: set the sign parameter for cusp
    :param dm_cusp_idx: chromatic index of exponential cusp
    :param dm_cusp_tmin: sampling minimum of DM cusp epoch
    :param dm_cusp_tmax: sampling maximum of DM cusp epoch
    :param dm_cusp_sym: make exponential cusp symmetric
    :param num_dm_cusps: number of dm exponential cusps
    :param dm_cusp_seqname: name of cusp sequence
    :param dm_dual_cusp: include a DM cusp with two chromatic indices
    :param dm_dual_cusp_tmin: sampling minimum of DM dual cusp epoch
    :param dm_dual_cusp_tmax: sampling maximum of DM dual cusp epoch
    :param dm_dual_cusp_idx1: first chromatic index of DM dual cusp
    :param dm_dual_cusp_idx2: second chromatic index of DM dual cusp
    :param dm_dual_cusp_sym: make dual cusp symmetric
    :param dm_dual_cusp_sign: set the sign parameter for dual cusp
    :param num_dm_dual_cusps: number of DM dual cusps
    :param dm_dual_cusp_seqname: name of dual cusp sequence
    :param dm_scattering: whether to explicitly model DM scattering variations
    :param dm_sw_deter: use the deterministic solar wind model
    :param dm_sw_gp: add a Gaussian process perturbation to the deterministic
        solar wind model.
    :param swgp_prior: prior is currently set automatically
    :param swgp_basis: ['powerlaw', 'periodic', 'sq_exp']
    :param coefficients: explicitly include latent coefficients in model
    :param psr_model: Return the enterprise model instantiated on the pulsar
        rather than an instantiated PTA object, i.e. model(psr) rather than
        PTA(model(psr)).
    :param factorized_like: Whether to run a factorized likelihood analyis Boolean
    :param gw_components: number of modes in Fourier domain for a common
           process in a factorized likelihood calculation.
    :param fact_like_gamma: fixed common process spectral index
    :param fact_like_logmin: specify lower prior for common psd. This is a prior on log10_rho
        if common_psd is 'spectrum', else it is a prior on log10 amplitude
    :param fact_like_logmax: specify upper prior for common psd. This is a prior on log10_rho
        if common_psd is 'spectrum', else it is a prior on log10 amplitude
    :param Tspan: time baseline used to determine Fourier GP frequencies
    :param extra_sigs: Any additional `enterprise` signals to be added to the
        model.
    :param tm_marg: Use marginalized timing model. In many cases this will speed
        up the likelihood calculation significantly.
    :param dense_like: Use dense or sparse functions to evalute lnlikelihood
    :return s: single pulsar noise model
    """
    amp_prior = 'uniform' if upper_limit else 'log-uniform'

    # timing model
    if not tm_var:
        if (is_wideband and use_dmdata):
            if dmjump_var:
                dmjump = parameter.Uniform(pmin=-0.005, pmax=0.005)
            else:
                dmjump = parameter.Constant()
            if white_vary:
                dmefac = parameter.Uniform(pmin=0.1, pmax=10.0)
                log10_dmequad = parameter.Uniform(pmin=-7.0, pmax=0.0)
                # dmjump = parameter.Uniform(pmin=-0.005, pmax=0.005)
            else:
                dmefac = parameter.Constant()
                log10_dmequad = parameter.Constant()
                # dmjump = parameter.Constant()
            s = gp_signals.WidebandTimingModel(dmefac=dmefac,
                                               log10_dmequad=log10_dmequad, dmjump=dmjump,
                                               dmefac_selection=selections.Selection(
                                                   selections.by_backend),
                                               log10_dmequad_selection=selections.Selection(
                                                   selections.by_backend),
                                               dmjump_selection=selections.Selection(
                                                   selections.by_frontend))
        else:
            if tm_marg:
                s = gp_signals.MarginalizingTimingModel(use_svd=tm_svd)
            else:
                s = gp_signals.TimingModel(use_svd=tm_svd, normed=tm_norm,
                                           coefficients=coefficients)
    else:
        # create new attribute for enterprise pulsar object
        psr.tmparams_orig = OrderedDict.fromkeys(psr.t2pulsar.pars())
        for key in psr.tmparams_orig:
            psr.tmparams_orig[key] = (psr.t2pulsar[key].val,
                                      psr.t2pulsar[key].err)
        if not tm_linear:
            s = timing_block(tmparam_list=tmparam_list)
        else:
            pass

    # red noise and common process
    if factorized_like:
        if Tspan is None:
            msg = 'Must Timespan to match amongst all pulsars when doing '
            msg += 'a factorized likelihood analysis.'
            raise ValueError(msg)

        s += common_red_noise_block(psd=psd, prior=amp_prior,
                                    Tspan=Tspan, components=gw_components,
                                    gamma_val=fact_like_gamma, delta_val=None,
                                    orf=None, name='gw',
                                    coefficients=coefficients,
                                    pshift=False, pseed=None,
                                    logmin=fact_like_logmin, logmax=fact_like_logmax)

    if red_var:
        s += red_noise_block(psd=psd, prior=amp_prior, Tspan=Tspan,
                             components=components, gamma_val=gamma_val,
                             coefficients=coefficients, select=red_select)

    # DM variations
    if dm_var:
        if dm_type == 'gp':
            if dmgp_kernel == 'diag':
                s += dm_noise_block(gp_kernel=dmgp_kernel, psd=dm_psd,
                                    prior=amp_prior, components=components,
                                    gamma_val=gamma_dm_val,
                                    coefficients=coefficients)
            elif dmgp_kernel == 'nondiag':
                s += dm_noise_block(gp_kernel=dmgp_kernel,
                                    nondiag_kernel=dm_nondiag_kernel,
                                    dt=dm_dt, df=dm_df,
                                    coefficients=coefficients)
        elif dm_type == 'dmx':
            s += chrom.dmx_signal(dmx_data=dmx_data[psr.name])
        if dm_annual:
            s += chrom.dm_annual_signal()
        if chrom_gp:
            s += chromatic_noise_block(gp_kernel=chrom_gp_kernel,
                                       psd=chrom_psd, idx=chrom_idx,
                                       components=components,
                                       nondiag_kernel=chrom_kernel,
                                       dt=chrom_dt, df=chrom_df,
                                       include_quadratic=chrom_quad,
                                       coefficients=coefficients)

        if dm_expdip:
            if dm_expdip_tmin is None and dm_expdip_tmax is None:
                tmin = [psr.toas.min() / const.day for ii in range(num_dmdips)]
                tmax = [psr.toas.max() / const.day for ii in range(num_dmdips)]
            else:
                tmin = (dm_expdip_tmin if isinstance(dm_expdip_tmin, list)
                        else [dm_expdip_tmin])
                tmax = (dm_expdip_tmax if isinstance(dm_expdip_tmax, list)
                        else [dm_expdip_tmax])
            if dmdip_seqname is not None:
                dmdipname_base = (['dmexp_' + nm for nm in dmdip_seqname]
                                  if isinstance(dmdip_seqname, list)
                                  else ['dmexp_' + dmdip_seqname])
            else:
                dmdipname_base = ['dmexp_{0}'.format(ii+1)
                                  for ii in range(num_dmdips)]

            dm_expdip_idx = (dm_expdip_idx if isinstance(dm_expdip_idx, list)
                             else [dm_expdip_idx])
            for dd in range(num_dmdips):
                s += chrom.dm_exponential_dip(tmin=tmin[dd], tmax=tmax[dd],
                                              idx=dm_expdip_idx[dd],
                                              sign=dmexp_sign,
                                              name=dmdipname_base[dd])
        if dm_cusp:
            if dm_cusp_tmin is None and dm_cusp_tmax is None:
                tmin = [psr.toas.min() / const.day for ii in range(num_dm_cusps)]
                tmax = [psr.toas.max() / const.day for ii in range(num_dm_cusps)]
            else:
                tmin = (dm_cusp_tmin if isinstance(dm_cusp_tmin, list)
                        else [dm_cusp_tmin])
                tmax = (dm_cusp_tmax if isinstance(dm_cusp_tmax, list)
                        else [dm_cusp_tmax])
            if dm_cusp_seqname is not None:
                cusp_name_base = 'dm_cusp_'+dm_cusp_seqname+'_'
            else:
                cusp_name_base = 'dm_cusp_'
            dm_cusp_idx = (dm_cusp_idx if isinstance(dm_cusp_idx, list)
                           else [dm_cusp_idx])
            dm_cusp_sign = (dm_cusp_sign if isinstance(dm_cusp_sign, list)
                            else [dm_cusp_sign])
            for dd in range(1, num_dm_cusps+1):
                s += chrom.dm_exponential_cusp(tmin=tmin[dd-1],
                                               tmax=tmax[dd-1],
                                               idx=dm_cusp_idx[dd-1],
                                               sign=dm_cusp_sign[dd-1],
                                               symmetric=dm_cusp_sym,
                                               name=cusp_name_base+str(dd))
        if dm_dual_cusp:
            if dm_dual_cusp_tmin is None and dm_cusp_tmax is None:
                tmin = psr.toas.min() / const.day
                tmax = psr.toas.max() / const.day
            else:
                tmin = dm_dual_cusp_tmin
                tmax = dm_dual_cusp_tmax
            if dm_dual_cusp_seqname is not None:
                dual_cusp_name_base = 'dm_dual_cusp_'+dm_cusp_seqname+'_'
            else:
                dual_cusp_name_base = 'dm_dual_cusp_'
            for dd in range(1, num_dm_dual_cusps+1):
                s += chrom.dm_dual_exp_cusp(tmin=tmin, tmax=tmax,
                                            idx1=dm_dual_cusp_idx1,
                                            idx2=dm_dual_cusp_idx2,
                                            sign=dm_dual_cusp_sign,
                                            symmetric=dm_dual_cusp_sym,
                                            name=dual_cusp_name_base+str(dd))
        if dm_sw_deter:
            Tspan = psr.toas.max() - psr.toas.min()
            s += solar_wind_block(ACE_prior=True, include_swgp=dm_sw_gp,
                                  swgp_prior=swgp_prior, swgp_basis=swgp_basis,
                                  Tspan=Tspan)

    if extra_sigs is not None:
        s += extra_sigs

    # adding white-noise, and acting on psr objects
    s2 = s + white_noise_block(vary=white_vary, inc_ecorr=inc_ecorr,
                               tnequad=tnequad, select=select)
    model = s2(psr)
    if psr_model:
        Model = s2

    if psr_model:
        return Model
    else:
        # set up PTA
        if dense_like:
            pta = signal_base.PTA([model], lnlikelihood=signal_base.LogLikelihoodDenseCholesky)
        else:
            pta = signal_base.PTA([model])

        # set white noise parameters
        if not white_vary or (is_wideband and use_dmdata):
            if noisedict is None:
                print('No noise dictionary provided!...')
            else:
                noisedict = noisedict
                pta.set_default_params(noisedict)

        return pta
