#!/usr/bin/env -S uv run --script
#
#! /home/joea/miniconda3/envs/aa2il/bin/python -u
#
# NEW: /home/joea/miniconda3/envs/aa2il/bin/python -u
# OLD: /usr/bin/python3 -u 
################################################################################
#
# rbn.py - Rev 2.0
# Copyright (C) 2022-5 by Joseph B. Attili, joe DOT aa2il AT gmail DOT com
#
# GUI to plot spots from reverse beacon network
#
# Examples:
#              rbn_tool.py 20220728.csv -t1 3 -hours 1 -na
#
#              rbn_tool.py 20250211
#
################################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
################################################################################

import numpy as np
from fileio import *
import sys
from unidecode import unidecode
import argparse
from pprint import pprint

# Fix problems with recent python releases
# Qt6Agg' is not a valid value for backend; supported values are
# ['gtk3agg', 'gtk3cairo', 'gtk4agg', 'gtk4cairo', 'macosx', 'nbagg', 'notebook', 'qtagg', 'qtcairo', 'qt5agg', 'qt5cairo', 'tkagg', 'tkcairo', 'webagg', 'wx', 'wxagg', 'wxcairo', 'agg', 'cairo', 'pdf', 'pgf', 'ps', 'svg', 'template']
if True:
    import matplotlib
    matplotlib.use('qtagg')

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import matplotlib.patches as mpatches
from matplotlib.image import imread

import cartopy.io.shapereader as shpreader
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from shapely import geometry

from datetime import timedelta,datetime
from settings import *

from dx import load_cty_info,Station
from latlon2maiden import *
from utilities import freq2band,find_resource_file

################################################################################

VERSION='1.01'

################################################################################

# Structure to contain processing params
class PARAMS:
    def __init__(self):

        # Process command line args
        # Can add required=True to anything that is required
        arg_proc = argparse.ArgumentParser()

        # nargs stands for Number Of Arguments
        # 3: 3 values, can be any number you want
        # ?: a single value, which can be optional
        # *: a flexible number of values, which will be gathered into a list
        # +: like *, but requiring at least one value
        
        # Unflagged arg with input file name
        arg_proc.add_argument('Files', metavar='Files',
                              type=str, nargs='+', default='',
                              help='RBN History Files')
        
        arg_proc.add_argument("-call", help="Call",
                              type=str,default=None)
        arg_proc.add_argument("-t1", help="Starting Time",
                              type=str,default='0')
        arg_proc.add_argument("-hours", help="No. Hours",
                              type=int,default=24)
        arg_proc.add_argument("-na", help="NA only",
                              action='store_true')
        arg_proc.add_argument("-grid", help="Grid Square",
                              type=str,default=None)
        args = arg_proc.parse_args()

        self.SETTINGS,junk = read_settings('.keyerrc')

        # Take care of non-standard location of support files
        load_cty_info(DIR=self.SETTINGS['MY_DATA_DIR'])
        
        self.fnames=args.Files
        #print('fnames=',self.fnames)

        self.t1=args.t1
        self.dt=args.hours

        if args.na:
            self.conts=['NA']
        else:
            self.conts=['NA','SA','OC','EU','AS','AF']

        if args.call==None:
            self.CALL  = self.SETTINGS['MY_CALL'].replace('/','_')
            self.CALL2 = None
        else:
            self.CALL  = args.call.upper()
            self.CALL2 = args.call.upper()

        self.GRIDSQ=args.grid

        #sys.exit(0)
        
################################################################################

print("\n\n***********************************************************************************")
print('\nStarting RBN Plotter v'+VERSION+' ...')
P=PARAMS()
print("\nP=",end=' ')
#print "\nP=",
pprint(vars(P))

# Init
MY_CALL = P.SETTINGS['MY_CALL'].replace('/','_')
print('MY_CALL=',MY_CALL)
DATA_DIR = os.path.expanduser('~/Python/rbn_tool/data/')

