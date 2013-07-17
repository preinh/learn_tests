from __future__ import division
import numpy as np


def ang_freq(h, b1, b2, r1, r2, u1, u2, c):
	return b1*(c**-2 + np.arctan(u2*np.sqrt(c**-2 - 1/float(b2)**2)/(u1*np.sqrt(-c**-2 + b1**(-2)))))/np.float(h)

if __name__ == '__main__':
	h = 40.0 * 1000
	b1 = 3.5 * 1000
	b2 = 4.5 * 1000
	r1 = 2.7 * 1000
	r2 = 3.3 * 1000
	u1 = r1*(b1**2)
	u2 = r2*(b2**2)
	for c in np.arange(3.8, 4.4, 0.2):
		print "c=%s\tw=%s"%(c*1000, ang_freq(h, b1, b2, r1, r2, u1, u2, c*1000))