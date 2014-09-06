# -*- coding: utf-8 -*-
import cPickle as pickle
import random as r
from collections import defaultdict
import copy

#Go from a cumulative distribution list to determine what kc's are
#linked to what item

def distribution(plist):
    n=r.random()
    for i in range(len(plist)):
        if n<plist[i]:
            return i+1
    return len(plist)+1

class edata:
    def checkdata(self):
        maxs=0
        for i in range(len(self.data)):
            if self.data[i][0]>maxs: 
                maxs=self.data[i][0]
            elif self.data[i][0]<maxs:
                print "Help, current student is lower than highest seen"
                print self.data[i][0],maxs
        sq=self.countStudentQuestions()
        
        dc=0
        for i in range(max(sq.keys())+1):
            for j in range(sq[i]):
                if self.data[dc][0]!=i:
                    print self.data[dc][0],i
                    
                dc+=1
        print max(sq.keys()), maxs
            
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
        self.testdata=None
        self.labels=None
        self.ikc=None
        self.nrs=None
        self.nrkc=None
        #in splitting kc's items or students may no longer be present in the set
        self.kcmis=[]
        self.itemmis=[]
        self.studentmis=[]
    
    def createMissing(self):
        iseen=defaultdict(int)
        kcseen=defaultdict(int)
        sseen=defaultdict(int)
        for d in self.giveData():
            sseen[d[0]]+=1
            iseen[d[1]]+=1
            for kc in self.ikc[d[1]]:
                kcseen[kc]+=1
        for i in range(self.nrs):
            if not sseen[i]:
                self.studentmis.append(i)
        for i in range(self.nrkc):
            if not kcseen[i]:
                self.kcmis.append(i)
        for i in range(len(self.ikc)):
            if not iseen[i]:
                self.itemmis.append(i)
        smap=[-1]*self.nrs
        skip=0
        for i in range(self.nrs):
            if not i in self.studentmis:
                smap[i]=i-skip
            else:
                skip+=1
        kcmap=[-1]*self.nrkc
        skip=0
        for i in range(self.nrkc):
            if not i in self.kcmis:
                kcmap[i]=i-skip
            else:
                skip+=1
        self.nrs-=len(self.studentmis)
        self.nrkc-=len(self.kcmis)
        #Not really implemented yet
        newikc=[]
        for i in range(len(self.ikc)):
#            if i in self.itemmis:
#                continue
            kclist=[]
            for kc in self.ikc[i]:
                kclist.append(kcmap[kc])
            self.ikc[i]=kclist
            newikc.append(kclist)
        #self.ikc=newikc
        for i in range(len(self.data)):
            d=self.data[i]
            self.data[i]=(smap[d[0]],d[1])
        for i in range(len(self.testdata)):
            d=self.testdata[i]
            baditem=False
            for kc in self.ikc[d[1]]:
                if kc in self.kcmis:
                    baditem=True
            if baditem:
                print "Baditem seen in testset: KC not present in train, item not added to testset"
                continue
            self.testdata[i]=(smap[d[0]],d[1],d[2])
        print "missing students/kcs/items vs total"
        print len(self.studentmis),len(self.kcmis),len(self.itemmis),self.nrs,self.nrkc,len(self.ikc)
            
    
    def addPoint(self,s,i,c):
        #Add a point, with student s, item i, and correctness c
        self.data.append((s,i))
        self.labels.append(c)
    
    def giveData(self):
        i=0
        while i<len(self.data):
            try:
                yield (self.data[i][0],self.data[i][1],self.labels[i])
            except:
                print "something wrong!"
                print self.data[i]
                print self.labels[i]
            i+=1

    def giveTestData(self):
        i=0
        while i<len(self.testdata):
            yield self.testdata[i]