# Read CSV format spreadsheet with RBN data
data=[]
for fname in P.fnames:

    # Check that we have the data locally
    #fname=DATA_DIR+fname
    #print(fname)
    #base=os.path.basename(fname)
    #print('base=',base)
    p=os.path.splitext(fname)
    print('p=',p)
    base=p[0]
    print('base=',base)
    ext=p[1]
    print('ext=',ext)
    #sys.exit(0)
    
    exists=os.path.exists(DATA_DIR+fname)
    if not exists and ext=='':
        if os.path.exists(DATA_DIR+fname+'.zip'):
            exists=True
            fname=fname+'.zip'
        elif os.path.exists(DATA_DIR+fname+'.csv'):
            exists=True
            fname=fname+'.csv'
        else:
            exists=False
            fname=fname+'.zip'
    print(exists)
    if not exists:
        print('Retrieving data ... - NEEDS more work!!!')
        url='https://data.reversebeacon.net/rbn_history/'
        cmd='cd '+DATA_DIR+' ; wget '+url+fname
        print(cmd)
        os.system(cmd)
        #sys.exit(0)
    
    data2,hdr=read_csv_file(DATA_DIR+fname)
    if 'dx' not in data2[-1]:
         data2.pop(-1)
    
    data+=data2
    print('hdr=',hdr)
    print('No. records=',len(data2),len(data))
    #print('data2[0]=',data2[0])
    #print('data2[1]=',data2[1])
    #print('data2[-2]=',data2[-2])
    #print('data2[-1]=',data2[-1])

#sys.exit(0)

# Digest spot data
spotters=set([])
myspots=[]
allspots=[]
n=0
for row in data:
    n+=1
    if n==1:
        
        # Get start date
        print(row)
        d=row['date'].split(' ')[0] + ' ' + str(P.t1)+':00:00'
        print('d=',d)
        date0 = datetime.strptime(d, "%Y-%m-%d %H:%M:%S")
        date1 = date0 + timedelta(hours=P.dt)
        print('Start date =',date0)
        print('Stop  date =',date1)

    # Test if line contains spot within time interval of interest
    # Also eliminate beacons and anything outside geo region of interest
    #print(row)
    mode=row['mode'] 
    cont=row['dx_cont'] 
    if ('BEACON' not in mode) and ('NCDXF' not in mode) and (cont in P.conts):
        d=datetime.strptime(row['date'], "%Y-%m-%d %H:%M:%S")
        if d>=date0 and d<=date1:
            #print(row)
            spotters.add(row['callsign'])
            allspots.append(row)
            if row['dx']==P.CALL:
                myspots.append(row)
        
#spotters=list(spotters)        
print('spotters=',spotters)
try:
    print('myspots[0]=',myspots[0])
    print('myspots[1]=',myspots[1])
    print('myspots[-2]=',myspots[-2])
    print('myspots[-1]=',myspots[-1])
except:
    print('myspots=',myspots)

spotter_info=OrderedDict()
for spotter in spotters:
    call = spotter.split('-')[0].upper()
    if call=='BH4RRG0':
        call='BH4RRG'
    elif call=='JH7CSU1':
        call='JH7CSU'
    elif ' ROWS)' in call:
        continue
    
    station = Station(call)
    #print(call)
    #pprint(vars(station))
    try:
        gridsq=latlon2maidenhead(station.latitude,-station.longitude,6)
    except:
        continue
    
    spotter_info[spotter]=OrderedDict()
    spotter_info[spotter]['GRID']=gridsq
    spotter_info[spotter]['LAT']=station.latitude
    spotter_info[spotter]['LON']=-station.longitude
    print(call,':\t',spotter_info[spotter])

print('\nThere are ',len(data),'spots in the file',fname)
print('There are ',len(allspots),'spots in the specified time interval and region',P.conts)    
print('There are ',len(myspots),'spots belonging to',P.CALL,'\n')
#sys.exit(0)

################################################################################

# Create the map
print('\nGenerating map ...')
#fig = plt.figure(num='RBN Analysis for '+P.CALL+' from '+fname)
fig = plt.figure(num='RBN Analysis for '+P.CALL+
                 ' from '+str(date0)+' to '+str(date1))
lon0=-75
proj=ccrs.PlateCarree(central_longitude=lon0) 
ax = fig.add_subplot(1, 1, 1,projection=proj)

# Put a background image on for nice sea rendering.
if False:
    # This doesn't work under pyinstaller ...
    ax.stock_img()
else:
    # ... so we load image directly instead
    fname99=find_resource_file('50-natural-earth-1-downsampled.png')
    print('fname99=',fname99)
    img = imread(fname99)
    ax.imshow(img, origin='upper', transform=ccrs.PlateCarree(),
              extent=[-180, 180, -90, 90])

# Create a feature for States/Admin 1 regions at 1:50m from Natural Earth
states_provinces = cfeature.NaturalEarthFeature(
    category='cultural',
    name='admin_1_states_provinces_lines',
    scale='50m',
    facecolor='none')

