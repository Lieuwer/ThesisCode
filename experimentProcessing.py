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
import matplotlib.patches as mpatches
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
    
    def __init__(self,mainModel,ap,ll,inter,ainter,var,ranks,avginhranks):
        #Names of the parameters
        self.paranames=mainModel.paranames
        #The internalvariances, list of length #par types with (nrkc x nrsplits) array. Missing values have NaN
        self.variancesInh=inter
        #Cleaned up avg variances (NaN values removed)
        self.avgvariancesInh=ainter
        #variances over the splits
        self.variancesSeen=var
        #Parameters of the main model, useful for figures and normalizing
        self.parametersMain=mainModel.parameters
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
        self.records=len(mainModel.data)
        self.nrs=mainModel.data.nrs
        self.nrkc=mainModel.data.nrkc

        
    def process(self):
        splits=len(self.KCCleaned)
        filebase=str(splits)
       
        if len(self.paranames)==3:
            filebase="afm"+filebase
        else:
            filebase="pfa"+filebase
        self.kcmis=np.zeros(len(self.parametersMain[0]))
        
        for i in range(len(self.parametersMain[0])):
                #Taking learning factor as guidance as this is most likely to have too little data
                if np.isnan(self.variancesSeen[1][i]) or (len(self.variancesSeen)>2 and np.isnan(self.variancesSeen[2][i])):
                    self.kcLeftOut.append(i)
        for k in range(len(self.parametersMain)-1):
            self.variancesSeen[k]=np.delete(self.variancesSeen[k],np.array(self.kcLeftOut))
            self.avgvariancesInh[k]=np.delete(self.avgvariancesInh[k],np.array(self.kcLeftOut))
            self.parametersMain[k]=np.delete(self.parametersMain[k],np.array(self.kcLeftOut))
            plt.figure()
            plt.xlabel("Parameter value")
            plt.ylabel("Paramater standard deviation")
            plt.plot(self.parametersMain[k], np.sqrt(self.variancesSeen[k]),"o", label="Seen")
            plt.plot(self.parametersMain[k], np.sqrt(self.avgvariancesInh[k]),"x", label="Inherent")
            plt.savefig(filebase+self.paranames[k]+"_valVSvar")
            
            plt.figure()
            plt.xlabel("seen sd")
            plt.ylabel("inherent sd")
            plt.plot(np.sqrt(self.variancesSeen[k]), np.sqrt(self.avgvariancesInh[k]),"o")
            plt.savefig(filebase+self.paranames[k]+"_svarVivar")
        self.avgtotsd=[]
        self.avginhsd=[]
        for i in range(len(self.paranames)-1):
            self.avgtotsd.append(np.mean(np.sqrt(self.variancesSeen[i])))
            self.avginhsd.append(np.mean(np.sqrt(self.avgvariancesInh[i])))
        for i in self.KCCleaned:
            for j in i:
                self.kcmis[j]+=1
            
    def rankOrder(self):
        
        avginhrank=np.mean(self.rankOrdersInh,0)
        for i in range(self.rankOrderSeen.shape[0]):
            print self.paranames[i],avginhrank[i], np.sum(self.rankOrderSeen[i,:,:])/((self.rankOrderSeen.shape[2]**2-self.rankOrderSeen.shape[2])/2)
            print "in/tot average sd",np.mean(np.sqrt(self.avgvariancesInh[i])), np.mean(np.sqrt(self.variancesSeen[i]))
            #Ineherent vs variance rankorder:
            print "rankorder inherent vs seen variance:", stat.spearmanr(self.avgvariancesInh[i],self.variancesSeen[i])[0]
        
    @staticmethod
    def allexp():
        datasets=["algebra","gong"]
        models=['afm','pfa']
        splits=[6,8,12,16,32]
        nrPars=[2,3]
        invar=[]
        totvar=[]
        for i in range(len(models)):
            invar.append([])
            totvar.append([])
            for j in range(nrPars[i]):
                invar[i].append([])
                totvar[i].append([])
                for k in datasets:
                    invar[i][j].append(np.array([]))
                    totvar[i][j].append(np.array([]))
        colors=['r','g','m']        
        plottypes=['o','x']
        plt.figure(0)
        plt.xlabel("A-prime")
        plt.ylabel("Rank-order")
        plt.figure(1)
        plt.xlabel("Average log likelihood")
        plt.ylabel("Rank-order")
        for k,dataset in enumerate(datasets):
            
            aprimes=[[],[]]
            llikely=[[],[]]
            totRanks=[[],[]]
            basefile="D:\\spyderstuff\\ThesisCode\\Experiments\\1106"+dataset+"\\"
            for i,split in enumerate(splits):
                for j,model in enumerate(models):
                    inf=experimentProcessing.load(basefile+model+str(split)+".info")
                    inf.process()
                    inf.rankOrder()
                    aprimes[j].append(np.mean(inf.aprimes))
                    llikely[j].append(np.mean(inf.lLikely))
                    totRanks[j].append(np.sum(inf.rankOrderSeen,(1,2))/((split**2-split)/2))
                    for l in range(nrPars[j]):
                        invar[j][l][k]=np.concatenate([invar[j][l][k],inf.avgvariancesInh[l]])
                        totvar[j][l][k]=np.concatenate([totvar[j][l][k],inf.variancesSeen[l]])
            plt.figure(0)
            for i,model in enumerate(models):
                for j in range(nrPars[i]):
                    plt.plot(aprimes[i],np.array(totRanks[i])[:,j],plottypes[i]+colors[j])
            plt.figure(1)
            for i,model in enumerate(models):
                for j in range(nrPars[i]):
                    plt.plot(llikely[i],np.array(totRanks[i])[:,j],plottypes[i]+colors[j])
        plt.figure(0)
        plt.savefig("allaprimes")
        plt.figure(1)
        plt.savefig("alllikely")

        for i,model in enumerate(models):
            print "model is",model
            for j in range(nrPars[i]):
                print " part looked at",j
                totalin=np.array([])
                totalto=np.array([])
                for k,dat in enumerate(datasets):
                    print "  dataset:", dat, stat.spearmanr(invar[i][j][k],totvar[i][j][k])[0]                  
                    totalin=np.concatenate([invar[i][j][k],totalin])
                    totalto=np.concatenate([totvar[i][j][k],totalto])
                print "  Overall:",stat.spearmanr(totalin,totalto)[0]
                    
            
