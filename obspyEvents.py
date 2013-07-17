import os
from obspy.core import UTCDateTime
from obspy.arclink import Client as arcClient
from obspy.iris import Client as irisClient
from obspy.sac import SacIO
from obspy.taup import taup
#from iagTaup import IagTaup
import urllib2
from xml.dom.minidom import parseString
from obspy.core import util


class ObspyEvents :
    
    
    def __init__(self, startTime, endTime, catalog='ISC', lat=None, lon=None, minRadius=None, maxRadius=None, minDepth=None, maxDepth=None, 
                 minMag=None, maxMag=None, magType=None):
        
        print "\nObspy Events 1.0\n"
        
        # to TravelTimes
        self.beforeP = 240
        self.afterS = 1500
        
        self.iris = irisClient()
        
        #self.arclink = arcClient(host="seisrequest.iag.usp.br", port=18001, user="ObsPy POET")
        self.arclink = arcClient(host="10.110.1.132", port=18001, user="ObsPy POET")

        try:

            self.events = self.iris.getEvents(format="xml", catalog=catalog, lat=lat, lon=lon, minradius=minRadius, maxradius=maxRadius,
                        mindepth=minDepth, maxdepth=maxDepth, minmag=minMag, maxmag=maxMag, magtype=magType,
                        starttime=startTime, endtime=endTime, preferredonly=True)
        except:

            print "No events found."
        
        self.xmlEvt = parseString(self.events)
                
    def getNumberOfEvents(self):
        nEvents = len(self.xmlEvt.getElementsByTagName('magnitude'))
        return nEvents
    
    def getTime(self, id):
        xmlTime = self.xmlEvt.getElementsByTagName('time')[id].toxml()
        time=xmlTime.replace('<time>','').replace('</time>','').replace('<value>','').replace('</value>','').replace(' ','').replace('\n','')
        return time[:-5].replace('T',' ')
    
    def getTimeUTC(self, id):
        xmlTime = self.xmlEvt.getElementsByTagName('time')[id].toxml()
        time=xmlTime.replace('<time>','').replace('</time>','').replace('<value>','').replace('</value>','').replace(' ','').replace('\n','')
        return time
    
    def getRegion(self, id):
        xmlRegion = self.xmlEvt.getElementsByTagName('text')[id].toxml()
        region=xmlRegion.replace('<text>','').replace('</text>','').replace('\n','').replace('\n','')
        return region
    
    def getLatitude(self, id):
        xmlLat = self.xmlEvt.getElementsByTagName('latitude')[id].toxml()
        latitude=xmlLat.replace('<latitude>','').replace('</latitude>','').replace('<value>','').replace('</value>','').replace(' ','').replace('\n','')
        return latitude
    
    def getLongitude(self, id):
        xmlLon = self.xmlEvt.getElementsByTagName('longitude')[id].toxml()
        longitude=xmlLon.replace('<longitude>','').replace('</longitude>','').replace('<value>','').replace('</value>','').replace(' ','').replace('\n','')
        return longitude
    
    def getMagnitude(self, id):
        xmlMag = self.xmlEvt.getElementsByTagName('mag')[id].toxml()
        magnitude=xmlMag.replace('<mag>','').replace('</mag>','').replace('<value>','').replace('</value>','').replace(' ','').replace('\n','')
        return magnitude
    
    def getDepth(self, id):
        xmlDep = self.xmlEvt.getElementsByTagName('depth')[id].toxml()
        depth=xmlDep.replace('<depth>','').replace('</depth>','').replace('<value>','').replace('</value>','').replace(' ','').replace('\n','')
        return depth
    
    def showCatalog(self):
        print self.getNumberOfEvents(), "events loaded.\n"
        for i in range(self.getNumberOfEvents()):
            print self.getTime(i), self.getRegion(i), self.getLatitude(i), self.getLongitude(i), self.getDepth(i), self.getMagnitude(i)
        print '\n'
    
    def writeCatalog(self, catalogFile):
        evtCatalog = file(catalogFile, "w")
        for i in range(self.getNumberOfEvents()):
            evtLine = self.getTime(i)+" "+self.getRegion(i)+" "+self.getLatitude(i)+" "+self.getLongitude(i)+" "+self.getDepth(i)+" "+self.getMagnitude(i)+"\n"
            evtCatalog.writelines(evtLine)
        print "catalog saved.\n"
        evtCatalog.close()
        
    def downloadLocalData(self, net, evtTime, evtLat, evtLon, evtDep, mag, fileFormat):
        
        if fileFormat == "MSEED" :
            fileFormat = str.lower(fileFormat)

        print "Setting local DB..."
        stations = self.arclink.getStations(evtTime, evtTime + 3600, net)
        #return stations
        
        for station in stations:
            staName = station["code"]
            staLon = station["longitude"]
            staLat = station["latitude"]
            staElev = station["elevation"]

            #delta = taup.locations2degrees(evtLat, evtLon, staLat, staLon) # delta stores distance in degrees
            delta = util.locations2degrees(evtLat, evtLon, staLat, staLon) # delta stores distance in degrees
            itp = taup() # calling IAG Taup class 
            itp.getTravelTimes(delta, evtDep)
            pTime = itp.P()
            sTime = itp.S()
            # to use in sac headers...
            seisTime = evtTime + pTime - self.beforeP
            originTime = self.beforeP - pTime
            
            fileTime = str(evtTime).replace('T', '-').replace(':', '-')[:-8]

            try:

                st = self.arclink.getWaveform(net, staName, "*", "*", evtTime + pTime - self.beforeP, evtTime + sTime + self.afterS)
                print "\nData found for station "+staName
                st.merge(method=1, fill_value="interpolate")
            
                try:
                    os.mkdir(staName)
                except:
                    pass
            
                os.mkdir(staName+"/"+fileTime)

                for tr in st :
                    loc = str(tr.stats.location)
                    fileName = staName+"/"+fileTime+"/"+net+"."+staName+"."+loc+"."+str(tr.stats.channel)+"."+fileTime+"."+fileFormat
                    tr.write(fileName, fileFormat)
                    print fileName, "saved."
                    if fileFormat == "SAC":
                        self.fillSACHeaders(fileName, seisTime, originTime, evtLat, evtLon, evtDep, mag, staLat, staLon, staElev)

            except:
                pass
                  
    def fillSACHeaders(self, fileName, seisTime, originTime, evtLat, evtLon, evtDep, mag, staLat, staLon, staElev):
        
        sac = SacIO(fileName)
        sac.SetHvalue("evla", evtLat)
        sac.SetHvalue("evlo", evtLon)
        sac.SetHvalue("evdp", evtDep)
        sac.SetHvalue("stla", staLat)
        sac.SetHvalue("stlo", staLon)
        sac.SetHvalue("stel", staElev)
        sac.SetHvalue("mag", mag)
        sac.SetHvalue("lcalda", True)
        pMark = sac.GetHvalue("b") + self.beforeP
        sac.SetHvalue("a", pMark)
        sac.SetHvalue("ka", "p iaspei")
        sMark = sac.GetHvalue("e") - self.afterS
        sac.SetHvalue("t0", sMark)
        sac.SetHvalue("kt0", "s iaspei")
        sac.SetHvalue("o", originTime)
        sac.SetHvalue("nzhour", seisTime.hour)
        sac.SetHvalue("nzmin", seisTime.minute)
        sac.SetHvalue("nzsec", seisTime.second)
        sac.SetHvalue("nzmsec", seisTime.microsecond/1000)
        _cmp = str(sac.GetHvalue("kcmpnm"))
        if _cmp[2] == "Z" :
            sac.SetHvalue("cmpaz", 0)
            sac.SetHvalue("cmpinc", 0)
        elif _cmp[2] == "N" :
            sac.SetHvalue("cmpaz", 0)
            sac.SetHvalue("cmpinc", 90)
        else :
            sac.SetHvalue("cmpaz", 90)
            sac.SetHvalue("cmpinc", 90)
        sac.WriteSacHeader(fileName)
        #print "SAC Headers filled" 
       
    def downloadRemoteData(self, net, evtTime, evtLat, evtLon, evtDep, mag, fileFormat):
        
        acceptedStations = ["SPB", "CPUP", "LPAZ", "PLCA", "LCO", "LVC", "OTAV", "PTGA", "RCBR", "SAML", "SDV", "TRQA", "CAN", "FDF", "HDC", "INU", "KIP", "PPTF", "TAM", "TRIS", "CNG", "CVNA", "GRM", "HVD", "SWZ", "UPI", "WIN"]

        stations = self.iris.station(network=net, station="*", starttime=evtTime, endtime=evtTime+3600, level="sta")    
        dom = parseString(stations)
        nStations = len(dom.getElementsByTagName('Station'))
        i = 0
        while i < nStations :
            for node in dom.getElementsByTagName('Station'):
                staName = node.getAttribute('sta_code')
                if staName not in acceptedStations :
                    i += 1
                else:
                    xmlStationLat = dom.getElementsByTagName('Lat')[i].toxml()
                    staLat=float(xmlStationLat.replace('<Lat>','').replace('</Lat>',''))
                    xmlStationLon = dom.getElementsByTagName('Lon')[i].toxml()
                    staLon=float(xmlStationLon.replace('<Lon>','').replace('</Lon>',''))
                    xmlStationElev = dom.getElementsByTagName('Elevation')[i].toxml()
                    staElev=float(xmlStationElev.replace('<Elevation>','').replace('</Elevation>',''))
                    
                    
                    #delta = taup.locations2degrees(evtLat, evtLon, staLat, staLon) # delta stores distance in degrees
                    delta = util.locations2degrees(evtLat, evtLon, staLat, staLon) # delta stores distance in degrees
                    itp = IagTaup() # calling IAG Taup class 
                    itp.getTravelTimes(delta, evtDep)
                    pTime = itp.P()
                    sTime = itp.S()
                    # to use in sac headers...
                    seisTime = evtTime + pTime - self.beforeP
                    originTime = self.beforeP - pTime
                    
                    fileTime = str(evtTime).replace('T', '-').replace(':', '-')[:-8]
                    
                    try:
                        st = self.iris.getWaveform(net, staName, "*", "BH*", evtTime + pTime - self.beforeP, evtTime + sTime + self.afterS)
                        print "\nData found for station "+staName
                        st.merge(method=1, fill_value="interpolate")
            
                        try:
                            os.mkdir(staName)
                        except:
                            pass
                    
                        os.mkdir(staName+"/"+fileTime)
                        for tr in st :
                            loc = str(tr.stats.location)
                            fileName = staName+"/"+fileTime+"/"+net+"."+staName+"."+loc+"."+str(tr.stats.channel)+"."+fileTime+"."+fileFormat
                            tr.write(fileName, fileFormat)
                            print fileName, "saved."
                            if fileFormat == "SAC":
                                self.fillSACHeaders(fileName, seisTime, originTime, evtLat, evtLon, evtDep, mag, staLat, staLon, staElev)
                    except:
                        pass
                    i+=1
        
            
    
if __name__ == '__main__':
    lat = "-15"
    lon = "-47"
    minRadius = "0" 
    maxRadius =  "180"
    minDepth = "0"
    maxDepth = "700"
    minMag = "0"
    maxMag = "10"
    magType = "mb" # "Ml" (local/Richter magnitude), "Ms" (surface magnitude), "mb" (body wave magnitude), "Mw" (moment magnitude)
    startTime = UTCDateTime("1998-03-10")
    endTime = UTCDateTime("1998-03-11")
    
    evts = ObspyEvents(lat=lat, lon=lon, minRadius=minRadius, maxRadius=maxRadius, minDepth=minDepth, maxDepth=maxDepth, 
                       minMag=minMag, maxMag=maxMag, magType="mb", startTime=startTime, endTime=endTime)
    
    evts.showCatalog()
     
    
