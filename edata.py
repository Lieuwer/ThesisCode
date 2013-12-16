# -*- coding: utf-8 -*-
import cPickle as pickle
import random as r
from collections import defaultdict

#Go from a cumulative distribution list to determine what kc's are
#linked to what item

def distribution(plist):
    n=r.random()
    for i in range(len(plist)):
        if n<plist[i]:
            return i+1
    return len(plist)+1

class edata:
    def save(self, filename):
        filehandle= open (filename,"wb")
        pickle.dump(self,filehandle)
        filehandle.close()
        
    @staticmethod
    def load(filename):
        filehandle=open (filename,"rb")
        return pickle.load(filehandle)
    
    def __len__(self):
        return len(self.data)


    def __init__(self):
        self.data=None
        self.labels=None
        self.ikc=None
        self.nrs=None
        self.nrkc=None

    def giveData(self):
        i=0
        while i<len(self.data):
            yield (self.data[i][0],self.data[i][1],self.labels[i])
            i+=1

    def generate(self,nrs,nrkc,nri):
        self.data=[]
        self.labels=[]
        self.nrs=nrs
        self.nrkc=nrkc
        self.ikc=[]
        kcdist = [.4,.65,.85,.99]

        
        for i in range(nri):
            kcs=[]
            for i in range(distribution(kcdist)):
                kc = r.randrange(nrkc)
                #make sure no KC is double
                while kc in kcs:
                    kc = r.randrange(nrkc)
                kcs.append(kc)
            self.ikc.append(kcs)
        
        
    def initialize(self,ikc,nrs,nrkc,data=[],labels=[]):
        self.data=data
        self.labels=labels
        self.ikc=ikc
        self.nrs=nrs
        self.nrkc=nrkc

    def initializeCopy(self,other,data=[],labels=[]):
        self.data=data
        self.labels=labels
        self.ikc=other.ikc
        self.nrs=other.nrs
        self.nrkc=other.nrkc
        
        
    def clearData(self):
        self.data=[]
        self.labels=[]

    def countStudentQuestions(self):
        s=defaultdict(int)
        for d in self.data:
            s[d[0]]+=1
        return s
    
    def countKCQuestions(self):
        s=defaultdict(int)
        for d in self.data:
            for kc in self.ikc[d[1]]:
                s[kc]+=1
        return s
        
    def countItemQuestions(self):
        s=defaultdict(int)
        for d in self.data:
            s[d[1]]+=1
        return s
        
    def removesq(self,nr):
        #Remove all students that answered less then nr questions
        sq=self.countStudentQuestions()
        removeS=[]
        
        jump=0
        for i in range(len(sq)):
            if sq[i]<nr:
                removeS.append(sq[i])
                jump+=1
            else:
                sq[i]=i-jump
        print len(removeS),len(sq)
        newData=[]
        newLabels=[]
        #enumerate leads to problems
        i=0
        for d in self.data:
            if d[0] not in removeS:
                newData.append((sq[d[0]],d[1]))
                newLabels.append(self.labels[i])    
            i+=1
        self.data=newData
        self.labels=newLabels
        self.updateItemMap()
        
    
    def removekcq(self,nr):
        updateData=False
        kcq=self.countKCQuestions()
        removeKC=[]
        removei=[]
        
        jump=0
        for i in range(len(kcq)):
            if kcq[i]<nr:
                jump+=1
                removeKC.append(kcq)
                kcq[i]=-1
            else:
                kcq[i]=i-jump
        print len(removeKC),len(kcq)
        for i in range(len(self.ikc)):
            for kc in removeKC:
                if kc in self.ikc[i]:
                    self.ikc[i].remove(kc)
            if len(self.ikc[i])==0:
                removei.append(i)
                updateData=True
            for j in range(len(self.ikc[i])):
                self.ikc[i][j]=kcq[self.ikc[i][j]]

        if updateData:
            newData=[]
            newLabels=[]
            #enumerate leads to error, so...
            i=0
            for d in self.data:
                if d[1] not in removei:
                    newData.append(d)
                    newLabels.append(self.labels[i])
                i+=1
            self.data=newData
            self.labels=newLabels
            self.updataItemMap()
               

    def updateItemMap(self):
        it=self.countItemQuestions()
        jump=0
        for i in range(len(self.ikc)):
            if it[i]==0:
                jump+=1
            else:
                it[i]=i-jump
                self.ikc[i-jump]=self.ikc[i]
        for i in range(jump):
            self.ikc.pop(-1)
        newData=[]
        newLabels=[]
        #enumerate leads to problems
        i=0
        for d in self.data:
            newData.append((d[0],it[d[1]]))
            newLabels.append(self.labels[i])    
            i+=1
        self.data=newData
        self.labels=newLabels

    def removekcsq(self,nrk,nrs):
        oldlen=0
        while (oldlen!=len(self.data)):
            oldlen=len(self.data)
            self.removesq(nrs)
            self.removekcq(nrk)
        
        maxkc=0
        maxs=0
        maxi=0
        minkc=10
        for d in self.data:
            if d[0]>maxs: maxs=d[0]
            if d[1]>maxi: maxi=d[1]
            if len(self.ikc[d[1]])<minkc: minkc=len(self.ikc[d[1]])
            if max(self.ikc[d[1]])>maxkc:maxkc=max(self.ikc[d[1]])
        print maxs, maxi, maxkc, minkc
            
    def splitDataS(self,parts):
        sets=[]
        for i in range(parts):
            sets.append(edata())
            sets[i].initializeCopy(self)
        for i in range(len(self.data)):
            sets[i%parts].data.append(self.data[i])
        for i in range(parts):
            kc=sets[i].countKCQuestions()
            print len(kc)
            
        return sets
            
            
        

        
