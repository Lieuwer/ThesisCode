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
import cPickle as pickle
from experiment import experiment

class experimentProcessing():
    def save(self, filename):
        filehandle= open (filename,"wb")
        pickle.dump(self,filehandle)
        filehandle.close()
    
    @staticmethod
    def load(filename):
        filehandle=open(filename,"rb")
        return pickle.load(filehandle)    
    
    def __init__(self):
        self.models=['afm','pfa']
        self.splits=[6,8,12,16,32]
        self.nrPars=[2,3]
        self.params=[]
        self.nrs=0
        
        self.params.append(np.zeros((len(self.splits),2*2)))
        self.params.append(np.zeros((len(self.splits),3*2)))
        for i,split in enumerate(self.splits):
            for j,model in enumerate(self.models):
                print split
                exp=experiment.load("D:\\spyderstuff\\ThesisCode\\Experiments\\gong\\"+model+str(split)+"exp.exp")
                info=exp.getVariances()
                self.nrs=exp.mainmodel.data.nrs*1.0
                print info
                self.params[j][i,:]=info
        #Due to memory crashes, data is put in like this. <--bridge data
#        self.params.append(np.array([[ 0.38872627, 0.50705948, 0.35116546, 1.11868367],[ 0.44374125,  0.58461036 , 0.38927952,  1.23754498],[ 0.5054817,  0.68828295,  0.44710189,  1.42358945],[ 0.56424658 , 0.77423182,  0.48583258 , 1.5486857 ],[ 0.68475655 , 0.94191299 , 0.55993345,  1.78899011]]))
#        self.params.append(np.array([[ 0.40543848,  0.52010538 , 0.56562546,  0.39037801,  1.03993924 , 0.7821048 ],[ 0.45872448 , 0.60275368 , 0.66000739 , 0.42487795 , 1.12692069,  0.84553601],[ 0.53947114 , 0.69562019 , 0.82460349 , 0.48667268 , 1.29535967 , 0.97180388],[ 0.6114219,   0.79009548 , 0.87890323 , 0.52164013 , 1.38569553,  1.0370177 ],[ 0.79287871 , 0.97850259,  1.11264888,  0.62302985  ,1.65357639 , 1.23620541]]))
        self.save("basic.info")
        nrslist=[]
        colors=['r','g','m']        
        params=['Beta','Gamma','Ro']
        for i in self.splits:
            nrslist.append(int(round(self.nrs/i)))
        for i,model in enumerate(self.models):
            plt.figure()
            plt.xlabel("Number of students per split")
            plt.ylabel("Average normalized standard deviation")
            for j in range(self.nrPars[i]):
                plt.plot(nrslist, self.params[i][:,j],'o'+colors[j]+'-',label=params[j]+'(Total)')
                plt.plot(nrslist,self.params[i][:,self.nrPars[i]+j],'o'+colors[j]+'--', label=params[j]+'(Internal)')
            plt.legend()
            plt.savefig("gong"+model)
        
        
if __name__ == "__main__":
    p=experimentProcessing()
