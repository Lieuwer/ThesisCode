from collections import defaultdict
import random as r
import cPickle as pickle
import math as m
import numpy as np

def distribution(plist):
        n=r.random()
        for i in range(len(plist)):
            if n<plist[i]:
                return i+1
        return len(plist)+1

class dataGenerator:
    @staticmethod
    def loadFile(filename):
        filehandle=open (filename,"rb")
        return pickle.load(filehandle)

    def __init__(self,nrs,nri,nrkc,kcdist):
        #store the kc's belonging to each item
        self.ikc=[]
        #lists that will hold the parameters of items and students
        self.ca=[]
        self.cg=[]
        self.cr=[]
        self.cb=[]
        self.st=[]
        self.se=[]
        self.data=[]
        self.testdata=[]
        self.totalerror=0.0
        self.testerror=0.0
        
        #create student parameters
        for i in range(nrs):
            self.st.append(r.normalvariate(-.03,1))
            self.se.append(r.uniform(.01,.05))

        #create knowledge component parameters
        for i in range(nrkc):
            self.ca.append(r.uniform(.5,2))
            g=r.uniform(.5,2)
            self.cg.append(g)
            self.cr.append(g*r.uniform(.2,.8))
            self.cb.append(r.normalvariate(0,1.5))

        #associate kcs to items
        for i in range(nri):
            kcs=[]
            for i in range(distribution(kcdist)):
                kc = r.randrange(nrkc)
                #make sure no KC is double
                while kc in kcs:
                    kc = r.randrange(nrkc)
                kcs.append(kc)
            self.ikc.append(kcs)

        for s in range(nrs):
            #Number of questions answered by student, keep a list of the questions
            nrans=r.normalvariate(30,5)
            if nrans<1:
                nrans=1
            self.generateData(s,nrans)
        print "error in generating", self.totalerror/len(self.data)
        print "error in testdata", self.testerror/len(self.testdata)

    def generateData(self,s,nrans):
        totc=0
        totf=0
        #creates nrans number of datapoints for student with id s and adds them to data
        #keep track of questions answered correctly and questions answered wrongly
        kcc = [0]*len(self.ca)
        kcf = [0]*len(self.ca)
        #'roundoff' error makes expected values lower, not really problem
        for i in range(int(nrans)):
            #make sure to have a question that was not answered before
            answered=[]
            q=r.randrange(len(self.ikc))
            while q in answered:
                q=r.randrange(len(self.ikc))
            answered.append(q)
            x=0
            for kc in self.ikc[q]:
                x+=self.ca[kc]*self.st[s]/len(self.ikc[q])+self.se[s]*self.cg[kc]*kcc[kc]+self.se[s]*self.cr[kc]*kcf[kc]-self.cb[kc]
            if r.random()<(1/(1+m.exp(-x))):
                self.data.append((s,q,1))
                totc+=1
                self.totalerror+=(1/(1+m.exp(x)))
                for kc in self.ikc[q]:
                    kcc[kc]+=1

            else:
                self.data.append((s,q,0))
                totf+=1
                self.totalerror+=(1/(1+m.exp(-x)))
                for kc in self.ikc[q]:
                    kcf[kc]+=1
        #Finally get a single point of test data
        q=r.randrange(len(self.ikc))
        x=0
        for kc in self.ikc[q]:
            x+=self.ca[kc]*self.st[s]/len(self.ikc[q])+self.se[s]*self.cg[kc]*kcc[kc]+self.se[s]*self.cr[kc]*kcf[kc]-self.cb[kc]
        if r.random()<(1/(1+m.exp(-x))):
            self.testdata.append((s,q,1))
            totc+=1
            self.testerror+=(1/(1+m.exp(x)))
            for kc in self.ikc[q]:
                kcc[kc]+=1

        else:
            self.testdata.append((s,q,0))
            totf+=1
            self.testerror+=(1/(1+m.exp(-x)))
            for kc in self.ikc[q]:
                kcf[kc]+=1
        print totc,totf


    def save(self, filename):
        filehandle= open (filename,"wb")
        pickle.dump(self,filehandle)
        filehandle.close()
        
    def saveData(data,filename):
        filehandle= open (filename,"wb")
        pickle.dump(data,filehandle)
        filehandle.close()



