from obspy.arclink import Client as C
from obspy.core import UTCDateTime as dt
from datetime import timedelta

c = C(host='seisrequest.iag.usp.br', port=18001, user='marlon')

d = dt.now() - timedelta(days = 1)
print d-3600

s = c.getWaveform('BL', 'BB19B', '', "HH*", d - 3600, d)

s.plot()
