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
from phy.traces.filter import bandpass_filter, apply_filter
from phy.traces.waveform import WaveformLoader, SpikeLoader

def app_user(handle, path):
    handle[path].require_group('application_data')
    handle[path].require_group('user_data')

def waveform_loader(model, filter_wave):
    """Create a waveform loader."""
    n_samples = (model._metadata['extract_s_before'],
                 model._metadata['extract_s_after'])
    order = model._metadata['filter_butter_order']
    rate = model._metadata['sample_rate']
    low = model._metadata['filter_low']
    high = model._metadata['filter_high_factor'] * rate
    b_filter = bandpass_filter(rate=rate,
                               low=low,
                               high=high,
                               order=order)

    if (filter_wave == True):
        def filter(x):
            return apply_filter(x, b_filter)

        filter_margin = order * 3
    else:
        filter = None
        filter_margin = 0

    dc_offset = model._metadata.get('waveform_dc_offset', None)
    scale_factor = model._metadata.get('waveform_scale_factor', None)
    return WaveformLoader(n_samples=n_samples,
                          filter=filter,
                          filter_margin=filter_margin,
                          dc_offset=dc_offset,
                          scale_factor=scale_factor,
                          )

def convert_to_kv(kwik_file):
    '''Converts an input phy-generated .kwik file to be readable by KlustaViewa'''

    print("Opening {0}...".format(kwik_file))
    try:
        kwik = h5py.File(kwik_file, 'r+')
    except(IOError, OSError) as e:
        print("Error opening file: {1}".format(e))
        return

    print("Writing metadata fields...")
    kwik.require_group('user_data')
    kwik.require_group('application_data')
    kwik.require_group('event_types')

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

    for i in kwik['recordings']:
        rec = kwik['recordings/' + i]
        rec.require_group('high')
        rec.require_group('low')
        app_user(kwik, 'recordings/' + i)

    kwx_file = op.splitext(kwik_file)[0] + '.kwx'
    print("Opening {0}...".format(kwx_file))
    try:
        kwx = h5py.File(kwx_file, 'r+')
    except(IOError, OSError) as e:
        print("Error opening file: {1}".format(e))
        return

    for i in kwik['channel_groups']:
        print("Writing waveforms for channel group {0}...".format(i))
        model = KwikModel(kwik_file, channel_group = int(i))

        sd_attrs = kwik.require_group('application_data/spikedetekt').attrs

        waveforms_nsamples = model._metadata['extract_s_before'] + model._metadata['extract_s_after']
        sd_attrs.create('waveforms_nsamples', waveforms_nsamples)
        sd_attrs.create('nfeatures_per_channel', model._metadata['n_features_per_channel'])

        wl_filtered = waveform_loader(model, filter_wave=True)
        wl_raw = waveform_loader(model, filter_wave=False)

        wl_raw.traces = wl_filtered.traces = model._traces
        wl_raw.channels = wl_filtered.channels = model._channel_order

        waveforms_filtered = SpikeLoader(wl_filtered, model.spike_samples)[:].astype('int16')
        waveforms_raw = SpikeLoader(wl_raw, model.spike_samples)[:].astype('int16')

        wr = kwx['channel_groups/' + i].\
            require_dataset(name='waveforms_raw',
                            shape=waveforms_raw.shape,
                            data=waveforms_raw[...],
                            dtype=waveforms_raw.dtype)

        wr = kwx['channel_groups/' + i].\
            require_dataset(name='waveforms_filtered',
                            shape=waveforms_filtered.shape,
                            data=waveforms_filtered[...],
                            dtype=waveforms_filtered.dtype)

if (len(sys.argv) != 2):
    print("Usage: tdtmat2dat.py KWIKPATH")
elif (op.splitext(sys.argv[1])[1] != ".kwik"):
    print("File must end in .kwik and be an HDF5 KWIK-format file")
else:
    convert_to_kv(sys.argv[1])
