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
import cPickle as pickle




class experiment():
    def save(self, filename):
        filehandle= open (filename,"wb")
        pickle.dump(self,filehandle)
        filehandle.close()
    
    @staticmethod
    def load(filename):
        filehandle=open(filename,"rb")
        return pickle.load(filehandle)    
    
    def __init__(self,model,filename):
        self.mainmodel=None
        self.models=[]
        #holdinternalvariances per part
        self.variances=[]
        self.modeltype=model
        self.filenamebase=filename
        #aprime values per part
        self.aprimes=[]
        
    def runExperiment(self,splits,runs,filename):
        data=edata.load(filename)
        data.createMissing()
        if self.modeltype=="afm":
            self.mainmodel=afmModel(data,False)
        if self.modeltype=="pfa":
            self.mainmodel=pfasModel(data,False)
        else:
            print "ERROR, no correct modeltype given"
            return
        self.mainmodel.fit()
        sets=data.splitDataStudent(splits)
        for d in sets:
            d.createMissing()
            if self.modeltype=="afm":
                model=afmModel(d,True)
            if self.modeltype=="pfa":
                model=pfasModel(d,True)
            model.fit()
            self.variances.append(model.determineVariance(runs))
            self.models.append(model)
            self.aprimes.append(model.aPrime())
        self.save(self.filenamebase+"exp.exp")
        
            
    def determineStds(self):
        textfile=open(self.filenamebase+".txt","w")
        mainmodel=self.mainmodel
        kcpars=0
        if self.modeltype=="afm":
            kcpars=2
        if self.modeltype=="pfa":
            kcpars=3
        pars=[]
        #per paratype stores parametervariance over all parameters of that type
        modelvars=[]
        #Totalvar over all the different sets per paratype
        totalvar=[]
        #store internalvariances per paratype in nrkc*nrmodels array
        internalvar=[]
        #store average internalvariances per paratype in nrkc*nrmodels array
        averageinternalvar=[]
        #store externalvariance per paratype in nrkc*1 array
        externalvar=[]
        for i in range(kcpars):
            pars.append(np.zeros((mainmodel.data.nrkc,len(self.models))))
            modelvars.append(mainmodel.parameterVariance(mainmodel.paranames[i]))
            totalvar.append(np.zeros(mainmodel.data.nrkc))
            internalvar.append(np.zeros((mainmodel.data.nrkc,len(self.models))))
            averageinternalvar.append(np.zeros(mainmodel.data.nrkc))
            externalvar.append(np.zeros(mainmodel.data.nrkc))
            
        for i in range(len(self.models)):
            skip=0
            for j in range(mainmodel.data.nrkc):
                if j+skip == mainmodel.data.nrkc:
                    break
                if j in self.models[i].data.kcmis:
                    skip+=1
                    for k in range(kcpars):
                        pars[k][j,i]=np.NaN
                        internalvar[k][j,i]=np.NaN
                else:
                    for k in range(kcpars):
                        pars[k][j,i]=self.models[i].parameters[k][j]
                        internalvar[k][j,i]=self.variances[i][k][j]
                        
                                   
        
        
        for i in range(mainmodel.data.nrkc):
            parlists=[]
            intparlists=[]
            for j in range(kcpars):
                parlists.append([])
                intparlists.append([])
            for j in range(len(self.models)):
                if not np.isnan(pars[0][i,j]):
                    for k in range(kcpars):
                        parlists[k].append(pars[k][i,j])
                        intparlists[k].append(internalvar[k][i,j])
                        
            for j in range(kcpars):
                #also normalize all this
                totalvar[j][i]=np.var(parlists[j],ddof=1)/modelvars[j]
                averageinternalvar[j][i]=(np.mean(intparlists))/modelvars[j]
                externalvar[j][i]=(np.var(parlists[j],ddof=1)-np.mean(intparlists))/modelvars[j]
                #externalvar is often below 0, so for now total var is used.
            if np.isnan(totalvar[1][i]):
                textfile.write("totalvar is NaN %i,%s \n" %(i, str(parlists[1])))
            if len(parlists[0])==1:
                textfile.write("only 1 entry %i \n"% i)

        textfile.write("Pars average var and std of var\n")
        for i in range(kcpars):
            textfile.write(str(self.mainmodel.paranames[i])+"\n") 
            textfile.write("internal: %.3f (%.3f)\n"%(np.mean(averageinternalvar[i]), np.var(averageinternalvar[i],ddof=1)))
            textfile.write("total:  %.3f (%.3f)\n"%(np.mean(totalvar[i]),np.var(totalvar[i],ddof=1)))
            textfile.write("external:  %.3f (%.3f)\n"%(np.mean(externalvar[i]),np.var(externalvar[i],ddof=1)))
        textfile.write("Aprime avg/std:  %.3f (%.3f)\n"%(np.mean(self.aprimes),np.std(self.aprimes)))

        bins = [0,.1,.2,.3,.4,.5,.6,.7,.8,.9,1,1.5,2]
        overlist=[]
        for i in range(kcpars):
            overlist.append([])
        
        for i in range(mainmodel.data.nrkc):
            for j in range(kcpars):
                if totalvar[j][i]>bins[-1]:
                    overlist[j].append(totalvar[j][i])
        for i in range(kcpars):
            textfile.write( "outliers "+str(self.mainmodel.paranames[i])+": "+str( overlist[i].sort())+"\n")
        
        plt.figure()
        x = np.column_stack(totalvar)
        print x.shape
        colors=['crimson', 'burlywood','chartreuse']
        n, bins, patches = plt.hist(x, bins, normed=1, histtype='bar',                      color=colors[:kcpars],label=self.mainmodel.paranames[:kcpars])
        plt.legend()
        plt.savefig(self.filenamebase+"variancehistogram")
        
        
        
        #Scatter plot of external vs internal variance
        for i in range(kcpars):
            plt.figure()
            plt.xlabel("total relative variance")
            plt.ylabel("Internal relative variance")
            plt.scatter(externalvar[i], averageinternalvar[i])
            plt.savefig(self.filenamebase+"in_tot_var"+self.mainmodel.paranames[i])
 
