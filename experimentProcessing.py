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
    
    def __init__(self,mainModel,ap,ll,inter,ainter,var,ranks,avginhranks,inhparvar,totparvar):
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
        
        self.inhparvar=inhparvar
        self.totparvar=totparvar
        
        
        #should keep track of total amount of data...
        self.records=len(mainModel.data)
        self.nrs=mainModel.data.nrs
        self.nrkc=mainModel.data.nrkc

        
    def process(self):
        splits=len(self.KCCleaned)
        filebase=str(splits)
        kcpars=0
        if len(self.paranames)==3:
            filebase="afm"+filebase
            kcpars=2
        elif self.paranames[2]=="ro":
            filebase="pfa"+filebase
            kcpars=3
        else:
            filebase="eir"+filebase
            kcpars=2
        
        for i in range(len(self.parametersMain[0])):
                #Taking learning factor as guidance as this is most likely to have too little data
                if np.isnan(self.variancesSeen[0][i]) or np.isnan(self.variancesSeen[1][i]) or (len(self.variancesSeen)>2 and np.isnan(self.variancesSeen[2][i])):
                    self.kcLeftOut.append(i)
        for k in range(kcpars):
            self.variancesSeen[k]=np.delete(self.variancesSeen[k],np.array(self.kcLeftOut))
            self.avgvariancesInh[k]=np.delete(self.avgvariancesInh[k],np.array(self.kcLeftOut))
            self.parametersMain[k]=np.delete(self.parametersMain[k],np.array(self.kcLeftOut))
            
            
#            plt.figure()
#            plt.xlabel("Parameter value")
#            plt.ylabel("Paramater standard deviation")
#            plt.plot(self.parametersMain[k], np.sqrt(self.variancesSeen[k]),"o", label="Seen")
#            plt.plot(self.parametersMain[k], np.sqrt(self.avgvariancesInh[k]),"x", label="Inherent")
#            plt.legend()
#            plt.savefig(filebase+self.paranames[k]+"_valVSvar")
#            
#            plt.figure()
#            plt.xlabel("seen sd")
#            plt.ylabel("inherent sd")
#            plt.plot(np.sqrt(self.variancesSeen[k]), np.sqrt(self.avgvariancesInh[k]),"o")
#            plt.savefig(filebase+self.paranames[k]+"_svarVivar")
            
            
        self.avgtotsd=[]
        self.avginhsd=[]
        for i in range(kcpars):
            self.avgtotsd.append(np.mean(np.sqrt(self.variancesSeen[i])))
            self.avginhsd.append(np.mean(np.sqrt(self.avgvariancesInh[i])))
        totalKC=0.0
        totalS=0.0
        for i in range(len(self.KCCleaned)):
            totalKC+=len(self.KCCleaned[i])
            totalS+=len(self.studentsCleaned[i])
