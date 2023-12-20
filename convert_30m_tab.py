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
import numpy as np
import os

"""Initial"""
# get the gildas command line interpreter to issue commands quickly
sic = pyclass.comm
# get the pyclass.gdict object for easy Gildas variable access
g = pyclass.gdict
# sic('SIC MESSAGE GLOBAL ON') # or OFF for less noise
###

### get data files list
uvt_dir = '../NOEMA/pre_merge/'
uvt_dir_out = '../NOEMA/merged/'
#inputfiles = glob('%s/FTS*.30m' %inputdir)

#Define source
source = 'NGC1333'

obs_param = {
    'DCOp': {'freq': 72039.31220, 'Lid': 'L09', 'uvt': 'NGC1333_DCOp_L09.uvt'},
    'HCOp': {'freq': 89188.52470, 'Lid': 'L22', 'uvt': 'NGC1333_HCOp_L22.uvt'},
    'H13COp': {'freq': 86754.28840, 'Lid': 'L17', 'uvt': 'NGC1333_H13COp_L17.uvt'},
    'DCN': {'freq': 72414.69360, 'Lid': 'L10', 'uvt': 'NGC1333_DCN_L10.uvt'},
    'HCN': {'freq': 88631.8475, 'Lid': 'L21', 'uvt': 'NGC1333_HCN_L21.uvt'},
    #'H13CN': {'freq': 86339.9214, 'Lid': 'L10', 'uvt':'-2 1 4 15'},
    #'HC15N': {'freq': 86054.9610, 'Lid': '-35 45', 'uvt':'5 10'},
    'DNC': {'freq': 76305.700, 'Lid': 'L15', 'uvt': 'NGC1333_DNC_L15.uvt'},
    'HNC': {'freq': 90663.56800, 'Lid': 'L23', 'uvt': 'NGC1333_HNC_L23.uvt'},
    #'H2CO': {'freq': 72837.94800, 'Lid': '-35 45', 'uvt':'-5 20'},
    'HC3N_72': {'freq': 72783.82200, 'Lid': 'L11', 'uvt':'NGC1333_HC3N_L11.uvt'},
    'HC3N_91': {'freq': 90979.02300, 'Lid': 'L24', 'uvt':'NGC1333_HC3N_L24.uvt'},
    'N2Dp': {'freq': 77109.24000, 'Lid': 'L16', 'uvt': 'NGC1333_N2Dp_L16.uvt'},
    'N2Hp': {'freq': 93171.61700, 'Lid': 'L28', 'uvt': 'NGC1333_N2Hp_L28.uvt'},
    #'SO2': {'freq': 72758.23500, 'Lid': 'L10', 'uvt':'0 15'},
    'SO2': {'freq': 72758.24340, 'Lid': 'L11', 'uvt':'NGC1333_SO2_L11.uvt'},
    'SiO': {'freq': 86846.96, 'Lid': 'L17', 'uvt': 'NGC1333_SiO_L17.uvt'},
    #
    'CCH_873_a': {'freq':  87284.105, 'Lid': 'L18', 'uvt': 'NGC1333_CCH_a_L18.uvt'},
    'CCH_873_b': {'freq':  87316.925, 'Lid': 'L18', 'uvt': 'NGC1333_CCH_b_L18.uvt'},
    'CCH_873_c': {'freq':  87328.624, 'Lid': 'L18', 'uvt': 'NGC1333_CCH_c_L18.uvt'},
    }

lines = ['HCOp'] #  'HC3N_91']#, 'N2Dp'] #

for line in lines:
    print('[INFO] Reducing line: %s' %line)
    inputfile = '{0}_{1}.30m'.format(source, line)
    sic('file in %s' %inputfile)

    #Get frequency
    freq = obs_param[line]['freq']
    Lid = obs_param[line]['Lid']
    uvt_file = uvt_dir + Lid + '/' + obs_param[line]['uvt']
    ###Define output
    outputfile = obs_param[line]['uvt'].replace('.uvt', '') # '{0}_{1}_{2}'.format(source, line, Lid)

    os.system('rm %s.*' %outputfile)
    sic('file out %s.30m single /overwrite' %outputfile)
    print('[INFO] Removing old output file')
    print('[INFO] Making new output file: %s' %outputfile)
    ####
    #Open and check file
    sic('find') #only obs with refrenecy
    if g.found == 0:
        #raise RuntimeError('No data found!')
        continue
    #Loop through spectral, baseline, and output
    inds = g.idx.ind
    sic('sic message class s-i') #! Speed-up long loops by avoiding too many screen informational messages
    sic('set mode x auto')
    sic('set unit v f')
    for ind in inds:
        sic('get %s' %ind)
        sic('modify freq %s' %freq)
        sic('modify Beam_Eff /Ruze')
        sic('write')
    sic('sic message class s+i') #! Toggle back screen informational messages

    ###Resample as 
    sic('file in %s.30m' %outputfile)
    sic('find /all')
    sic('table {0} new /NOCHECK source /like {1}'.format(outputfile, uvt_file))
    sic('xy_map %s' %outputfile)
    #sic('let name %s' %outputfile)
    #sic('let type lmv')
    #sic('go view')
    
    # copy to folder for merging
    os.system('cp {0}.tab {1}/{2}/.'.format(outputfile, uvt_dir_out, Lid))
    os.system('cp {0} {1}/{2}/.'.format(uvt_file, uvt_dir_out, Lid))


