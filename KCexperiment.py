# -*- coding: utf-8 -*-
"""
Created on Fri Aug 22 12:27:20 2014
Experiment to determine total and external variance of specifically the KC 
parameters in fitting the AFM model and fitting the pfas model.

@author: Lieuwe
"""

import sys
sys.path.append('.\models')
from edata import edata
from complexModel import complexModel
from pfasModel import pfasModel
from afmModel import afmModel
import time,datetime
from baseline import baseline
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stat
import random as r
def main():
    data=edata.load("train.edata")
    print len(data.data)
    sets=data.splitDataStudent(6)
    s=0
    for i in sets:
        s+=len(i.data)
        print len(i.data)
    print s
    folderpath='.\Experiments\1\\'    
    
if __name__ == "__main__":
    t0=time.time()
    main()
    t1=time.time()
    print "Time taken by all code", str(datetime.timedelta(seconds=(t1-t0)))