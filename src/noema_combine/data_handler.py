from __future__ import annotations
import tempfile
import os
from glob import glob
import numpy as np
import configparser

try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

config = configparser.ConfigParser()
config_file = "config.ini"
if os.path.isfile(config_file):
    config.read(config_file)
else:
    pack_file = files("noema_combine").joinpath(config_file)
    config.read(pack_file)

file_source_catalogue = config["catalogues"]["source_catalogue"]
if os.path.isfile(file_source_catalogue) == False:
    file_source_catalogue = files(
        "noema_combine").joinpath(file_source_catalogue)
    if os.path.isfile(file_source_catalogue) == False:
        raise FileNotFoundError(
            f"File not found: {config['catalogues']['source_catalogue']}"
        )

file_line_catalogue = config["catalogues"]["line_catalogue"]
if os.path.isfile(file_line_catalogue) == False:
    file_line_catalogue = files("noema_combine").joinpath(file_line_catalogue)
    if os.path.isfile(file_line_catalogue) == False:
        raise FileNotFoundError(
            f"File not found: {config['catalogues']['line_catalogue']}"
        )


(
    list_source_name,
    list_source_key,
    list_source_out,
    list_RA,
    list_Dec,
    list_Vlsr,
) = np.loadtxt(
    file_source_catalogue,
    dtype="U",
    delimiter=",",
    quotechar='"',
    comments="#",
    unpack=True,
)

source_print = ""
for key_i in list_source_name:
    source_print += key_i + ", "

ignorefiles = []
# config['file_handling']['ignorefiles']
for key, item in config.items("file_handling"):
    if key.startswith("ignorefiles"):
        ignorefiles.append(item)


# load parameters used for the preparation of the data
(
    line_name,
    QN,
    freq,
    name_str,
    QN_str,
    Lid,
    vel_width,
    vel_width_30m,
    vel_width_base_30m,
) = np.loadtxt(
    file_line_catalogue,
    dtype="U",
    delimiter=",",
    quotechar='"',
    comments="#",
    usecols=(0, 1, 2, 3, 4, 9, 10, 13, 14),
    unpack=True,
)

uvt_dir = config["folders"]["uvt_dir"]
dir_30m = config["folders"]["dir_30m"]
uvt_dir_out = config["folders"]["uvt_dir_out"]
inputdir = config["folders"]["inputdir"]


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
                f"Line name is not unique: {line_name_i}, add the Quantum number (QN)."
            )
    else:
        print(f"line_name: {line_name_i}, QN: {QN_i}")
        idx = np.where((line_name == line_name_i) & (QN_str == QN_i))[0]
    if len(idx) == 0:
        raise ValueError(f"Line not found in the catalogue: {line_name_i}")
    return idx


def get_source_param(source_name: str) -> tuple[str, str, str, float, float, float]:
    """
    Function to find the index of the source in the catalogue.
    It returns the values in the catalogue for the source.
    """
    print(f"source_name: {source_name}")
    idx = np.where((source_name == list_source_name))[0]
    if len(idx) == 0:
        raise ValueError(
            f"Source {source_name} not found in the catalogue: {source_print}"
        )
    # return idx
    return (
        list_source_name[idx],
        list_source_key[idx],
        list_source_out[idx],
        list_RA[idx].astype(float),
        list_Dec[idx].astype(float),
        list_Vlsr[idx].astype(float),
    )


def get_uvt_file(source_name: str, line_name: str, QN: str, Lid: str) -> str:
    uvt_filename = f"{source_name}_{line_name}_{QN}_{Lid}.uvt"
    return uvt_filename


def get_30m_file(source_out: str, line_name: str, QN: str) -> str:
    outputfile = "{0}{1}_{2}_{3}.30m".format(
        dir_30m, source_out, line_name, QN)
    return outputfile