#        print "stuff cleaned", len(self.kcLeftOut),totalKC/len(self.KCCleaned),(totalS-self.nrs*(len(self.studentsCleaned)-1))/len(self.studentsCleaned)
         
         
    def rankOrder(self):
        
        avginhrank=np.mean(self.rankOrdersInh,0)
        for i in range(self.rankOrderSeen.shape[0]):
            print self.paranames[i],avginhrank[i], np.sum(self.rankOrderSeen[i,:,:])/((self.rankOrderSeen.shape[2]**2-self.rankOrderSeen.shape[2])/2)
            print "in/tot average sd",np.mean(np.sqrt(self.avgvariancesInh[i])), np.mean(np.sqrt(self.variancesSeen[i]))
            #Ineherent vs variance rankorder:
            print "rankorder inherent vs seen variance:", stat.spearmanr(self.avgvariancesInh[i],self.variancesSeen[i])[0]
        
    @staticmethod
    def allexp():
        datasets=["algebra","bridge","gong"]
        models=['afm','pfa','eirt']
        splits=[6,8,12,16,32]
        nrPars=[2,3,2]
        invar=[]
        totvar=[]
        ranks=[]
        
        
        for i in range(len(models)):
            ranks.append([])
            invar.append([])
            totvar.append([])
            for j in range(nrPars[i]):
                ranks[i].append([])
                totvar[i].append([])
                invar[i].append([])
                totvar[i].append([])
                for k in datasets:
                    ranks[i][j].append([])
                    invar[i][j].append(np.array([]))
                    totvar[i][j].append(np.array([]))
        colors=['b','orange','m']        
        plottypes=['o','x','v']
        plt.figure(0)
        plt.xlabel("A-prime")
        plt.ylabel("Rank-order")
        plt.figure(1)
        plt.xlabel("Average log likelihood")
        plt.ylabel("Rank-order")
        plt.figure(2)
        plt.xlabel("Number of records per split per KC")
        plt.ylabel("(average) Kendall rankorder over(/within) splits")
        plt.figure(3)
        plt.xlabel("Number of records per split per KC")
        plt.ylabel("Average normalized standard deviation over(/within) splits")
        
        for k,dataset in enumerate(datasets):
            params=[]
            recperkc=0
            aprimes=[]
            llikely=[]
            totRanks=[]
            inhRanks=[]
            for i in range(len(models)):
                inhRanks.append([])
                totRanks.append([])
                params.append(np.zeros((len(splits),nrPars[i]*2)))
                aprimes.append([])
                llikely.append([])
            basefile="D:\\spyderstuff\\ThesisCode\\Experiments\\1119"+dataset+"\\"
            for i,split in enumerate(splits):
                for j,model in enumerate(models):
                    
                    inf=experimentProcessing.load(basefile+model+str(split)+".info")
                    inf.process()
                    inf.rankOrder()
                    recperkc=inf.records*1.0/inf.nrkc
#                    inf.avgtotsd/=np.std(np.array(inf.parametersMain[:nrPars[j]]),1)
#                    inf.avginhsd/=np.std(np.array(inf.parametersMain[:nrPars[j]]),1)
                    inf.avgtotsd/=(np.mean(np.sqrt(np.array(inf.totparvar)),0)[:nrPars[j]])
                    inf.avginhsd/=(np.mean(np.sqrt(np.array(inf.inhparvar)),0)[:nrPars[j]])
                    params[j][i,:]=np.concatenate([inf.avgtotsd,inf.avginhsd])
                    aprimes[j].append(np.mean(inf.aprimes))
                    llikely[j].append(np.mean(inf.lLikely))
                    avginhrank=np.mean(inf.rankOrdersInh,0)
                    inhRanks[j].append(avginhrank)
                    totRanks[j].append(np.sum(inf.rankOrderSeen,(1,2))/((split**2-split)/2))
                    for l in range(nrPars[j]):
                        invar[j][l][k]=np.concatenate([invar[j][l][k],inf.avgvariancesInh[l]])
                        totvar[j][l][k]=np.concatenate([totvar[j][l][k],inf.variancesSeen[l]])
                        ranks[j][l][k].append(stat.spearmanr(inf.avgvariancesInh[l],inf.variancesSeen[l])[0])
            nrslist=[] 
            for i in splits:
                nrslist.append((recperkc/i))
            plt.figure(0)
            for i,model in enumerate(models):
                for j in range(nrPars[i]):
                    plt.plot(aprimes[i],params[i][:,j],plottypes[i],color=colors[j])
            plt.figure(1)
            for i,model in enumerate(models):
                for j in range(nrPars[i]):
                    plt.plot(llikely[i],params[i][:,j],plottypes[i],color=colors[j])
                    
        
            plt.figure(2)
            for i,model in enumerate(models):
                for j in range(nrPars[i]):
                    plt.plot(nrslist,np.array(totRanks[i])[:,j],plottypes[i]+'-',color=colors[j])
                    plt.plot(nrslist,np.array(inhRanks[i])[:,j],plottypes[i]+'--',color=colors[j])
            plt.figure(3)
            for i,model in enumerate(models):
                for j in range(nrPars[i]):
                    plt.plot(nrslist,params[i][:,j],plottypes[i]+'-',color=colors[j])
                    plt.plot(nrslist,params[i][:,nrPars[i]+j],plottypes[i]+'--',color=colors[j])

            
        plt.figure(0)
        plt.savefig("allaprimes")
        plt.figure(1)
        plt.savefig("alllikely")
        plt.figure(2)
        plt.savefig("allmodranksKC")
        plt.figure(3)
        plt.savefig("allmodsdsKC")
        
        for i,model in enumerate(models):
            print "model is",model
            for j in range(nrPars[i]):
                print " part looked at",j
                totalin=np.array([])
                totalto=np.array([])
                
                for k,dat in enumerate(datasets):
                    print "%.2f(%.2f)"%(stat.spearmanr(invar[i][j][k],totvar[i][j][k])[0],np.mean(ranks[i][j][k]))
                    print "  dataset:", dat, stat.spearmanr(invar[i][j][k],totvar[i][j][k])[0]
                    print "   Average over splits:",np.mean(ranks[i][j][k])
                    totalin=np.concatenate([invar[i][j][k],totalin])
                    totalto=np.concatenate([totvar[i][j][k],totalto])
                print "  Overall:",stat.spearmanr(totalin,totalto)[0]
                print "%.2f(%.2f)"%(stat.spearmanr(totalin,totalto)[0],np.mean(ranks[i][j])) 
                    
            
