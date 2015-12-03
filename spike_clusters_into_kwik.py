import numpy as np
from phy.io import KwikModel
import sys
import time

def spike_clusters_into_kwik(scname, kwikname, clustering_name):
    try:
    	print("Loading {0}".format(scname))
    	sc = np.loadtxt(scname, dtype=int) - 1
    	print("Loaded {0} spikes".format(len(sc)))
    except(IOError, OSError) as e:
        print("Error opening file: {1}".format(e))
        return

    model = KwikModel(kwikname)
    print("Adding {0} into {1}, clustering {2}".format(sys.argv[1], sys.argv[2], sys.argv[3]))
    try:
	    model.add_clustering(clustering_name, sc)
    except ValueError:
        print("Overwriting old clustering!")
        time.sleep(5)
        # Hack to switch then overwrite clustering...
        model.add_clustering('123_interim_temp', sc)
        model.clustering = '123_interim_temp'
        model.delete_clustering(clustering_name)
        model.copy_clustering('123_interim_temp', clustering_name)

if (len(sys.argv) != 4):
    print("Usage: spike_clusters_into_kwik.py SCNAME KWIKNAME CLUSTERINGNAME")
else:
    spike_clusters_into_kwik(sys.argv[1], sys.argv[2], sys.argv[3])
