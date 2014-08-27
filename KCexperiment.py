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
    runExperiment(6,5)
    
def runExperiment(splits,runs):
    
    data=edata.load("train.edata")
    mainmodel=afmModel(data,False)
    mainmodel.fit()
    models=[]
    variances=[]
    sets=data.splitDataStudent(splits)
    for d in sets:
        d.createMissing()
        model=afmModel(d,True)
        model.fit()
        variances.append(model.determineVariance(runs))
        models.append(model)
    bpars=np.zeros((mainmodel.data.nrkc,splits))
    gpars=np.zeros((mainmodel.data.nrkc,splits))

    for i in range(splits):
        skip=0
        for j in range(mainmodel.data.nrkc):
            if j+skip == mainmodel.data.nrkc:
                break
            if j in models[i].data.kcmis:
                skip+=1
                bpars[j,i]=np.NaN
                gpars[j,i]=np.NaN
            else:
                bpars[j,i]=models[i].cb[j]
                gpars[j,i]=models[i].cg[j]
    varb=mainmodel.parameterVariance("b")
    varg=mainmodel.parameterVariance("g")
    stdsb=np.zeros(mainmodel.data.nrkc)
    stdsg=np.zeros(mainmodel.data.nrkc)
    for i in range(mainmodel.data.nrkc):
        blist=[]
        glist=[]
        for j in range(splits):
            if not np.isnan(bpars[i,j]):
                blist.append(bpars[i,j])
                glist.append(gpars[i,j])
        stdsb[i]=np.std(blist)/varb**.5       
        stdsg[i]=np.std(glist)/varg**.5
    print "B/G average and std"
    print np.mean(stdsb), np.std(stdsb), np.mean(stdsg), np.std(stdsg)
    
    plt.figure()

    # create a new data-set
    x = np.column_stack((stdsb,stdsg))
    print x.shape

    n, bins, patches = plt.hist(x, 10, normed=1, histtype='bar',                      color=['crimson', 'burlywood'],label=['cb', 'cg'])
    plt.legend()
        
    folderpath='.\Experiments\1\\'    
    
if __name__ == "__main__":
    t0=time.time()
    main()
    t1=time.time()
    print "Time taken by all code", str(datetime.timedelta(seconds=(t1-t0)))