if __name__ == "__main__":
        experimentProcessing.allexp()
        assert(False)

#        inf=experimentProcessing.load("eirt12.info")
#        inf.process()
#        inf.rankOrder()
#        assert(False)
    
        temp=np.zeros((2,5))
        pick=0
        datsets=["bridge","algebra","gong"]
        basefile="D:\\spyderstuff\\ThesisCode\\Experiments\\1119"+datsets[pick]+"\\"
        models=['afm','pfa','eirt']
        splits=[6,8,12,16,32]
        nrPars=[2,3,2]
        params=[]
        totRanks=[]
        inhRanks=[]
        aprimes=[]
        llikely=[]
        parstds=[]
        
        invstoRank=[]
        
        #relative variance of parameters to the variance of parameters in mainmodel. List for the models, rows for parameters (first inh, then tot).
        parvar=[]
        
        nstudents=0
        nkcs=0
        nrecords=0
        #Change to Total questions
        nrs=0
        
        for i in range(len(models)):
            parvar.append(np.zeros((nrPars[i]*2,len(splits))))
            inhRanks.append([])
            totRanks.append([])
            params.append(np.zeros((len(splits),nrPars[i]*2)))
            aprimes.append([])
            llikely.append([])
            invstoRank.append(np.zeros((len(splits),nrPars[i]*2)))
            
        
        for i,split in enumerate(splits):
            for j,model in enumerate(models):
                print split, model
                
                inf=experimentProcessing.load(basefile+model+str(split)+".info")
                print "parvar inf", np.mean(np.array(inf.totparvar),0)[1],np.std(np.array(inf.totparvar),0)[1]                
                nrs=inf.records*1.0/inf.nrkc
                inf.process()                            
                temp[0,i]+=len(inf.kcLeftOut)
                totK=0.0
                for l in inf.KCCleaned:
                    totK+=len(l)
                temp[1,i]+=totK/len(inf.KCCleaned)
                #inf.rankOrder()
                #nrs=len(inf.parametersMain[-1])*1.0
                #needs to be normalized first...
                
                #change here!
