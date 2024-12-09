#!/usr/bin/env python3
from __future__ import annotations
import tempfile
import os
import argparse
import numpy as np
from config import source_catalogue, line_catalogue, uvt_dir, uvt_dir_out, dir_30m

source_print = ''
for key_i in source_catalogue.keys():
    source_print += key_i + ', '

# load parameters used for the preparation of the data
line_name, QN, freq, name_str, QN_str, Lid, vel_width = np.loadtxt(
    line_catalogue,
    dtype="U",
    delimiter=",",
    quotechar='"',
    comments="#", usecols=(0, 1, 2, 3, 4, 9, 10),
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


def line_prepare(source_name, lines, QNs) -> None:
    if source_name in source_catalogue:
        source = source_catalogue[source_name]['source']
        source_out = source_catalogue[source_name]['source_out']
        ra0 = source_catalogue[source_name]['ra0']
        dec0 = source_catalogue[source_name]['dec0']
        vlsr = source_catalogue[source_name]['vlsr']
    else:
        raise ValueError(
            f'Source {source_name} not found in the catalogue: {source_print}')

    for line_i, QN_i in zip(lines, QNs):
        print(f'[INFO] Reducing line: {line_i} with QN: {QN_i}')
        index = get_line_param(line_i, QN_i)
        print(source_out, line_name[index][0], QN[index][0])
        inputfile = '{0}_{1}_{2}.30m'.format(
            source_out, line_name[index][0], QN[index][0])
        # Get frequency
        freq_i = freq[index][0].astype(float)*1e3
        Lid_i = Lid[index][0]  # obs_param[line]['Lid']
        uvt_filename = f'{source_out}_{line_i}_{QN[index][0]}_{Lid_i}.uvt'
        print(uvt_dir, Lid_i, uvt_filename)
        uvt_file = uvt_dir + Lid_i + '/' + uvt_filename
        outputfile = dir_30m + uvt_filename.replace('.uvt', '')

        os.system('rm %s.*' % outputfile)
        fb = tempfile.NamedTemporaryFile(
            delete=True, mode='w+', dir='.', suffix='.class')
        fb.write(f'file in {dir_30m}{inputfile}\n')
        fb.write(f'file out {outputfile}.30m  single /overwrite\n')
        fb.write(f"say [INFO] Removing old output file\n")
        fb.write(f'say "[INFO] Making new output file: {outputfile}"\n')
        fb.write(f'find\n')
        fb.write(f'set mode x auto\n')
        fb.write(f'set unit v f\n')
        fb.write(f'get zero\n')
        fb.write(f'sic message class s-i\n')
        fb.write(f'for i 1 to found\n')
        fb.write(f'  get next\n')
        fb.write(f'  modify linename {name_str[index][0]}\n')
        fb.write(f'  modify freq {freq_i}\n')
        fb.write(f'  modify source {source_out}\n')
        fb.write(f'  modify Beam_Eff /Ruze\n')
        fb.write(f'  write\n')
        fb.write(f'next\n')
        fb.write(f'sic message class s+i\n')
        fb.write(f'file in {outputfile}.30m\n')
        fb.write(f'find /all\n')
        fb.write(f'table {outputfile} new /NOCHECK source /like {uvt_file}\n')
        # fb.write(f'xy_map {outputfile}\n')
        fb.write(f'exit\n')
        fb.flush()
        os.system('class -nw @ %s' % fb.name)
        fb.close()
    # copy to folder for merging
        merged_folder = f'{uvt_dir_out}{Lid_i}'
        if not os.path.exists(merged_folder):
            os.makedirs(merged_folder)
        os.system(
            'cp {0}.tab {1}/.'.format(outputfile, merged_folder))
        os.system('cp {0} {1}/.'.format(uvt_file, merged_folder))


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

    line_prepare(args.source.upper(), args.lines, args.QNs)
