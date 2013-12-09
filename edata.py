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
        
    def removesq(self,nr):
        #Remove all students that answered less then nr questions
        sq=self.countStudentQuestions()
        removeS=[]
        for s,q in sq.iteritems():
            if q<nr:
                removeS.append(s)
        print len(removeS),len(sq)
        newData=[]
        for d in self.data:
            if d[0] not in removeS:
                newData.append(d)
        self.data=newData
    
    def removekcq(self,nr):
        doIteration=True
        kcq=self.countKCQuestions()
        oldlen=0
        while(len(kcq)!=oldlen):
            oldlen=len(kcq)
            removeKC=[]
            removei=[]
            for kc,q in kcq.iteritems():
                if q<nr:
                    removeKC.append(kc)
            print len(removeKC),len(kcq)
            for i in range(len(self.ikc)):
                for kc in removeKC:
                    if kc in self.ikc[i]:
                        self.ikc[i].remove(kc)
                if len(self.ikc[i])==0:
                    removei.append(i)
            if doIteration:
                newData=[]
                for d in self.data:
                    if d[1] not in removei:
                        newData.append(d)
                self.data=newData
            kcq=self.countKCQuestions()    

    def refactor(self):
        #Remove items and students by shifting the numbers.
        items=[0]*len(self.ikc)
        kc=self.countKCQuestions()
        s=self.countStudentQuestions()
        for d in self.data():
            items[d[1]]+=1
        jump=0
        for i in range(len(items)):
            if items[i]==0:
                jump+=1
            else:
                items[i]=i-jump
                self.ikc[i]=ikc[i-jump]
        for i in range(jumps):
            self.ikc.del(-1)
        jump=0
        for i in range(len(kc.values)):
            if kc[i]==0:
                jump+=1
            else:
                kc[i]=i-jump
        
        jump=0
        for i in range(len(s.values)):
            if s[i]==0:
                jump+=1
            else:
                s[i]=i-jump
            
        
                
       
    def removekcsq(self,nrk,nrs):
        oldlen=0
        while (oldlen!=len(self.data)):
            oldlen=len(self.data)
            self.removesq(nrs)
            self.removekcq(nrk)
        
            
            
        

        
