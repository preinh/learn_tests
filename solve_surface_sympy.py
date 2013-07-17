from __future__ import division
import sympy as s
import numpy as np

h, w, b1, b2, r1, r2, u1, u2, c = s.symbols('h, w, b1, b2, r1, r2, u1, u2, c')

expr = s.tan(h*w*s.sqrt(b1**-2) - c**-2) - (( u2*s.sqrt(c**-2 - b2**-2))  /  (u1*s.sqrt( b1**-2 - c**-2 )))
print 
e = s.solve( expr , w)[0]

print e

eu = e.subs(u1,  r1*(b1**2))
e0 = eu.subs(u2, r2*(b2**2))
e1 = e0.subs(b1, 3.5 * 1000)
e2 = e1.subs(b2, 4.5 * 1000)
e3 = e2.subs(h, 40.0 * 1000)
e4 = e3

e4

e5 = e4.subs(r1, 2.7 * 1000 )
e6 = e5.subs(r2, 3.3 * 1000 )

c_v = []
r_v = []
for i in np.arange(3.0, 6.0, 0.01):
	r = np.absolute(e6.subs(c, i*1000).evalf())
	print "c=%s\tw=%s"%(i*1000, r)
	c_v.append(i*1000)
	r_v.append(r)



from pylab import plot, show

plot(c_v, r_v, 'o')
show()