if __name__ == "__main__":
        experimentProcessing.allexp()
        assert(False)
#        inf=experimentProcessing.load("pfa6.info")
#        inf.process()
#        inf.rankOrder()
        pick=2
        datsets=["bridge","algebra","gong"]
        basefile="D:\\spyderstuff\\ThesisCode\\Experiments\\1106"+datsets[pick]+"\\"
        models=['afm','pfa']
        splits=[6,8,12,16,32]
        nrPars=[2,3]
        params=[]
        totRanks=[]
        inhRanks=[]
        aprimes=[]
        llikely=[]
        parstds=[]
        
        invstoRank=[]
        
        nstudents=0
        nkcs=0
        nrecords=0
        #Change to Total questions
        nrs=0
        
        for i in range(len(models)):
            inhRanks.append([])
            totRanks.append([])
            params.append(np.zeros((len(splits),nrPars[i]*2)))
            aprimes.append([])
            llikely.append([])
            invstoRank.append(np.zeros((len(splits),nrPars[i]*2)))
            
        
        for i,split in enumerate(splits):
            for j,model in enumerate(models):
                print split
                inf=experimentProcessing.load(basefile+model+str(split)+".info")
                nrs=inf.records*1.0/inf.nrkc
                inf.process()
                inf.rankOrder()
                #nrs=len(inf.parametersMain[-1])*1.0
                #needs to be normalized first...
                inf.avgtotsd/=np.std(np.array(inf.parametersMain[:-1]),1)
                inf.avginhsd/=np.std(np.array(inf.parametersMain[:-1]),1)
                params[j][i,:]=np.concatenate([inf.avgtotsd,inf.avginhsd])
                aprimes[j].append(np.mean(inf.aprimes))
                llikely[j].append(np.mean(inf.lLikely))
                avginhrank=np.mean(inf.rankOrdersInh,0)
                inhRanks[j].append(avginhrank)
                totRanks[j].append(np.sum(inf.rankOrderSeen,(1,2))/((split**2-split)/2))
                for k in range(nrPars[j]):
                    invstoRank[j][i,k]=stat.spearmanr(inf.avgvariancesInh[k],inf.variancesSeen[k])[0]
                    
                
                    
        
        nrslist=[]
        colors=['r','g','m']        
        paranames=['Beta','Gamma/Eta','Ro']
        plottypes=['o','x']
        for i in splits:
            nrslist.append(int(round(nrs/i)))
