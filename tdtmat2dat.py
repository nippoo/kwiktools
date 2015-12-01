# Max Hunter, CortexLab, 2015
# Converts old .mat files produced by TDT into a single flat nsamples x nchannels file
# Example: python tdtmat2dat.py MA024_NN16x2_NN16x2-58_ output.dat

import sys
import os
import re
import os.path as op

import numpy as np
import scipy.io


def natural_sort(l):
    '''Sorts a list 'naturally' i.e. [1, 2, 3, 10, 11] vs [1, 10, 11, 2, 3]'''
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)

def tdtmat2dat(basename, outputdat):
    '''Converts multiple .mat files from TDT to one nsamples * nchannels .dat file'''
    # First, list the filepaths
    basepath = op.dirname(basename)

    source_filenames = []
    for f in os.listdir(basepath):
        if f.startswith(op.basename(basename)):
            source_filenames.append(op.join(basepath, f))

    # Sort them naturally, since os.listdir() is just a regular sort :(
    source_filenames = natural_sort(source_filenames)

    # Open one file to determine length
    init = source_filenames[0]
    print("Loading {0} to determine length".format(init))
    try:
        source = scipy.io.loadmat(init)['wavstream'][0]
    except(IOError, OSError):
        print("Error opening file {0} ({1}): {2}".format(init, e.errno, e.strerror))
        return

    # Create new memmapped .dat file
    n_channels = len(source_filenames)
    chunk_length = len(source[0])
    n_samples = chunk_length * len(source)
    dtype = source[0].dtype

    filesize = dtype.itemsize * n_samples * n_channels / 1073741824

    print("Detected {0} channels, chunk length {1}, {2} samples, dtype {3}, will take up {4:.2f}GB".\
        format(n_channels, chunk_length, n_samples, dtype, filesize))

    print("Creating destination file {0}".format(outputdat))
    try:
        dest = np.memmap(outputdat, dtype=dtype, mode='r+', shape=(n_samples, n_channels))
    except(IOError, OSError):
        print("Error opening file {0} ({1}): {2}".format(outputdat, e.errno, e.strerror))
        return

    # Now open and convert the source files
    for i in range(len(source_filenames)):
        f = source_filenames[i]
        try:
            print("Loading and converting {0}".format(f))
            source = scipy.io.loadmat(f)['wavstream'][0]
            for j in range(len(source)):
                dest[(chunk_length * j):(chunk_length * (j + 1)),i] = source[j][:,0]
        except(IOError, OSError):
            print("Error opening file {0} ({1}): {2}".format(f, e.errno, e.strerror))
            return


if (len(sys.argv) != 3):
    print("Usage: tdtmat2dat.py BASENAME OUTPUTDAT")
else:
    tdtmat2dat(sys.argv[1], sys.argv[2])