import numpy as np
from phy.io import KwikModel
import sys

def spike_clusters_into_kwik(scname, kwikname, clustering_name):
    try:
    	print("Loading {0}".format(scname))
    	sc = np.loadtxt(scname, dtype=int) - 1
    	print("Loaded {0} spikes".format(len(sc)))
    except(IOError, OSError):
    	print("Error opening file {0} ({1}): {2}".format(scname, e.errno, e.strerror))
    	exit()

    model = KwikModel(kwikname)
    print("Adding {0} into {1}, clustering {3}".format(sys.argv[1], sys.argv[2], sys.argv[3]))
    model.add_clustering(clustering_name, sc)

if (len(sys.argv) != 4):
    print("Usage: spike_clusters_into_kwik.py SCNAME KWIKNAME CLUSTERINGNAME")
else:
    spike_clusters_into_kwik(sys.argv[1], sys.argv[2], sys.argv[3])
