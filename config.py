# Configuration file to be used in processing the data.
# This file is used to define the source, the source name, the source coordinates, and the VLSR.
#
source_catalogue = {
    'B5': {'source': 'B5*', 'source_out': 'B5', 'ra0': 3.794, 'dec0': 32.865, 'vlsr': 9.0},
    'NGC1333': {'source': 'NGC1333*', 'source_out': 'NGC1333', 'ra0': 3.4862, 'dec0': 31.23, 'vlsr': 5.0},
    'PER2': {'source': 'PER2*', 'source_out': 'Per-emb-2', 'ra0': 3.53806, 'dec0': 30.830, 'vlsr': 5.0},
    'CLOUDH': {'source': 'CLOUDH', 'source_out': 'CloudH', 'ra0': 18.9521, 'dec0': 2.1775, 'vlsr': 45.0}
}

line_catalogue = 'line_catalogue_3mm.csv'
# Folder definitions
uvt_dir = 'D/'
uvt_dir_out = 'D30m/'
dir_30m = '30m/'
inputdir = 'raw_data/'

ignorefiles = ['raw_data/FTSOdp20220220.30m',
               'raw_data/FTSOdp20220731.30m']


# Define lines, frequencies as used with NOEMA data
# vel_ext is better to give a wide range
# vel_win is the velocity window for the baseline, better tight around the line
# obs_param = {
#     '13CS': {'freq': 92494.3080, 'vel_ext': '-35 45', 'vel_win': '5 12'},
#     'CCS_93': {'freq': 93870.0980, 'vel_ext': '-35 45', 'vel_win': '5 12'},
#     'CCD': {'freq': 72107.7205, 'vel_ext': '-35 45', 'vel_win': '5 12'},
#     'c-C3H': {'freq': 91494.3490, 'vel_ext': '-35 45', 'vel_win': '5 12'},
#     'HNCO_87_10K': {'freq': 87925.23700, 'vel_ext': '-35 45', 'vel_win': '5 12'},
#     'HNCO_87_53K': {'freq': 87597.33000, 'vel_ext': '-35 45', 'vel_win': '5 12'},
#     'DCOp': {'freq': 72039.31220, 'vel_ext': '-35 45', 'vel_win': '5 12'},
#     'HCOp': {'freq': 89188.52470, 'vel_ext': '-85 95', 'vel_win': '-45 60'},
#     'H13COp': {'freq': 86754.22840, 'vel_ext': '-35 35', 'vel_win': '-5 20'},
#     'DCN': {'freq': 72414.90500, 'vel_ext': '-35 45', 'vel_win': '-3.5 1.5 5 10 12 16'},
#     'HCN': {'freq': 88631.8475, 'vel_ext': '-55 75', 'vel_win': '-23 30'},
#     'H13CN': {'freq': 86339.9214, 'vel_ext': '-35 45', 'vel_win': '-2 1 4 15'},
#     'HC15N': {'freq': 86054.9610, 'vel_ext': '-35 45', 'vel_win': '5 10'},
#     'H15NC': {'freq': 88865.692, 'vel_ext': '-35 45', 'vel_win': '5 10'},
#     'HN13C': {'freq': 870908500, 'vel_ext': '-35 45', 'vel_win': '5 10'},
#     'DNC': {'freq': 76305.72700, 'vel_ext': '-35 45', 'vel_win': '5 12'},
#     'HNC': {'freq': 90663.56800, 'vel_ext': '-35 45', 'vel_win': '2 15'},
#     'H2CO': {'freq': 72837.94800, 'vel_ext': '-35 45', 'vel_win': '-5 20'},
#     'HC3N_72': {'freq': 72783.82200, 'vel_ext': '-35 45', 'vel_win': '0 15'},
#     'HC3N_91': {'freq': 90979.02300, 'vel_ext': '-35 45', 'vel_win': '0 15'},
#     'N2Dp': {'freq': 77109.24330, 'vel_ext': '5 95', 'vel_win': '31 37 41 56'},
#     'N2Hp': {'freq': 93173.39770, 'vel_ext': '5 95', 'vel_win': '30 58'},
#     'SO2': {'freq': 72758.24340, 'vel_ext': '-35 45', 'vel_win': '0 15'},
#     'SiO': {'freq': 86846.96, 'vel_ext': '-70 95', 'vel_win': '-10 40'},
#     'SO': {'freq': 86093.95000, 'vel_ext': '-70 95', 'vel_win': '-10 40'},
#     'CCH_873_a': {'freq': 87284.105, 'vel_ext': '-35 45', 'vel_win': '2 15'},
#     'CCH_873_b': {'freq': 87316.925, 'vel_ext': '-25 45', 'vel_win': '5 12'},
#     'CCH_873_c': {'freq': 87328.624, 'vel_ext': '-35 45', 'vel_win': '2 15'},
#     'CH3CHO_93.5_a': {'freq': 93580.90910, 'vel_ext': '-35 45', 'vel_win': '5 10'},
#     'CH3CHO_93.5_b': {'freq': 93595.23490, 'vel_ext': '-35 45', 'vel_win': '5 10'},
#     # CH3OH
#     'CH3OH_76.5': {'freq': 76509.684, 'vel_ext': '-35 45', 'vel_win': '5 10'},
#     'CH3OH_92.4': {'freq': 92409.490, 'vel_ext': '-35 45', 'vel_win': '5 10'},
# }
