# 'Cleans' ISI between overlapping spikes. If there is any mask overlap
# in space or time between two spikes, one of them will be chosen at random
# to delete.
#
# Usage: isi_clean.py kwik_file.kwik interval_samples
# Dependencies: h5py, numpy
# Max Hunter, CortexLab, 2015

from __future__ import division
import sys
import os.path as op
import numpy as np
import h5py
import random

def overlapping_spikes(ts, masks=None, interval=0, mask_min=0, rand_disc=True):
    keep_idx = np.ones(len(ts), dtype=bool)
    n_discarded = 0
    next_counter = 1000
    idx0 = 0
    idx1 = 1

    def is_overlap(i0, i1):
        # Check for temporal overlap
        if (int(ts[i1]) - int(ts[i0])) >= interval:
            return False
        else:
            # Check for mask overlap
            if np.dot(masks[i0][::3,1],masks[i1][::3,1]) <= mask_min:
                return False
            return True

    while idx1 < len(ts):
        while is_overlap(idx0, idx1):
            if rand_disc == True:
                # pick a random sample to discard
                ch = random.choice([True, False])
            else:
                # always discard first sample
                ch = True

            if ch:
                # discard the first sample and use second sample as comparison
                keep_idx[idx0] = False
                idx0 = idx1
            else:
                # discard second sample keeping first sample as comparison
                keep_idx[idx1] = False
            n_discarded = n_discarded + 1

            # increment second sample and recalculate difference
            idx1 = idx1 + 1
            if (idx1 >= len(ts)):
                break
            diff = (int(ts[idx1]) - int(ts[idx0]))

        idx0 = idx1
        idx1 = idx1 + 1

        # Progress counter
        if (idx0 >= next_counter):
            print('{0:.1f}% complete, discarded {1} spikes ({2:.1f}%)'.
                  format(100*idx0/len(ts), n_discarded, 100*n_discarded/idx0))
            next_counter = int(np.ceil((idx0 + 1) / 1000) * 1000)

    return keep_idx, n_discarded

def convert_to_kv(kwik_file, interval_samples, mask_min, rand_disc):
    '''Converts an input phy-generated .kwik file to be readable by KlustaViewa'''

    print("Opening {0}...".format(kwik_file))
    try:
        kwik = h5py.File(kwik_file, 'r+')
    except(IOError, OSError) as e:
        print("Error opening file: {0}".format(e))
        return

    kwx_file = op.splitext(kwik_file)[0] + '.kwx'
    print("Opening {0}...".format(kwx_file))
    try:
        kwx = h5py.File(kwx_file, 'r+')
    except(IOError, OSError) as e:
        print("Error opening file: {0}".format(e))
        return

    for i in kwik['channel_groups']:
        cgpath = 'channel_groups/' + i + '/'
        fm = kwx[cgpath + 'features_masks']
        ts = kwik[cgpath + 'spikes/time_samples']
        tf = kwik[cgpath + 'spikes/time_fractional']
        rec = kwik[cgpath + 'spikes/recording']
        scpath = cgpath + 'spikes/clusters/'
        sc = [kwik[scpath + i] for i in kwik[scpath]]

        try:
            wr = kwx[cgpath + 'waveforms_raw']
            wf = kwx[cgpath + 'waveforms_filtered']
        except KeyError:
            wr = wf = None

        print("Temporal overlap: {0}. Spatial mask overlap: {1}. Randomly discarding spike: {2}"
              .format(interval_samples, mask_min, ("True" if rand_disc else "False")))

        keep_idx, n_discarded = overlapping_spikes(ts, fm, interval_samples, mask_min, rand_disc)
        newlen = len(fm) - n_discarded

        print("100% complete, discarded {0} spikes ({1:.1f}%). n_spikes: {2} -> {3}."
              .format(n_discarded, 100*n_discarded/len(fm), len(fm), newlen))

        for j in ([fm, ts, tf, rec, wr, wf] + sc):
            if j:
                print("Resizing {0}".format(j.name))
                j_name = j.name
                j_file = j.file
                newj = j[keep_idx,...]
                del j_file[j_name]
                k = j_file.create_dataset(j_name, data=newj)

if (len(sys.argv) != 5):
    print("Usage: isi_clean.py KWIKPATH INTERVAL_SAMPLES MASK_MIN RAND_DISC")
elif (op.splitext(sys.argv[1])[1] != ".kwik"):
    print("File must end in .kwik and be an HDF5 KWIK-format file")
else:
    convert_to_kv(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
