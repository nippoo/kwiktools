# Conversion tool from phy<=0.2.0-generated KWIK format to KlustaViewa>=0.3.0
# Writes needed metadata fields and extracts waveforms into .kwx file
#
# Usage: phy2kv.py kwik_file.kwik
# Dependencies: phy 0.2.0, h5py, numpy
# Max Hunter, CortexLab, 2015

import sys
import os.path as op
import numpy as np
import h5py
from phy.io.kwik import KwikModel

def app_user(handle, path):
    handle[path].require_group('application_data')
    handle[path].require_group('user_data')

def convert_to_kv(kwik_file):
    '''Converts an input phy-generated .kwik file to be readable by KlustaViewa'''

    print("Opening {0}...".format(kwik_file))
    try:
        kwik = h5py.File(kwik_file, 'r+')
    except(IOError, OSError) as e:
        print("Error opening file {0}: {1}".format(kwik_file, e))
        return

    print("Writing metadata fields...")
    kwik.require_group('user_data')
    for i in kwik['channel_groups']:
        group_path = 'channel_groups/' + i
        app_user(kwik, group_path)

        for j in kwik[group_path + '/channels']:
            app_user(kwik, group_path + '/channels/' + j)

        for j in kwik[group_path + '/clusters']:
            for k in kwik[group_path + '/clusters/' + j]:
                cluster_path = group_path + '/clusters/' + j + '/' + k
                app_user(kwik, cluster_path)
                kwik[cluster_path].require_group('quality_measures')

        for j in kwik[group_path + '/cluster_groups']:
            for k in kwik[group_path + '/cluster_groups/' + j]:
                cluster_group_path = group_path + '/cluster_groups/' + j + '/' + k
                app_user(kwik, cluster_group_path)

        kwik[group_path + '/spikes'].require_group('features_masks').attrs.create\
            ('hdf5_path', '{{kwx}}/channel_groups/{0}/features_masks'.format(i).encode('ascii'))
        kwik[group_path + '/spikes'].require_group('waveforms_raw').attrs.create\
            ('hdf5_path', '{{kwx}}/channel_groups/{0}/waveforms_raw'.format(i).encode('ascii'))
        kwik[group_path + '/spikes'].require_group('waveforms_filtered').attrs.create\
            ('hdf5_path', '{{kwx}}/channel_groups/{0}/waveforms_filtered'.format(i).encode('ascii'))

    kwik.close()

    print("Writing waveforms_filtered...")
    model = KwikModel(kwik_file)

if (len(sys.argv) != 2):
    print("Usage: tdtmat2dat.py KWIKPATH")
elif (op.splitext(sys.argv[1])[1] != ".kwik"):
    print("File must end in .kwik and be an HDF5 KWIK-format file")
else:
    convert_to_kv(sys.argv[1])
