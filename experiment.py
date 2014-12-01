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
from eirtModel import eirtModel
from pfasModel import pfasModel
from afmModel import afmModel
from experimentProcessing import experimentProcessing
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
        self.inherentRankOrder=[]
        self.parvartot=[]
        self.parvarinh=[]
        
    def runExperiment(self,splits,runs,filename):
        data=edata.load(filename)
        data.beforeSplitCleaning()
        if self.modeltype=="afm":
            self.mainmodel=afmModel(data,False)
        elif self.modeltype=="pfa":
            self.mainmodel=pfasModel(data,False)
        elif self.modeltype=="eirt":
            self.mainmodel=eirtModel(data,False)
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
            if self.modeltype=="eirt":
                model=eirtModel(d,False)
            print "Avg error in fit", np.e**model.fit()
            
            inherentInfo=model.determineVariance(runs)
            self.variances.append(inherentInfo[0])
            self.inherentRankOrder.append(inherentInfo[1])
            self.models.append(model)
            self.aprimes.append(model.aPrime())
            self.loglike.append(model.dataLikely())
            print "The variance over the different parameters"
            totparvar=[]
            for i in range(len(self.mainmodel.parameters)):
                print "model:",model.parameterVariance(model.paranames[i])
                print "inherent:",inherentInfo[2][i]
                totparvar.append(model.parameterVariance(model.paranames[i]))
                print "mainM:",totparvar[i]
            self.parvarinh.append(inherentInfo[2])
            self.parvartot.append(totparvar)
        self.save(self.filenamebase+".exp")


    def determineStds(self):
        
        #Get some data on how many KCs and students were tossed out.
        missing=[0.0,0.0]
        for m in self.models:
            missing[0]+=len(m.data.studentmis)
            missing[1]+=len(m.data.kcmis)
        missing[0]/=len(self.models)
        missing[1]/=len(self.models)
        print "studentmis", missing[0], "kcmis", missing[1]
       # textfile=open(self.filenamebase+".txt","w")
        mainmodel=self.mainmodel
        kcpars=0
        if self.modeltype=="afm" or self.modeltype=="eirt":
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
                for k in range(kcpars):
                    if not np.isnan(pars[k][i,j]):
                        parlists[k].append(pars[k][i,j])
                        intparlists[k].append(internalvar[k][i,j])
                        
            for j in range(kcpars):
                if len(parlists[j])>2 and sum(np.abs(parlists[j]))>0:
                    totalvar[j][i]=np.var(parlists[j],ddof=1)
                    averageinternalvar[j][i]=(np.mean(intparlists[j]))
                    externalvar[j][i]=(totalvar[j][i]-np.mean(intparlists[j]))
#                    totalvar[j]=1-(totalvar[j]/(totalvar[j]+modelvars[j]))
#                    averageinternalvar[j]=1-(averageinternalvar[j]/(averageinternalvar[j]+modelvars[j]))
                else:
                    totalvar[j][i]=np.NaN
                    averageinternalvar[j][i]=np.NaN
                    externalvar[j][i]=np.NaN
