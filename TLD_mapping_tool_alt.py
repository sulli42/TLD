# coding: utf-8

## The Long Dark Mapping Tool

# The MIT License (MIT)  
# Copyright (c) 2015 Loïc Norgeot  
# Permission is hereby granted, free of charge, to any person obtaining a copy  
# of this software and associated documentation files (the "Software"), to deal  
# in the Software without restriction, including without limitation the rights  
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell  
# copies of the Software, and to permit persons to whom the Software is  
# furnished to do so, subject to the following conditions:  
# The above copyright notice and this permission notice shall be included in all  
# copies or substantial portions of the Software.  
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,  
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE  
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER  
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,  
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE  
# SOFTWARE.  

### 1 - Map-related functions

#### 1.0 - Module imports

# In[1]:

import os
import numpy as np
import matplotlib.pyplot as plt
from numpy import linspace, meshgrid
from matplotlib.mlab import griddata
from pylab import rcParams
rcParams['figure.figsize'] = 12,9.5
#import scipy.ndimage as nd


#### 1.1 - Screenshots and savefiles manipulation

# In[2]:

def readCoordsFromScreenshots(path):
    screenshots = os.listdir(path)
    screenshots = [S for S in screenshots if "screen" in S]
    coords = np.array([[int(x) for x in s[s.find("(")+1:s.find(")")].split(",")] for s in screenshots])
    return coords

def readCoordsFromFile(fileName):
    C = []
    with open(fileName) as f:
        content = f.readlines()
        for c in content:
            s = c.split(" ")
            C.append([int(s[0]), int(s[2]), int(s[1])])
    return np.array(C)

def writeCoordsToFile(data, fileName, mode="w"):
    with open(fileName, mode) as f:
        for c in data:
            f.write(str(c[0]) + " " + str(c[2]) + " " + str(c[1]) +"\n" )

def deleteScreenshots(path):
    for fileName in os.listdir(path):
        if((".png" in fileName) and ("screen" in fileName)):
            os.remove(path + fileName)


#### 1.2 - Plotting

# In[3]:

def contourPlot(data, path, save=True):
    fig = plt.figure()
    xi = linspace(min(data[:,0]),max(data[:,0]),111)
    yi = linspace(min(data[:,2]),max(data[:,2]),111)
    zi = griddata(data[:,0],data[:,2],data[:,1], xi,yi, interp='linear') 
    #zi = nd.gaussian_filter(zi, sigma=0.6, order=0)
    plt.contour (xi,yi,zi,41,linewidths=0.5,colors='black') 
    plt.contourf(xi,yi,zi,82,);
    plt.colorbar()  
    plt.grid(True)
    plt.set_cmap('terrain')
    if(save):
        plt.savefig(path + "TM_map_contour.png",dpi=150)
    
def scatterPlot(data, path, save=True):
    fig = plt.figure()
    plt.scatter(data[:,0],data[:,2], c=data[:,1], linewidth=0,s=40)
    plt.xlim(min(data[:,0]),max(data[:,0]))
    plt.ylim(min(data[:,2]),max(data[:,2]))
    plt.colorbar()  
    plt.grid(True)
    plt.set_cmap('terrain')
    if(save):
        plt.savefig(path + "TM_map_path.png",dpi=150)


#### 1.3 - User routines

# In[4]:

def createMaps(sPath, fPath):
    fC          = readCoordsFromFile(fPath + "coords.txt")
    sC          = readCoordsFromScreenshots(sPath)
    coordinates = np.array([]);

    if( (len(fC)==0) and (len(sC)==0)):
        print("No data to work on! Doing nothing...")
    elif( len(fC)==0 ):
        print("No files, but screenshots, going on...")
        coordinates=sC
        writeCoordsToFile(coordinates, fpath+ "coords.txt")
        deleteScreenshots(sPath)
    elif( len(sC)==0 ):
        print("No screenshots, but files, going on...")
        coordinates=fC
    else:
        print("Screenshots and files! Going on...")
        coordinates = np.concatenate((fC, sC))
        writeCoordsToFile(coordinates, fPath+ "coords.txt")
        deleteScreenshots(sPath)
 
    contourPlot(coordinates, fPath)
    scatterPlot(coordinates, fPath)
    