# Add boundaries
ax.add_feature(cfeature.LAND)
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS)
ax.add_feature(states_provinces, edgecolor='gray')

# Expand map to fill canvas
ax.set_aspect('auto')
fig.tight_layout(pad=0)

# Read country and state shape data
shpfilename = shpreader.natural_earth(resolution='110m',
                                      category='cultural',
                                      name='admin_0_countries')
countries = shpreader.Reader(shpfilename).records()

shpfilename = shpreader.natural_earth(resolution='110m',
                                      category='cultural',
                                      name='admin_1_states_provinces_lakes')

states = shpreader.Reader(shpfilename).records()

# Plot Spotters
colors={'Spotters':'wo', '160m':'y>', '80m':'g<', '40m':'rx', '20m':'b+', '15m':'mv', '10m':'c^'}
lines=[]
labels=[]
for key in spotter_info.keys():
    lat=spotter_info[key]['LAT']
    lon=spotter_info[key]['LON']
    x,y = proj.transform_point(lon,lat, ccrs.Geodetic())
    lab='Spotters'
    c=colors[lab]
    line=ax.plot(x,y,c,label=lab)
    if lab not in labels:
        labels.append(lab)
        lines.append(line[0])

# Plot spotters that saw me
for spot in myspots:
    call=spot['callsign']        #.split('-')[0].upper()
    lat=spotter_info[call]['LAT']
    lon=spotter_info[call]['LON']
    
    freq=spot['freq']
    band=freq2band(0.001*float(freq))
    c=colors[band]
    x,y = proj.transform_point(lon,lat, ccrs.Geodetic())
    line=ax.plot(x,y,c,label=band)
    if band not in labels:
        labels.append(band)
        lines.append(line[0])

# Plot my location        
station = Station(P.CALL)
print("\nStation=",end=' ')
pprint(vars(station))
if P.GRIDSQ!=None:
    lat,lon=maidenhead2latlon(P.GRIDSQ)
else:
    lat=station.latitude
    lon=-station.longitude
x,y = proj.transform_point(lon,lat, ccrs.Geodetic())
line=ax.plot(x,y,'o',color='orange',label=P.CALL)
lines.append(line[0])

# Legend
#print('Legend:',colors)
ax.legend(handles=lines,loc='lower right')

plt.show()

#sys.exit(0)

################################################################################

# Analyze sending speeds
print('\nSpeed analysis ...')
speeds=[]
speeds2=[]
for spot in allspots:
    mode=spot['tx_mode']
    #print(mode,spot['dx'])
    if mode=='CW':
        speed=int(spot['speed'])
        speeds.append(speed)
        call=spot['dx']
        if call==P.CALL2:
            speeds2.append(speed)

mu=np.mean(speeds)
mn=np.min(speeds)
mx=np.max(speeds)
bins=range(mn,mx+1)

fig,ax = plt.subplots(num='Speed Analysis')
h,b,p=ax.hist(speeds,bins=bins,label='All Calls')
#h,b,p=ax.hist(speeds,bins=bins,density=True,color='blue')
h=np.array(h)

#print('P.CALL2=',P.CALL2,'\tspeeds2=',speeds2)
if P.CALL2 and sum(speeds2)>0:
    ax2 = ax.twinx()
    h2,b2,p2=ax2.hist(speeds2,bins=bins,color='red',label=P.CALL,histtype='step')
    #h2,b2,p2=ax.hist(speeds2,bins=bins,density=True,color='red')
    #print('speeds2=',speeds2)
    #print('h2=',h2)

#print('\nSpeed Hist:')
hbest=-1
for bb,hh in zip(b,h):
    #print(bb,hh)
    if hh>hbest:
        mode=bb
        hbest=hh
        
print('\nMean speed=',mu,' wpm')
print('Min. speed=',mn,' wpm')
print('Max. speed=',mx,' wpm')
print('Most common speed=',mode,' wpm')

ax.set_title('CW Speed Distribution\n'+str(date0)+' to '+str(date1))
ax.grid(True)
ax.set_xlabel('WPM')
ax.set_ylabel('Spot Histogram')
#ax.set_ylabel('PMF')
ax.set_xlim(10,50)
ax.legend(loc='upper left')
if P.CALL2 and sum(speeds2)>0:
    ax2.legend(loc='upper right')

plt.show()

    