#            
##        for i,model in enumerate(models):
##            plt.figure()
##            plt.xlabel("Number of records per split per KC")
##            plt.ylabel("Average normalized standard deviation")
##            for j in range(nrPars[i]):
##                plt.plot(nrslist, params[i][:,j],'o'+colors[j]+'-',label=paranames[j]+'(Total)')
##                plt.plot(nrslist,params[i][:,nrPars[i]+j],'o'+colors[j]+'--', label=paranames[j]+'(Internal)')
##            plt.legend()
##            plt.savefig(datset+model+"sdsKC")
##   
##        for i,model in enumerate(models):
##            plt.figure()
##            plt.xlabel("Number of records per split per KC")
##            plt.ylabel("(average) Kendall rankorder over(/within) splits")
##            for j in range(nrPars[i]):
##                plt.plot(nrslist,np.array(totRanks[i])[:,j],'o'+colors[j]+'-',label=paranames[j]+'(Total)')
##                plt.plot(nrslist,np.array(inhRanks[i])[:,j],'o'+colors[j]+'--', label=paranames[j]+'(Internal)')
##            #plt.legend()
##            plt.savefig(datset+model+"ranksKC")
##        
##        plt.figure()
##        plt.xlabel("A-prime")
##        plt.ylabel("Rank-order")
##        for i,model in enumerate(models):
##            for j in range(nrPars[i]):
##                plt.plot(aprimes[i],np.array(totRanks[i])[:,j],plottypes[i]+"-")     
##        plt.savefig(datset+"apVSrank")
##        
##        plt.figure()
##        plt.xlabel("Average log likelihood")
##        plt.ylabel("Rank-order")
##        for i,model in enumerate(models):
##            for j in range(nrPars[i]):
##                plt.plot(llikely[i],np.array(totRanks[i])[:,j],plottypes[i]+"-")     
##        plt.savefig(datset+"llVSrank")
##        
##        
        plt.figure()
        plt.xlabel("Number of records per split per KC")
        plt.ylabel("(average) Kendall rankorder over(/within) splits")
        for i,model in enumerate(models):
            for j in range(nrPars[i]):
                plt.plot(nrslist,np.array(totRanks[i])[:,j],plottypes[i]+colors[j]+'-',label=paranames[j]+'(Total)')
                plt.plot(nrslist,np.array(inhRanks[i])[:,j],plottypes[i]+colors[j]+'--', label=paranames[j]+'(Internal)')
            #plt.legend()
        plt.savefig(datsets[pick]+"allmodranksKC")
##
##
##        
        plt.figure()
        plt.xlabel("Number of records per split per KC")
        plt.ylabel("Average normalized standard deviation over(/within) splits")
        for i,model in enumerate(models):
            for j in range(nrPars[i]):
                plt.plot(nrslist,params[i][:,j],plottypes[i]+colors[j]+'-',label=paranames[j]+'(Total)')
                plt.plot(nrslist,params[i][:,nrPars[i]+j],plottypes[i]+colors[j]+'--', label=paranames[j]+'(Internal)')
            #plt.legend()
        plt.savefig(datsets[pick]+"allmodsdsKC")
##
##        #Get a legend figure
##        plt.figure()
##        labels=[]
##        plt.plot([0,0],[1,1],"k-", label="Total")
##        labels.append(plt.plot([0,0],[1,1],"k--", label="Inherent")[0])
##        for i in range(len(colors)):
##            labels.append(plt.plot([0,0],[1,1],colors[i]+"-",label=paranames[i]))
##        for i in range(len(plottypes)):
##            labels.append(plt.plot([0,0],[1,1],plottypes[i]+"k", label=models[i]))
##        plt.legend()
##        plt.savefig("legend")
#        
#        
#        for j,model in enumerate(models):
#                for k in range(nrPars[j]):
#                    print "%.2f (%.3f)"%(np.mean(invstoRank[j],0)[k],np.std(invstoRank[j],0)[k])
#                   