def checkFile(fileName):
    fC          = readCoordsFromFile(fileName)
    coordinates = np.array([]);
    if( (len(fC)==0)):
        print("No data to work on! Doing nothing...")
    else:
        print("No screenshots, but a file, going on...")
        print("Number of points in the file = ", len(coordinates))
        coordinates=fC
    contourPlot(coordinates, " ", save=False)
    scatterPlot(coordinates, " ", save=False)


### 2 - Interractive mapping functions

#### 2.0 - Imports

# In[5]:

from subprocess import check_output
from win32api import keybd_event, GetAsyncKeyState
import time


#### 2.1 - Functions

# In[6]:

def isTLDRunning():
    processes_string = check_output("wmic process get description", shell=True)
    return ('tld.exe' in processes_string.split())

def press(key=0x77):
    keybd_event(key, 0,1,0)
    time.sleep(.05)
    keybd_event(key, 0,2,0)
    
def wasPressed(key=0x76):
    return GetAsyncKeyState(key)

def startInteractiveMapping(sPath, fPath, time_step=2.5):
    t = time.time()
    recording = False

    while(isTLDRunning()):

        if(wasPressed(0x76)):
            if not recording:
                recording = True
            else:
                recording = False

        if(recording):
            if(time.time() - t > time_step):
                press(0x77)
                t = time.time()
                coord = readCoordsFromScreenshots(sPath)
                writeCoordsToFile(coord, fPath + "coords.txt", "a")
                deleteScreenshots(sPath)
                
        time.sleep(0.2)

    deleteScreenshots(sPath)


### 3 - GUI

# In[7]:

import Tkinter, tkFileDialog, Tkconstants

class TLD_Mapping_tool_tk(Tkinter.Tk):
    
    mPath=""
    sPath=""
    
    def __init__(self,parent):
        Tkinter.Tk.__init__(self,parent)
        self.parent = parent
        self.initialize()

    def initialize(self):
        
        self.grid()
        
        maps_bt = Tkinter.Button(self, text='Choose maps directory', command=self.chooseMapsDir)
        maps_bt.grid(column=0,row=0,columnspan=2,sticky='EW')
        
        screenshots_bt = Tkinter.Button(self, text='Choose screenshots directory', command=self.chooseScreenDir)
        screenshots_bt.grid(column=0,row=1,columnspan=2,sticky='EW')
        
        self.run_bt = Tkinter.Button(self,
                                     text    = u"Start mapping",
                                     state   = 'disabled',
                                     command = lambda: startInteractiveMapping(self.sPath, self.mPath))
        self.run_bt.grid(column=0,row=2)
        
        self.createmap_bt = Tkinter.Button(self,
                                           text    = u"Create maps",
                                           state   = 'disabled',
                                           command = lambda: createMaps(self.sPath, self.mPath))
        self.createmap_bt.grid(column=1,row=2)
        
        self.grid_columnconfigure(0,weight=1)
        self.resizable(False,False)
        
    def enableButtons(self):
        if self.sPath!="" and self.mPath!="":
            self.run_bt['state']       = 'normal'
            self.createmap_bt['state'] = 'normal'
            
    def chooseScreenDir(self):
        self.sPath = tkFileDialog.askdirectory() + "/"
        self.enableButtons()
        
    def chooseMapsDir(self):
        self.mPath = tkFileDialog.askdirectory() + "/"
        self.enableButtons()


### 4 - Execution

# In[8]:

if __name__ == "__main__":
    app = TLD_Mapping_tool_tk(None)
    app.title('TLD Mapping Tool')
    app.mainloop()
