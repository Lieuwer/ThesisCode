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


class experimentProcessing():
    def save(self, filename):
        filehandle= open (filename,"wb")
        pickle.dump(self,filehandle)
        filehandle.close()
    
    @staticmethod
    def load(filename):
        filehandle=open(filename,"rb")
        return pickle.load(filehandle)    
    
    def __init__(self,paranms,parameters,ap,ll,inter,ainter,var,ranks,avginhranks):
        #Names of the parameters
        self.paranames=paranms
        #The internalvariances, list of length #par types with (nrkc x nrsplits) array. Missing values have NaN
        self.variancesInh=inter
        #Cleaned up avg variances (NaN values removed)
        self.avgvariancesInh=ainter
        #variances over the splits
        self.variancesSeen=var
        #Parameters of the main model, useful for figures and normalizing
        self.parametersMain=parameters
        #Rankordermatrix of the values over the splits
        self.rankOrderSeen=ranks
        #avg rankorder for every splits generated models
        self.rankOrdersInh=avginhranks
        #Students dropped in cleaning for every split
        self.studentsCleaned=[]
        #KC's dropped in cleaning for every split
        self.KCCleaned=[]
        #aprime and log likelihood (normalized) for every split
        self.aprimes=ap
        self.lLikely=ll
        #Left out on the basis of missing internal/external 
        self.kcLeftOut=[]
        
        #should keep track of total amount of data...
        
    def process(self):
        splits=len(self.KCCleaned)
        filebase=str(splits)
       
        if len(self.paranames)==3:
            filebase="afm"+filebase
        else:
            filebase="pfa"+filebase
        self.kcmis=np.zeros(len(self.parametersMain[0]))
        for i in self.KCCleaned:
            for j in i:
                self.kcmis[j]+=1
        for i in range(len(self.parametersMain[0])):
                #Taking learning factor as guidance as this is most likely to have too little data
                if np.isnan(self.variancesSeen[1][i]) or (len(self.variancesSeen)>2 and np.isnan(self.variancesSeen[2][i])):
                    self.kcLeftOut.append(i)
        for k in range(len(self.parametersMain)-1):
            self.variancesSeen[k]=np.delete(self.variancesSeen[k],np.array(self.kcLeftOut))
            self.avgvariancesInh[k]=np.delete(self.avgvariancesInh[k],np.array(self.kcLeftOut))
            self.parametersMain[k]=np.delete(self.parametersMain[k],np.array(self.kcLeftOut))
#            plt.figure()
#            plt.xlabel("Parameter value")
#            plt.ylabel("Paramater standard deviation")
#            plt.plot(self.parametersMain[k], np.sqrt(self.variancesSeen[k]),"o")
#            plt.savefig(filebase+self.paranames[k]+"_valVSvar")
#            
#            plt.figure()
#            plt.xlabel("seen sd")
#            plt.ylabel("inherent sd")
#            plt.plot(np.sqrt(self.variancesSeen[k]), np.sqrt(self.avgvariancesInh[k]),"o")
#            plt.savefig(filebase+self.paranames[k]+"_svarVivar")
        self.avgtotsd=[]
        self.avginhsd=[]
        for i in range(len(self.paranames)-1):
            self.avgtotsd.append(np.mean(np.sqrt(self.variancesSeen[i])))
            self.avginhsd.append(np.mean(np.sqrt(self.avgvariancesInh[i])))
        
            
    def rankOrder(self):
        
        avginhrank=np.mean(self.rankOrdersInh,0)
        for i in range(self.rankOrderSeen.shape[0]):
            print self.paranames[i],avginhrank[i], np.sum(self.rankOrderSeen[i,:,:])/((self.rankOrderSeen.shape[2]**2-self.rankOrderSeen.shape[2])/2)
            print "in/tot average sd",np.mean(np.sqrt(self.avgvariancesInh[i])), np.mean(np.sqrt(self.variancesSeen[i]))
            #Ineherent vs variance rankorder:
            print "rankorder inherent vs seen variance:", stat.kendalltau(self.avgvariancesInh[i],self.variancesSeen[i])[0]
        
            
if __name__ == "__main__":
#        inf=experimentProcessing.load("pfaTest8e.info")
#        inf.process()
#        inf.rankOrder()
        datset="algebra"
        basefile="D:\\spyderstuff\\ThesisCode\\Experiments\\1031gong\\"
        models=['afm','pfa']
        splits=[6,8,12,16,32]
        nrPars=[2,3]
        params=[]
        totRanks=[]
        inhRanks=[]
        aprimes=[]
        llikely=[]
        #Change to Total questions
        nrs=0
        
        for i in range(len(models)):
            inhRanks.append([])
            totRanks.append([])
            params.append(np.zeros((len(splits),nrPars[i]*2)))
            aprimes.append([])
            llikely.append([])
            
        
        for i,split in enumerate(splits):
            for j,model in enumerate(models):
                print split
                inf=experimentProcessing.load(basefile+model+str(split)+".info")
                inf.process()
                inf.rankOrder()
                nrs=len(inf.parametersMain[-1])*1.0
                #needs to be normalized first...
                params[j][i,:]=np.array(inf.avgtotsd+inf.avginhsd)
                aprimes[j].append(np.mean(inf.aprimes))
                llikely[j].append(np.mean(inf.lLikely))
                avginhrank=np.mean(inf.rankOrdersInh,0)
                inhRanks[j].append(avginhrank)
                totRanks[j].append(np.sum(inf.rankOrderSeen,(1,2))/((split**2-split)/2))
        
        nrslist=[]
        colors=['r','g','m']        
        paranames=['Beta','Gamma','Ro']
        plottypes=['o','x']
        for i in splits:
            nrslist.append(int(round(nrs/i)))
            
        for i,model in enumerate(models):
            plt.figure()
            plt.xlabel("Number of students per split")
            plt.ylabel("Average normalized standard deviation")
            for j in range(nrPars[i]):
                plt.plot(nrslist, params[i][:,j],'o'+colors[j]+'-',label=paranames[j]+'(Total)')
                plt.plot(nrslist,params[i][:,nrPars[i]+j],'o'+colors[j]+'--', label=paranames[j]+'(Internal)')
            plt.legend()
            plt.savefig(datset+model+"sds")
   
        for i,model in enumerate(models):
            plt.figure()
            plt.xlabel("Number of students per split")
            plt.ylabel("(average) Kendall rankorder over(/within) splits")
            for j in range(nrPars[i]):
                plt.plot(nrslist,np.array(totRanks[i])[:,j],'o'+colors[j]+'-',label=paranames[j]+'(Total)')
                plt.plot(nrslist,np.array(inhRanks[i])[:,j],'o'+colors[j]+'--', label=paranames[j]+'(Internal)')
            #plt.legend()
            plt.savefig(datset+model+"ranks")
        
        plt.figure()
        plt.xlabel("A-prime")
        plt.ylabel("Rank-order")
        for i,model in enumerate(models):
            for j in range(nrPars[i]):
                plt.plot(aprimes[i],np.array(totRanks[i])[:,j],plottypes[i]+"-")     
        plt.savefig(datset+"apVSrank")
        
        plt.figure()
        plt.xlabel("Average log likelihood")
        plt.ylabel("Rank-order")
        for i,model in enumerate(models):
            for j in range(nrPars[i]):
                plt.plot(llikely[i],np.array(totRanks[i])[:,j],plottypes[i]+"-")     
        plt.savefig(datset+"llVSrank")