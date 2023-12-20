"""Reduce IRAM 30-m observaitons"""

"""Need to set up and source the Gildas path"""
## Source gildas installation - outside of python
# source /vol/software/software/astro/gildas/initgildas-nov18a.sh
## Add gildas installation to python path
# export PYTHONPATH=$PYTHONPATH:/vol/software/software/astro/gildas/gildas-exe-nov18a/x86_64-ubuntu18.04-gfortran/python
##

"""Import  pygildas  modeules"""
import pygildas
import pyclass

"""General imports"""
from glob import glob
import argparse
import numpy as np
import os, sys, getopt

"""Initial"""
# get the gildas command line interpreter to issue commands quickly
sic = pyclass.comm
# get the pyclass.gdict object for easy Gildas variable access
g = pyclass.gdict
# sic('SIC MESSAGE GLOBAL ON') # or OFF for less noise
###

#Define lines, frequencies as used with NOEMA data
# vel_ext is better to give a wide range
# vel_win is the velocity window for the baseline, better tight around the line 
obs_param = {
    '13CS': {'freq': 92494.3080, 'vel_ext': '-35 45', 'vel_win':'5 12'},
    'CCS_93': {'freq': 93870.0980, 'vel_ext': '-35 45', 'vel_win':'5 12'},
    'CCD': {'freq': 72107.7205, 'vel_ext': '-35 45', 'vel_win':'5 12'},
    'c-C3H': {'freq': 91494.3490, 'vel_ext': '-35 45', 'vel_win':'5 12'},
    'HNCO_87_10K': {'freq': 87925.23700, 'vel_ext': '-35 45', 'vel_win':'5 12'},
    'HNCO_87_53K': {'freq': 87597.33000, 'vel_ext': '-35 45', 'vel_win':'5 12'},
    'DCOp': {'freq': 72039.31220, 'vel_ext': '-35 45', 'vel_win':'5 12'},
    'HCOp': {'freq': 89188.52470, 'vel_ext': '-85 95', 'vel_win':'-45 60'},
    'H13COp': {'freq': 86754.22840, 'vel_ext': '-35 35', 'vel_win':'-5 20'},
    'DCN': {'freq': 72414.90500, 'vel_ext': '-35 45', 'vel_win':'-3.5 1.5 5 10 12 16'},
    'HCN': {'freq': 88631.8475, 'vel_ext': '-55 75', 'vel_win':'-23 30'},
    'H13CN': {'freq': 86339.9214, 'vel_ext': '-35 45', 'vel_win':'-2 1 4 15'},
    'HC15N': {'freq': 86054.9610, 'vel_ext': '-35 45', 'vel_win':'5 10'},
    'H15NC': {'freq': 88865.692, 'vel_ext': '-35 45', 'vel_win':'5 10'},
    'HN13C': {'freq': 870908500, 'vel_ext': '-35 45', 'vel_win':'5 10'},
    'DNC': {'freq': 76305.72700, 'vel_ext': '-35 45', 'vel_win':'5 12'},
    'HNC': {'freq': 90663.56800, 'vel_ext': '-35 45', 'vel_win':'2 15'},
    'H2CO': {'freq': 72837.94800, 'vel_ext': '-35 45', 'vel_win':'-5 20'},
    'HC3N_72': {'freq': 72783.82200, 'vel_ext': '-35 45', 'vel_win':'0 15'},
    'HC3N_91': {'freq': 90979.02300, 'vel_ext': '-35 45', 'vel_win':'0 15'},
    'N2Dp': {'freq': 77109.24330, 'vel_ext': '-35 45', 'vel_win':'-5 -2 3 9 11 17'},
    'N2Hp': {'freq': 93173.39770, 'vel_ext': '-35 45', 'vel_win':'-4 1 2.5 9.5 10 15'},
    'SO2': {'freq': 72758.24340, 'vel_ext': '-35 45', 'vel_win':'0 15'},
    'SiO': {'freq': 86846.96, 'vel_ext': '-70 95', 'vel_win':'-10 40'},
    'SO': {'freq': 86093.95000, 'vel_ext': '-70 95', 'vel_win':'-10 40'},
    'CCH_873_a': {'freq': 87284.105, 'vel_ext': '-35 45', 'vel_win':'2 15'},
    'CCH_873_b': {'freq': 87316.925, 'vel_ext': '-25 45', 'vel_win':'5 12'},
    'CCH_873_c': {'freq': 87328.624, 'vel_ext': '-35 45', 'vel_win':'2 15'},
    'CH3CHO_93.5_a': {'freq': 93580.90910, 'vel_ext': '-35 45', 'vel_win':'5 10'},
    'CH3CHO_93.5_b': {'freq': 93595.23490, 'vel_ext': '-35 45', 'vel_win':'5 10'},
    # CH3OH
    'CH3OH_76.5': {'freq': 76509.684, 'vel_ext': '-35 45', 'vel_win':'5 10'},
    'CH3OH_92.4': {'freq': 92409.490, 'vel_ext': '-35 45', 'vel_win':'5 10'},
    }
