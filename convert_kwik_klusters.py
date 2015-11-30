import numpy as np
import os, sys

from kwiklib import Experiment, convert_dtype

def write_mask(mask, filename, fmt="%f"):
    with open(filename, 'w') as fd:
        fd.write(str(mask.shape[1])+'\n') # number of features
        np.savetxt(fd, mask, fmt=fmt)

def write_fet(fet, filepath):
    with open(filepath, 'w') as fd:
        #header line: number of features
        fd.write('%i\n' % fet.shape[1])
        #next lines: one feature vector per line
        np.savetxt(fd, fet, fmt="%i")

def save_old(exp, shank, dir=None):
    chg = exp.channel_groups[shank]
            
    # Create files in the old format (FET and FMASK)
    fet = chg.spikes.features_masks[...]
    if fet.ndim == 3:
        masks = fet[:,:,1]  # (nsamples, nfet)
        fet = fet[:,:,0]  # (nsamples, nfet)
    else:
        masks = None
    res = chg.spikes.time_samples[:]
    
    times = np.expand_dims(res, axis =1)
    masktimezeros = np.zeros_like(times)
    
    fet = convert_dtype(fet, np.int16)
    fet = np.concatenate((fet, times),axis = 1)
    mainfetfile = os.path.join(dir, exp.name + '.fet.' + str(shank))
    write_fet(fet, mainfetfile)
    
    if masks is not None:
        fmasks = np.concatenate((masks, masktimezeros),axis = 1)
        fmaskfile = os.path.join(dir, exp.name + '.fmask.' + str(shank))
        write_mask(fmasks, fmaskfile, fmt='%f')

if (len(sys.argv) != 4):
    print("Usage: convert_kwik_klusters.py KWIKNAME SHANK OUTPUTDIR")
    exit()
else:
    print("Opening and converting " + str(sys.argv[1]))

e = Experiment(sys.argv[1])
save_old(e, shank=int(sys.argv[2]), dir=sys.argv[3])
