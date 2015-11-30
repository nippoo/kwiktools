import numpy as np
import phy
import sys

def spike_clusters_into_kwik(scname, kwikname):
	try:
		sc = np.loadtxt(scname, skiprows=1, dtype=int)
	except IOError, OSError:
		print("Error opening file {0} ({1}): {2}".format(scname, e.errno, e.strerror)
		return
