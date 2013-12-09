# -*- coding: utf-8 -*-
from complexModel import complexModel
import time
import datetime
from edata import edata
from baseline import baseline

def main():
    #Load the prepared train data
    data=edata.load("train.edata")
    #Create a model on the data and fit it to the data
    model=complexModel(data,False)
    model.fit()
    #Also create a baseline model for comparison
    model2=baseline(data)
    model2.fit()
    
    #see how the model does on testset
    data=edata.load("test.edata")
    testerror=0.0
    baseerror=0.0
    for d in data.giveData():
        if d[2]:
            testerror+=1-model.predict(d[0],d[1])
            baseerror+=1-model2.predict(d[0],d[1])
        else:
            testerror+=model.predict(d[0],d[1])
            baseerror+=model2.predict(d[0],d[1])
    print "Fitted model error on testset", testerror/len(data)
    print "Base model error on testset", baseerror/len(data)
    model.save("real.cmodel")
    
if __name__ == "__main__":
    t0=time.clock()
    main()
    t1=time.clock()
    print "Time taken by all code", str(datetime.timedelta(seconds=(t1-t0)))