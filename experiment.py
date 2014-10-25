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
        self.loglike=[]
        self.ranks
        
    def runExperiment(self,splits,runs,filename):
        data=edata.load(filename)
        data.beforeSplitCleaning()
        if self.modeltype=="afm":
            self.mainmodel=afmModel(data,False)
        elif self.modeltype=="pfa":
            self.mainmodel=pfasModel(data,False)
        else:
            print "ERROR, no correct modeltype given",self.mainmodel
            return
        #Don't forget to uncomment! when removing the raise
        self.mainmodel.fit()
        
        sets=data.splitDataStudent(splits)
        
        for d in sets:
            d.splitCleaning()
            if self.modeltype=="afm":
                model=afmModel(d,False)
            if self.modeltype=="pfa":
                model=pfasModel(d,False)
            self.loglike.append(model.fit())
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
        #For some reasons particular kc parameters may be left out.
        leaveout=[]
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
                if j in self.models[i].data.kcmis:
                    skip+=1
                    for k in range(kcpars):
                        pars[k][j,i]=np.NaN
                        internalvar[k][j,i]=np.NaN
                else:
                    for k in range(kcpars):
                        pars[k][j,i]=self.models[i].parameters[k][j-skip]
                        internalvar[k][j,i]=self.variances[i][k][j-skip]
                        
                                   
        
        
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
                if len(parlists[j])>2 and sum(np.abs(parlists[j]))>0:
                    totalvar[j][i]=np.var(parlists[j],ddof=1)/modelvars[j]
                    averageinternalvar[j][i]=(np.mean(intparlists))/modelvars[j]
                    externalvar[j][i]=(totalvar[j][i]-np.mean(intparlists))/modelvars[j]                    
#                    totalvar[j]=1-(totalvar[j]/(totalvar[j]+modelvars[j]))
#                    averageinternalvar[j]=1-(averageinternalvar[j]/(averageinternalvar[j]+modelvars[j]))
                else:
                    totalvar[j][i]=np.NaN
                    averageinternalvar[j][i]=np.NaN
                    externalvar[j][i]=np.NaN
            if np.isnan(totalvar[1][i]):
                textfile.write("totalvar is NaN %i,%s \n" %(i, str(parlists[1])))
                leaveout.append(i)


        for k in range(kcpars):
            totalvar[k]=np.delete(totalvar[k],np.array(leaveout))
            averageinternalvar[k]=np.delete(averageinternalvar[k],np.array(leaveout))
            externalvar[k]=np.delete(externalvar[k],np.array(leaveout))
            
        spearman=np.zeros((len(self.models),kcpars))
        for i in range(len(self.models)):
            for j in range(i+1,len(self.models)):
                spearman[i,:]=self.models[i].spearman(self.models[j])   
        
        textfile.write("Pars (harmonic) average var and std of var\n")
        for i in range(kcpars):
            textfile.write(str(self.mainmodel.paranames[i])+"\n") 
            textfile.write("internal: %.3f (%.3f)\n"%(np.mean(averageinternalvar[i]), np.var(averageinternalvar[i],ddof=1)))
            textfile.write("total:  %.3f (%.3f)\n"%(np.mean(totalvar[i]),np.var(totalvar[i],ddof=1)))
            textfile.write("external:  %.3f (%.3f)\n"%(np.mean(externalvar[i]),np.var(externalvar[i],ddof=1)))
            textfile.write("spearman over total: %.3f\n"%np.mean(spearman[:,i]))
        #textfile.write("Aprime avg/std:  %.3f (%.3f)\n"%(np.mean(self.aprimes),np.std(self.aprimes)))



#        bins = [0,.1,.2,.3,.4,.5,.6,.7,.8,.9,1,1.5,2]
#        overlist=[]
#        for i in range(kcpars):
#            overlist.append([])
#        for i in range(len(totalvar[0])):
#            for j in range(kcpars):
#                if totalvar[j][i]>bins[-1]:
#                    overlist[j].append(totalvar[j][i])
#        for i in range(kcpars):
#            textfile.write( "outliers "+str(self.mainmodel.paranames[i])+": "+str( overlist[i].sort())+"\n")
        
#        plt.figure()
#        x = np.column_stack(totalvar)
#        print x.shape
#        colors=['crimson', 'burlywood','chartreuse']
#        n, bins, patches = plt.hist(x, bins, normed=1, histtype='bar',                      color=colors[:kcpars],label=self.mainmodel.paranames[:kcpars])
#        plt.legend()
#        plt.savefig(self.filenamebase+"variancehistogram")
        
        
        
        #Scatter plot of external vs internal variance
        for i in range(kcpars):
            plt.figure()
            plt.xlabel("Total normalized standard deviaton")
            plt.ylabel("Internal normalized standard deviaton")
            plt.plot(np.sqrt(totalvar[i]), np.sqrt(averageinternalvar[i]),"o")
            to=min([max(np.sqrt(totalvar[i])),max(np.sqrt(averageinternalvar[i]))])
            fro=max([min(np.sqrt(totalvar[i])),min(np.sqrt(averageinternalvar[i]))])
            plt.plot([fro, to], [fro, to],"k-")

            plt.savefig(self.filenamebase+"in_tot_var"+self.mainmodel.paranames[i])
                        
                        
    def rankOrder(self,order="kendall"):
        
        dims=len(self.models[0].rankOrder(self.models[0]))
        self.ranks=np.zeros((dims,len(self.models),len(self.models)))
        for i in range(len(self.models)):
            for j in range(i+1,len(self.models)):
                self.ranks[:,i,j]=self.models[i].rankOrder(self.models[j],order)
        print "Rankorder:", order
        
        
        for i in range(dims):
            print self.mainmodel.paranames[i], np.sum(self.ranks[i,:,:])/((len(self.models)**2-len(self.models))/2)

    def getVariances(self):
        mainmodel=self.mainmodel
        kcpars=0
        if self.modeltype=="afm":
            kcpars=2
        if self.modeltype=="pfa":
            kcpars=3
        #For some reasons particular kc parameters may be left out.
        leaveout=[]
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
                if j in self.models[i].data.kcmis:
                    skip+=1
                    for k in range(kcpars):
                        pars[k][j,i]=np.NaN
                        internalvar[k][j,i]=np.NaN
                else:
                    for k in range(kcpars):
                        pars[k][j,i]=self.models[i].parameters[k][j-skip]
                        internalvar[k][j,i]=self.variances[i][k][j-skip]
                        
                                   
        
        
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
                if len(parlists[j])>2 and sum(np.abs(parlists[j]))>0:
                    totalvar[j][i]=np.var(parlists[j],ddof=1)/modelvars[j]
                    averageinternalvar[j][i]=(np.mean(intparlists))/modelvars[j]
                    
                else:
                    totalvar[j][i]=np.NaN
                    averageinternalvar[j][i]=np.NaN
                    externalvar[j][i]=np.NaN
            if np.isnan(totalvar[0][i]) or np.isnan(totalvar[1][i]):
                leaveout.append(i)
            if kcpars>2 and np.isnan(totalvar[2][i]):
                leaveout.append(i)


        for k in range(kcpars):
            totalvar[k]=np.delete(totalvar[k],np.array(leaveout))
            totalvar[k]=np.mean(np.sqrt(totalvar[k]))
            averageinternalvar[k]=np.delete(averageinternalvar[k],np.array(leaveout))
            averageinternalvar[k]=np.mean(np.sqrt(averageinternalvar[k]))
        return np.array(totalvar+averageinternalvar)
        
            