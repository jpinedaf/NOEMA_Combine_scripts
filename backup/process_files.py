from __future__ import annotations
import tempfile
from glob import glob
import argparse
import numpy as np
import os

from noema_combine.config import source_catalogue, line_catalogue, uvt_dir, uvt_dir_out, dir_30m, ignorefiles, inputdir


source_print = ''
for key_i in source_catalogue.keys():
    source_print += key_i + ', '

# load parameters used for the reduction of the 30m data
line_name, QN, freq, name_str, QN_str, vel_width_30m, vel_width_base_30m = np.loadtxt(
    line_catalogue,
    dtype=str,
    delimiter=",",
    quotechar='"',
    comments="#", usecols=(0, 1, 2, 3, 4, 13, 14),
    unpack=True)


def get_line_param(line_name_i: str, QN_i: str) -> int:
    """
    Function to find the index of the line in the catalogue.
    If the Quantum number is not given, it will return the line only if there is a single entry in the catalogue.
    In the case of multiple line entried for the same molecule, an error is raised.
    """
    if QN_i is None:
        idx = np.where(line_name == line_name_i)[0]
        if len(idx) > 1:
            raise ValueError(
                f'Line name is not unique: {line_name_i}, add the Quantum number (QN).')
    else:
        print(f'line_name: {line_name_i}, QN: {QN_i}')
        idx = np.where((line_name == line_name_i) & (QN_str == QN_i))[0]
    if len(idx) == 0:
        raise ValueError(f'Line not found in the catalogue: {line_name_i}')
    return idx


def line_reduce(source_name, lines, QNs) -> None:
    if source_name in source_catalogue:
        source = source_catalogue[source_name]['source']
        source_out = source_catalogue[source_name]['source_out']
        ra0 = source_catalogue[source_name]['ra0']
        dec0 = source_catalogue[source_name]['dec0']
        vlsr = source_catalogue[source_name]['vlsr']
    else:
        raise ValueError(
            f'Source {source_name} not found in the catalogue: {source_print}')

    freq_corr = (1 - vlsr / 3e5)
    # get data files list
    # inputdir = 'raw_data/'
    inputfiles = glob('%s/*.30m' % inputdir)
    if len(inputfiles) == 0:
        raise ValueError(f'No files found in the input directory: {inputdir}')
    # Just in case there are files that must be avoided.
    # # ignorefiles = ['raw_data/none.30m']
    # ignorefiles = ['raw_data/FTSOdp20220220.30m',
    #                'raw_data/FTSOdp20220731.30m']
    for line_i, QN_i in zip(lines, QNs):
        print(f'[INFO] Reducing line: {line_i} with QN: {QN_i}')
        index = get_line_param(line_i, QN_i)
        print(source_out, line_name[index][0], QN[index][0])
        # Get frequency
        freq_i = freq[index][0].astype(float)*1e3
        dv_base = vel_width_base_30m[index][0].astype(float)
        dv = vel_width_30m[index[0]].astype(float)
        vel_win = '{0:.2f}  {1:.2f}'.format(vlsr - dv_base, vlsr + dv_base)
        vel_ext = '{0:.2f}  {1:.2f}'.format(vlsr - dv, vlsr + dv)
        # Define output
        # outputfile = '{0}/{0}_{1}'.format(source_out, line)
        outputfile = '{0}{1}_{2}_{3}.30m'.format(
            dir_30m, source_out, line_name[index][0], QN[index][0])

        os.system('rm %s.*' % outputfile)
        fb = tempfile.NamedTemporaryFile(
            delete=True, mode='w+', dir='.', suffix='.class')
        fb.write(f'file out {outputfile}  single\n')
        fb.write(f"say [INFO] Removing old output file\n")
        fb.write(f'say "[INFO] Making new output file: {outputfile}"\n')
        ####
        # Loop through files - one file per date
        for inputfile in inputfiles:
            if inputfile in ignorefiles:
                fb.write(f'say "[INFO] Ignoring file: {inputfile}"\n')
                continue
            fb.write(f'say "[INFO] Processing file: {inputfile}"\n')
            # Load file and det defaults
            fb.write(f'file in "{inputfile}"\n')
            fb.write(f"set source {source}\n")
            fb.write(f"set tele *\n")
            fb.write(f"set line *\n")
            # Open and check file
            # only observations with reference frequency
            fb.write('find /frequency {0}\n'.format(freq_i * freq_corr))
            fb.write(f'set mode x auto\n')
            fb.write(f'set unit v\n')
            fb.write(f'get zero\n')
            fb.write(f'sic message class s-i\n')
            fb.write(f'for i 1 to found\n')
            fb.write(f'  get next\n')
            fb.write(f'  modify linename {name_str[index][0]}\n')
            fb.write(f'  modify freq {freq_i}\n')
            fb.write(f'  modify source {source_out}\n')
            fb.write(f'  modify projection = {ra0} {dec0} =\n')
            fb.write(f'  modify telescope 30M-MRT\n')
            fb.write(f'  extract {vel_ext} velocity\n')  # cut out spectra
            fb.write(f'  set window {vel_win}\n')  # define baseline window
            fb.write(f'  base 1\n')  # first order baseline
            fb.write(f'  write\n')
            fb.write(f'next\n')
            # ! Toggle back screen informational messages
            fb.write(f'sic message class s+i\n')
        # Now process the whole dataset available
        # Regrid and output to fits file
        print(outputfile)
        fb.write(f'file in {outputfile}\n')
        fb.write(f'find /all\n')
        fb.write(f'table {outputfile[:-4]} new /nocheck\n')
        fb.write(f'xy_map {outputfile[:-4]}\n')
        fb.write(f'exit\n')
        fb.flush()
        os.system(f'rm -f {outputfile}')
        os.system(f'class -nw @ {fb.name}')
        fb.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This scrips processes 30-m observations and it creates cubes.")
    parser.add_argument('-s', '--source',
                        type=str, default='CLOUDH',
                        help='Source name to process.')
    parser.add_argument('-l', '--lines',
                        type=str, default=['N2Hp'], nargs='+',
                        help='Line names to process. This can be an array with linenames.')
    parser.add_argument('-qn', '--QNs',
                        type=str, default=[None], nargs='+',
                        help='Quantum number strings. This can be an array.')
    args = parser.parse_args()

    line_reduce(args.source.upper(), args.lines, args.QNs)