#lines = ['DCOp', 'HCOp', 'H13COp', 'HCN', 'DCN', 'H13CN', 'HC15N',
#         'DNC', 'HNC', 'H2CO', #'CCH_873_b'] #
#         'HC3N_72', 'HC3N_91', 'N2Dp', 'N2Hp', 'SO2']
#lines = ['CH3CHO_93.5_a', 'CH3CHO_93.5_b']

#def main(argv):
def main(source_name, lines):
    # 
    """lines = ['N2Hp']
    try:
        opts, args = getopt.getopt(argv, "hs:l:", ["source=", "lines="])
    except getopt.GetoptError:
        print('process_files.py -s <sourcename> -l <lines>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('process_files.py -s <sourcename> -l <lines>')
            sys.exit()
        elif opt in ("-s", "--sourcename"):
            source_name = arg
        elif opt in ("-l", "--lines"):
            lines = [arg]
    """
    #Define source
    if source_name == 'NGC1333':
        source = 'NGC1333*'
        source_out = 'NGC1333'
        ra0 = 3.4862
        dec0 =  31.23
    elif (source_name == 'B5') | (source_name == 'Barnard5'):
        source = 'B5*'
        source_out = 'B5'
        ra0 = 3.794
        dec0 = 32.865
    elif (source_name == 'Per2') | (source_name == 'Per-emb-2'):
        source = 'PER2*'
        source_out = 'Per-emb-2'
        ra0 = 3.53806
        dec0 = 30.830
    else:
        print('Sources accepted at the moment are: Pper-emb-2, NGC1333, and B5')
        sys.exit(2)

    ### get data files list
    inputdir = 'raw_data/'
    inputfiles = glob('%s/FTS*.30m' %inputdir)

    # Just in case there are files that must be avoided.
    # ignorefiles = ['raw_data/none.30m']
    ignorefiles = ['raw_data/FTSOdp20220220.30m', 'raw_data/FTSOdp20220731.30m']

    for line in lines:
        print('[INFO] Reducing line: %s' %line)
        #Get frequency
        freq = obs_param[line]['freq'] # freqs[line]
        vel_win = obs_param[line]['vel_win'] # vel_window[line]
        vel_ext = obs_param[line]['vel_ext']
        ###Define output
        outputfile = '{0}/{0}_{1}'.format(source_out, line)
        os.system('rm %s.*' %outputfile)
        sic('file out %s.30m single' %outputfile)
        print('[INFO] Removing old output file')
        print('[INFO] Making new output file: %s' %outputfile)
        ####
        ###Loop through files - one file per date
        for inputfile in inputfiles:
            if inputfile in ignorefiles:
                print('[INFO] Ignoring file: %s' %inputfile)
                continue
            #Load file and det defaults
            sic('file in %s' %inputfile)
            sic('set source %s' %source)
            sic('set tele *')
            sic('set line *')

            #Open and check file
            sic('find /frequency %s' %freq) #only obs with refrenecy
            if g.found == 0:
                #raise RuntimeError('No data found!')
                continue

            #Loop through spectral, baseline, and output
            inds = g.idx.ind
            sic('sic message class s-i') #! Speed-up long loops by avoiding too many screen informational messages

            sic('set mode x auto')
            for ind in inds:
                sic('get %s' %ind)
                sic('modify freq %s' %freq)
                sic('modify linename %s' %line)
                sic('modify source %s' %source_out)
                sic('modify projection = {0} {1} ='.format(ra0, dec0))
                sic('modify telescope 30M-MRT')
                # if Tmb is needed
                # sic('modify Beam_Eff /Ruze')
                sic('set unit v')
                sic('extract %s velocity' %vel_ext) #cut out spectra
                sic('set window %s' %vel_win) #cut out spectra
                try:
                    sic('base 1')
                except:
                    continue
                sic('write')
            sic('sic message class s+i') #! Toggle back screen informational messages

        ###Regrid and output to fits file
        print(outputfile)
        sic('file in %s.30m' %outputfile)
        sic('find /all')
        sic('table %s new /nocheck' %outputfile)
        sic('xy_map %s' %outputfile)
        # sic('vector\\fits %s.fits from %s.lmv' %(outputfile, outputfile))
        ###

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description="This scrips processes 30-m observations and it creates cubes.")
    parser.add_argument('-s', '--source', 
        type=str, default='NGC1333', 
        help='Source name to process.')
    parser.add_argument('-l', '--lines', 
        type=str, default=['N2Hp'], nargs='+', 
        help='Line names to process. This can be an array with linenames.')
    args = parser.parse_args()
    
    main(args.source, args.lines)
