#!/usr/bin/env python

import orns
import pns
import numpy as np
import matplotlib.pyplot as plt

R_orn = orns.orns()
R_pn = pns.pns()

plt.matshow(R_orn)
plt.title('Hallem & Carlson ORN responses')
plt.matshow(R_pn)
plt.title('Synthetic PN responses, input gain control model')

plt.matshow(np.corrcoef(R_orn.T))
plt.title('ORN glomeruli correlations')
plt.matshow(np.corrcoef(R_pn.T))
plt.title('PN glomeruli correlations')

plt.show()