#            if np.isnan(totalvar[1][i]):
#                textfile.write("totalvar is NaN %i,%s \n" %(i, str(parlists[1])))
#                leaveout.append(i)
#        
#        
#
#        for k in range(kcpars):
#            totalvar[k]=np.delete(totalvar[k],np.array(leaveout))
#            averageinternalvar[k]=np.delete(averageinternalvar[k],np.array(leaveout))
#            externalvar[k]=np.delete(externalvar[k],np.array(leaveout))
            

        
#        textfile.write("Pars (harmonic) average var and std of var\n")
#        for i in range(kcpars):
#            textfile.write(str(self.mainmodel.paranames[i])+"\n") 
#            textfile.write("internal: %.3f (%.3f)\n"%(np.mean(averageinternalvar[i]), np.var(averageinternalvar[i],ddof=1)))
#            textfile.write("total:  %.3f (%.3f)\n"%(np.mean(totalvar[i]),np.var(totalvar[i],ddof=1)))
#            textfile.write("external:  %.3f (%.3f)\n"%(np.mean(externalvar[i]),np.var(externalvar[i],ddof=1)))
#                    spearman=np.zeros((len(self.models),kcpars))
#        for i in range(len(self.models)):
#            for j in range(i+1,len(self.models)):
#                spearman[i,:]=self.models[i].spearman(self.models[j])   
#            textfile.write("spearman over total: %.3f\n"%np.mean(spearman[:,i]))
        

        ranks=np.zeros((kcpars,len(self.models),len(self.models)))
        for i in range(len(self.models)):
            for j in range(i+1,len(self.models)):
                ranks[:,i,j]=self.models[i].rankOrder(self.models[j])
                
          
            
        inf=experimentProcessing(self.mainmodel,self.aprimes,self.loglike,internalvar,averageinternalvar,totalvar,ranks,self.inherentRankOrder,self.parvarinh,self.parvartot)
        
        
        for model in self.models:
            inf.studentsCleaned.append(model.data.studentmis)
            inf.KCCleaned.append(model.data.kcmis)
        inf.save(self.filenamebase+".info")
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
#        for i in range(kcpars):
#            plt.figure()
#            plt.xlabel("Total normalized standard deviaton")
#            plt.ylabel("Internal normalized standard deviaton")
#            plt.plot(np.sqrt(totalvar[i]), np.sqrt(averageinternalvar[i]),"o")
#            to=min([max(np.sqrt(totalvar[i])),max(np.sqrt(averageinternalvar[i]))])
#            fro=max([min(np.sqrt(totalvar[i])),min(np.sqrt(averageinternalvar[i]))])
#            plt.plot([fro, to], [fro, to],"k-")
#
#            plt.savefig(self.filenamebase+"in_tot_var"+self.mainmodel.paranames[i])
                        
                        
   

    def getVariances(self):
        
        mainmodel=self.mainmodel
        kcpars=0
        if self.modeltype=="afm" or self.modeltype=="eirt":
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
 

if __name__ == "__main__":
    exp=experiment("pfa","pfaTest8e")
    exp.runExperiment(8,4,"gong.edata")
#    exp.determineStds()
#        self.models=['afm','pfa']
#        self.splits=[6,8,12,16,32]
#        self.nrPars=[2,3]
#        self.params=[]
#        self.nrs=0
#        
#        self.params.append(np.zeros((len(self.splits),2*2)))
#        self.params.append(np.zeros((len(self.splits),3*2)))
#        for i,split in enumerate(self.splits):
#            for j,model in enumerate(self.models):
#                print split
#                exp=experiment.load("D:\\spyderstuff\\ThesisCode\\Experiments\\gong\\"+model+str(split)+"exp.exp")
#                info=exp.getVariances()
#                self.nrs=exp.mainmodel.data.nrs*1.0
#                print info
#                self.params[j][i,:]=info
#        #Due to memory crashes, data is put in like this. <--bridge data
##        self.params.append(np.array([[ 0.38872627, 0.50705948, 0.35116546, 1.11868367],[ 0.44374125,  0.58461036 , 0.38927952,  1.23754498],[ 0.5054817,  0.68828295,  0.44710189,  1.42358945],[ 0.56424658 , 0.77423182,  0.48583258 , 1.5486857 ],[ 0.68475655 , 0.94191299 , 0.55993345,  1.78899011]]))
##        self.params.append(np.array([[ 0.40543848,  0.52010538 , 0.56562546,  0.39037801,  1.03993924 , 0.7821048 ],[ 0.45872448 , 0.60275368 , 0.66000739 , 0.42487795 , 1.12692069,  0.84553601],[ 0.53947114 , 0.69562019 , 0.82460349 , 0.48667268 , 1.29535967 , 0.97180388],[ 0.6114219,   0.79009548 , 0.87890323 , 0.52164013 , 1.38569553,  1.0370177 ],[ 0.79287871 , 0.97850259,  1.11264888,  0.62302985  ,1.65357639 , 1.23620541]]))
#        self.save("basic.info")
#        nrslist=[]
#        colors=['r','g','m']        
#        params=['Beta','Gamma','Ro']
#        for i in self.splits:
#            nrslist.append(int(round(self.nrs/i)))
#        for i,model in enumerate(self.models):
#            plt.figure()
#            plt.xlabel("Number of students per split")
#            plt.ylabel("Average normalized standard deviation")
#            for j in range(self.nrPars[i]):
#                plt.plot(nrslist, self.params[i][:,j],'o'+colors[j]+'-',label=params[j]+'(Total)')
#                plt.plot(nrslist,self.params[i][:,self.nrPars[i]+j],'o'+colors[j]+'--', label=params[j]+'(Internal)')
#            plt.legend()
#            plt.savefig("gong"+model)         