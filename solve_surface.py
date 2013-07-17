from __future__ import division
import numpy as np
import sympy as sp


h  = 40  * 1000;
b1 = 3.5 * 1000;
b2 = 4.5 * 1000;
r1 = 2.7 * 1000;
r2 = 3.3 * 1000;
u1 = r1 * b1**2;
u2 = r2 * b2**2;

c_v = []
r_v = []
for c in np.arange(b1, b2, 10.0):
	p = 1/c

	x = (1/b1**2)-p**2
	y = p**2 - (1/b2**2)
	
	w = sp.symbols('w')
	eq = sp.tan(h*w*sp.sqrt(x)) - ((u2*sp.sqrt(y)) / (u1*sp.sqrt(x)))

	r = np.absolute(sp.solve(eq, w)[0])
	print c, r
	c_v.append(c)
	r_v.append(r)

#print zip(c_v, r_v)

import pylab as pl
	
pl.plot(r_v, c_v, 'o')
pl.show()