#                inf.avgtotsd/=np.std(np.array(inf.parametersMain[:nrPars[j]]),1)
#                inf.avginhsd/=np.std(np.array(inf.parametersMain[:nrPars[j]]),1)

                inf.avgtotsd/=(np.mean(np.sqrt(np.array(inf.totparvar)),0)[:nrPars[j]])
                inf.avginhsd/=(np.mean(np.sqrt(np.array(inf.inhparvar)),0)[:nrPars[j]])
                   
                
                
                mainparvar=np.var(np.reshape(np.concatenate(inf.parametersMain[:nrPars[j]]),(nrPars[j],len(inf.parametersMain[0]))),1)
                print "\n sanity check:", mainparvar
                parvar[j][:,i]=np.concatenate([np.mean(np.sqrt(np.array(inf.totparvar)),0)[:nrPars[j]]/mainparvar,np.mean(np.sqrt(np.array(inf.inhparvar)),0)[:nrPars[j]]/mainparvar])
                params[j][i,:]=np.concatenate([inf.avgtotsd,inf.avginhsd])
                aprimes[j].append(np.mean(inf.aprimes))
                llikely[j].append(np.mean(inf.lLikely))
                avginhrank=np.mean(inf.rankOrdersInh,0)
                inhRanks[j].append(avginhrank)
                totRanks[j].append(np.sum(inf.rankOrderSeen,(1,2))/((split**2-split)/2))
                for k in range(nrPars[j]):
                    invstoRank[j][i,k]=stat.spearmanr(inf.avgvariancesInh[k],inf.variancesSeen[k])[0]
                    
                
        temp/=3
        for i in range(5):
            print "%.1f(%.1f)&"%(temp[0,i],temp[1,i])
        
        nrslist=[]
        colors=['b','orange','m']        
        paranames=['Beta','Gamma/Alpha','Ro']
        plottypes=['o','x','v']
        #print "\nNRS:", nrs
        for i in splits:
            nrslist.append((nrs/i))
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
        plt.ylabel("(average) Kendall tau over(/within) splits")
        for i,model in enumerate(models):
            for j in range(nrPars[i]):
                plt.plot(nrslist,np.array(totRanks[i])[:,j],plottypes[i]+'-',label=paranames[j]+'(Total)',color=colors[j])
                plt.plot(nrslist,np.array(inhRanks[i])[:,j],plottypes[i]+'--', label=paranames[j]+'(Internal)',color=colors[j])
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
                plt.plot(nrslist,params[i][:,j],plottypes[i]+'-',label=paranames[j]+'(Total)',color=colors[j])
                plt.plot(nrslist,params[i][:,nrPars[i]+j],plottypes[i]+'--', label=paranames[j]+'(Internal)',color=colors[j])
            #plt.legend()
        plt.savefig(datsets[pick]+"allmodsdsKC")
        
        
        fig,ax=plt.subplots(1,1)
#        ax.set_ylim((0,8))
        plt.xlabel("Number of records per split per KC")
        plt.ylabel("Relative standard deviation of parameter values")
        for i,model in enumerate(models):
            for j in range(nrPars[i]):
                if True: #j==0 or (j<2 and i!=0): 
                    plt.plot(nrslist,parvar[i][j,:],plottypes[i]+'-',label=paranames[j]+'(Total)',color=colors[j])
                    plt.plot(nrslist,parvar[i][nrPars[i]+j,:],plottypes[i]+'--', label=paranames[j]+'(Internal)',color=colors[j])
            #plt.legend()
        plt.savefig(datsets[pick]+"allmodsparvar")
        
##
        #Get a legend figure
#        plt.figure()
#        labels=[]
#        plt.plot([0,0],[1,1],"k-", label="Total")
#        labels.append(plt.plot([0,0],[1,1],"k--", label="Inherent")[0])
#        for i in range(len(colors)):
#            labels.append(plt.plot([0,0],[1,1],"-",label=paranames[i],color=colors[i]))
#        for i in range(len(plottypes)):
#            labels.append(plt.plot([0,0],[1,1],plottypes[i]+"k", label=models[i]))
#        plt.legend()
#        plt.savefig("legend")
#        
#        
#        for j,model in enumerate(models):
#                for k in range(nrPars[j]):
#                    print "%.2f (%.3f)"%(np.mean(invstoRank[j],0)[k],np.std(invstoRank[j],0)[k])
#                   