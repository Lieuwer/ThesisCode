# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 12:43:11 2014

@author: Lieuwe
"""
from edata import edata
from complexModel import complexModel
from pfasModel import pfasModel
from afmModel import afmModel
import time,datetime
from baseline import baseline
import numpy as np
import matplotlib.pyplot as plt

def main():
    data=edata.load("train.edata")
    testdata=edata.load("test.edata")
  #  data.removekcsq(10,15)
#    
    model=afmModel(data, False)
    print model.fit()
    model.save("trying.aModel")
#    print model.useTestset(testdata)
#
    bl = baseline(data)
    bl.fit()
    print "baseline:", bl.useTestset(testdata)
    
#------------------------------------------------------------------------------
    
    model=afmModel.load("trying.pModel")

    
    print "model:", model.useTestset(testdata)
    print np.average(model.cr), np.std(model.cr)
    print np.average(model.cg), np.std(model.cg)
    print np.average(model.cb), np.std(model.cb)
    print np.average(model.st), np.std(model.st)    
    
if __name__ == "__main__":
    t0=time.time()
    main()
    t1=time.time()
    print "Time taken by all code", str(datetime.timedelta(seconds=(t1-t0)))