def line_prepare_merge(source_name: str, line_i: str, QN_i: str) -> None:
    """
    Function to prepare the 30m data for the merging.
    It will ensure that the 30m data are in Tmb and in the correct frequency.
    It will use the uvt file from the NOEMA observations to regrid the
    speactral axis of the 30m data.

    parameters:
    -----------
    source_name: str
        Name of the source to reduce
    line: list
        List of the line to reduce
    QNs: list
        List of the Quantum numbers of the line to reduce
    """
    _, _, source_out, _, _, _ = get_source_param(source_name)

    print(f"[INFO] Reducing line: {line_i} with QN: {QN_i}")
    index = get_line_param(line_i, QN_i)
    print(source_out, line_name[index][0], QN[index][0])
    inputfile = "{0}_{1}_{2}.30m".format(
        source_out, line_name[index][0], QN[index][0])
    freq_i = freq[index][0].astype(float) * 1e3
    Lid_i = Lid[index][0]
    uvt_filename = get_uvt_file(source_out, line_i, QN[index][0], Lid_i)
    # uvt_filename = f'{source_out}_{line_i}_{QN[index][0]}_{Lid_i}.uvt'
    print(uvt_dir, Lid_i, uvt_filename)
    uvt_file = uvt_dir + Lid_i + "/" + uvt_filename
    outputfile = dir_30m + uvt_filename.replace(".uvt", "")
    file_30m = get_30m_file(source_out, line_name[index][0], QN[index][0])

    os.system(f"rm {outputfile}.*")
    fb = tempfile.NamedTemporaryFile(
        delete=True, mode="w+", dir=".", suffix=".class")
    fb.write(f"file in {file_30m}\n")
    fb.write(f"file out {outputfile}.30m  single /overwrite\n")
    fb.write(f"say [INFO] Removing old output file\n")
    fb.write(f'say "[INFO] Making new output file: {outputfile}"\n')
    fb.write(f"find\n")
    fb.write(f"set mode x auto\n")
    fb.write(f"set unit v f\n")
    fb.write(f"get zero\n")
    fb.write(f"sic message class s-i\n")
    fb.write(f"for i 1 to found\n")
    fb.write(f"  get next\n")
    fb.write(f"  modify linename {name_str[index][0]}\n")
    fb.write(f"  modify freq {freq_i}\n")
    fb.write(f"  modify source {source_out}\n")
    fb.write(f"  modify Beam_Eff /Ruze\n")
    fb.write(f"  write\n")
    fb.write(f"next\n")
    fb.write(f"sic message class s+i\n")
    fb.write(f"file in {outputfile}.30m\n")
    fb.write(f"find /all\n")
    fb.write(f"table {outputfile} new /NOCHECK source /like {uvt_file}\n")
    # fb.write(f'xy_map {outputfile}\n')
    fb.write(f"exit\n")
    fb.flush()
    os.system("class -nw @ %s" % fb.name)
    fb.close()
    # copy to folder for merging
    merged_folder = f"{uvt_dir_out}{Lid_i}"
    if not os.path.exists(merged_folder):
        os.makedirs(merged_folder)
    os.system("cp {0}.tab {1}/.".format(outputfile, merged_folder))
    os.system("cp {0} {1}/.".format(uvt_file, merged_folder))


def line_reduce_30m(source_name: str, lines: str, QNs: str) -> None:
    source, source_find, source_out, ra0, dec0, vlsr = get_source_param(
        source_name)

    freq_corr = 1 - vlsr / 3e5
    # get data files list
    inputfiles = glob(f"{inputdir}/*.30m")
    if len(inputfiles) == 0:
        raise ValueError(f"No files found in the input directory: {inputdir}")

    for line_i, QN_i in zip(lines, QNs):
        print(f"[INFO] Reducing line: {line_i} with QN: {QN_i}")
        index = get_line_param(line_i, QN_i)
        print(source_out, line_name[index][0], QN[index][0])
        # Get frequency
        freq_i = freq[index][0].astype(float) * 1e3
        dv_base = vel_width_base_30m[index][0].astype(float)
        dv = vel_width_30m[index[0]].astype(float)
        vel_win = "{0:.2f}  {1:.2f}".format(vlsr - dv_base, vlsr + dv_base)
        vel_ext = "{0:.2f}  {1:.2f}".format(vlsr - dv, vlsr + dv)
        # Define output
        outputfile = get_30m_file(
            source_out, line_name[index][0], QN[index][0])
        os.system("rm %s.*" % outputfile)
        fb = tempfile.NamedTemporaryFile(
            delete=True, mode="w+", dir=".", suffix=".class"
        )
        fb.write(f"file out {outputfile}  single\n")
        fb.write(f"say [INFO] Removing old output file\n")
        fb.write(f'say "[INFO] Making new output file: {outputfile}"\n')
        ####
        # Loop through files - one file per date
        for inputfile in inputfiles:
            for ignorefile in ignorefiles:
                if ignorefile in inputfile:
                    fb.write(f'say "[INFO] Ignoring file: {inputfile}"\n')
                    continue
            fb.write(f'say "[INFO] Processing file: {inputfile}"\n')
            # Load file and det defaults
            fb.write(f'file in "{inputfile}"\n')
            fb.write(f"set source {source_find}\n")
            fb.write(f"set tele *\n")
            fb.write(f"set line *\n")
            # Open and check file
            # only observations with reference frequency
            fb.write("find /frequency {0}\n".format(freq_i * freq_corr))
            fb.write(f"set mode x auto\n")
            fb.write(f"set unit v\n")
            fb.write(f"get zero\n")
            fb.write(f"sic message class s-i\n")
            fb.write(f"for i 1 to found\n")
            fb.write(f"  get next\n")
            fb.write(f"  modify linename {name_str[index][0]}\n")
            fb.write(f"  modify freq {freq_i}\n")
            fb.write(f"  modify source {source_out}\n")
            fb.write(f"  modify projection = {ra0} {dec0} =\n")
            fb.write(f"  modify telescope 30M-MRT\n")
            fb.write(f"  extract {vel_ext} velocity\n")  # cut out spectra
            fb.write(f"  set window {vel_win}\n")  # define baseline window
            fb.write(f"  base 1\n")  # first order baseline
            fb.write(f"  write\n")
            fb.write(f"next\n")
            # ! Toggle back screen informational messages
            fb.write(f"sic message class s+i\n")
        # Now process the whole dataset available
        # Regrid and output to fits file
        print(outputfile)
        fb.write(f"file in {outputfile}\n")
        fb.write(f"find /all\n")
        fb.write(f"table {outputfile[:-4]} new /nocheck\n")
        fb.write(f"xy_map {outputfile[:-4]}\n")
        fb.write(f"exit\n")
        fb.flush()
        os.system(f"rm -f {outputfile}")
        os.system(f"class -nw @ {fb.name}")
        fb.close()
