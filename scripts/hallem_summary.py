#!/usr/bin/env python3

"""
To understand the distances between ORN representations of Hallem odors better.
"""

from scipy.spatial.distance import pdist
import matplotlib.pyplot as plt

import drosolf.orns as orns


orns = orns.orns()
fig = plt.figure()
plt.hist(pdist(orns), bins='auto', color='k')
plt.title('Distances between Hallem ORN representations')
plt.xlabel('Euclidean distance')
fig.savefig('hallem_dist_distribution.png')

plt.show()