#            except:
#                print "something wrong in giving testdata!"
#                print i,self.testdata[i],"testdata length",len(self.testdata)
                
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
        
        
    def initialize(self,ikc,nrs,nrkc,data=[],labels=[],testdata=[]):
        self.data=data
        self.labels=labels
        self.ikc=ikc
        self.nrs=nrs
        self.nrkc=nrkc
        self.testdata=testdata

    def initializeCopy(self,other,data=[],labels=[],testdata=[]):
        self.data=copy.deepcopy(data[:])
        self.labels=copy.deepcopy(labels[:])
        self.testdata=copy.deepcopy(testdata[:])
        self.ikc=copy.deepcopy(other.ikc)
        self.nrs=other.nrs
        self.nrkc=other.nrkc

        
        
    def clearData(self):
        self.data=[]
        self.labels=[]
        self.testdata=[]

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
        smap={}
        
        jump=0
        for i in range(max(sq.keys())+1):
            if sq[i]<nr:
                if not sq[i]==0:
                    removeS.append(i)
                jump+=1
            else:
                smap[i]=i-jump
        print len(removeS),len(sq),max(sq.keys())
        newData=[]
        newLabels=[]
        #enumerate leads to problems
        for i in range(len(self.data)):
            d=self.data[i]
            if d[0] not in removeS:
                newData.append((smap[d[0]],d[1]))
                newLabels.append(self.labels[i])
        self.data=newData
        self.labels=newLabels
        self.nrs=max(sq.keys())+1-jump
        self.updateItemMap()
        
    
    def removekcq(self,nr):
        updateData=False
        kcq=self.countKCQuestions()
        removeKC=[]
        removei=[]
        kcmap={}
        jump=0
        for i in range(max(kcq.keys())+1):
            if kcq[i]<nr:
                jump+=1
                if not kcq[i]==0:
                    removeKC.append(i)
            else:
                kcmap[i]=i-jump
        print len(removeKC),max(kcq.keys())
        for i in range(len(self.ikc)):
            for kc in removeKC:
                if kc in self.ikc[i]:
                    self.ikc[i].remove(kc)
            if len(self.ikc[i])==0:
                removei.append(i)
                updateData=True
            for j in range(len(self.ikc[i])):
                self.ikc[i][j]=kcmap[self.ikc[i][j]]
        print self.nrkc,len(removeKC)
        self.nrkc=max(kcq.keys())+1-jump

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
            self.updateItemMap()
               

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
        
        for i in range(len(self.data)):
            d=self.data[i]
            newData.append((d[0],it[d[1]]))
            newLabels.append(self.labels[i])    
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
        print maxs, maxi, maxkc, minkc, self.nrs, self.nrkc

    def splitDataS(self,parts):
        sets=[]
        for i in range(parts):
            sets.append(edata())
            sets[i].initializeCopy(self)
        sq=self.countStudentQuestions()
        print "checking:",sum(sq.values()),len(self.data)
        skip=0
        dCounter=0
        for i in range(max(sq.keys())+1):
            #every part gets an equal part from every student and a rest is left
            perS=sq[i]/parts
            rest=sq[i]%parts
            for j in range(parts):
                if ((j+skip)%parts)<rest: extra=1
                else: extra = 0
                for k in range(perS+extra):
                    sets[j].data.append(self.data[dCounter])
                    sets[j].labels.append(self.labels[dCounter])
                    
                    
                    if self.data[dCounter][0] != i:
                        print i,self.data[dCounter][0]
                        print "Student being processed and in data don't match!"
                    dCounter+=1
            skip=(skip+rest)%parts
        for i in range(parts):
            kc=sets[i].countKCQuestions()
            print max(kc), len(kc),self.nrkc, len(self.data)            
        return sets
            
            
    def splitDataStudent(self,parts):
        #splits the data in 'parts' # parts, where the records of any user
        #are all in the same part
        sets=[]
        for i in range(parts):
            sets.append(edata())
            sets[i].initializeCopy(self)
        smap=range(self.nrs)
        r.shuffle(smap)
        for i in range(len(smap)):
            smap[i]=smap[i]%parts
        for dat in self.giveData():
            sets[smap[dat[0]]].addPoint(dat[0],dat[1],dat[2])
        for dat in self.giveTestData():
            sets[smap[dat[0]]].testdata.append(dat)
        return sets

        
