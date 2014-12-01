# -*- coding: utf-8 -*-
import cPickle as pickle
import random as r
from collections import defaultdict
import copy
import time,datetime
import matplotlib.pyplot as plt
import operator

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
    
    def removeNotSeen(self):
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
        print "missing students/kcs/items vs total"
        print len(self.studentmis),len(self.kcmis),len(self.itemmis),self.nrs,self.nrkc,len(self.ikc)
        self.removeData()
        
        
    def forgetMapping(self):
        self.updateMapping()
        self.studentmis=[]
        self.kcmis=[]
        self.itemmis=[]
        
    def removeData(self):
        t=time.time()
        #Remove all the data corresponding to missing students and KC's
        self.studentmis=list(set(self.studentmis))
        self.kcmis=list(set(self.kcmis))
        self.itemmis=list(set(self.itemmis)) 
        for i in range(len(self.ikc)):
            kclist=[]
            for kc in self.ikc[i]:
                if kc not in self.kcmis:
                    kclist.append(kc)
            self.ikc[i]=kclist
            if len(self.ikc[i])==0:
                self.itemmis.append(i)
        remove=[]
        for i,d in enumerate(self.giveData()):
            if d[0] in self.studentmis or len(self.ikc[d[1]])==0:
                remove.append(i)
        remove.sort(reverse=True)
        for i in remove:
            self.data.pop(i)
            self.labels.pop(i)
        removeFromTestSet=[]        
        for i,d in enumerate(self.giveTestData()):
            if len(self.ikc[d[1]])==0:
                removeFromTestSet.append(i)
        removeFromTestSet.sort(reverse=True)
        for i in removeFromTestSet:
            self.testdata.pop(i)
        
        print "Time taken by removeData", str(datetime.timedelta(seconds=(time.time()-t)))
        
    def updateMapping(self):
        #This method does a remapping of the student and KC id's. No missing stuff should be added after this method is run!
        t=time.time()
        self.studentmis=list(set(self.studentmis))
        self.kcmis=list(set(self.kcmis))
        self.itemmis=list(set(self.itemmis))        
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
        for i in range(len(self.ikc)):
#            if i in self.itemmis:
#                continue
            kclist=[]
            for kc in self.ikc[i]:
                if kc not in self.kcmis:
                    kclist.append(kcmap[kc])
            self.ikc[i]=kclist
        for i in range(len(self.data)):
            d=self.data[i]
            self.data[i]=(smap[d[0]],d[1])  
        for i in range(len(self.testdata)):
            d=self.testdata[i]
            self.testdata[i]=(smap[d[0]],d[1],d[2])
        print "Time taken by updateData", str(datetime.timedelta(seconds=(time.time()-t)))

    
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
        s=[0]*self.nrs
        for d in self.data:
            s[d[0]]+=1
        return s
    
    def countKCQuestions(self):
        s=[0]*self.nrkc
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
        for i,n in enumerate(sq):
            if n<nr:
                self.studentmis.append(i)
        self.removeData()
        
    def removekcq(self,nr):
        kcq=self.countKCQuestions()
        for i,n in enumerate(kcq):
            if n<nr:
                self.kcmis.append(i)
        self.removeData()                

    def removekcsq(self,nrk,nrs):
        #remove students and kc's for which there aren't at least nrk and nrs questions respectively
        oldlen=0
        while (oldlen!=len(self.data)):
            oldlen=len(self.data)
            self.removesq(nrs)
            self.removekcq(nrk)
# If to be used again, first needs to be adapted to current way of working!
#    def splitDataS(self,parts):
#        #split data of students, such that the first answers of each student are in the first part etc.
#        sets=[]
#        for i in range(parts):
#            sets.append(edata())
#            sets[i].initializeCopy(self)
#        sq=self.countStudentQuestions()
#        print "checking:",sum(sq.values()),len(self.data)
#        skip=0
#        dCounter=0
#        for i in range(max(sq.keys())+1):
#            #every part gets an equal part from every student and a rest is left
#            perS=sq[i]/parts
#            rest=sq[i]%parts
#            for j in range(parts):
#                if ((j+skip)%parts)<rest: extra=1
#                else: extra = 0
#                for k in range(perS+extra):
#                    sets[j].data.append(self.data[dCounter])
#                    sets[j].labels.append(self.labels[dCounter])
#                    
#                    
#                    if self.data[dCounter][0] != i:
#                        print i,self.data[dCounter][0]
#                        print "Student being processed and in data don't match!"
#                    dCounter+=1
#            skip=(skip+rest)%parts
#        for i in range(parts):
#            kc=sets[i].countKCQuestions()
#            print max(kc), len(kc),self.nrkc, len(self.data)            
#        return sets
            
            
    def splitDataStudent(self,parts):
        #splits the data in 'parts' # parts, where the records of any user
        #are all in the same part.
        sets=[]
        for i in range(parts):
            sets.append(edata())
            sets[i].initializeCopy(self)
        smap=range(self.nrs-len(self.studentmis))
        r.shuffle(smap)
        for i in range(len(smap)):
            smap[i]=smap[i]%parts
        for dat in self.giveData():
            sets[smap[dat[0]]].addPoint(dat[0],dat[1],dat[2])
        for dat in self.giveTestData():
            sets[smap[dat[0]]].testdata.append(dat)
        return sets

    def studentCheck(self,minq):
        #Removes those students for which there are only correct or incorrect answers to questions. Students removed are not remembered if forget is true!
        correct=[0]*self.nrs
        incorrect=[0]*self.nrs
        for d in self.giveData():
            if d[2]:
                correct[d[0]]+=1
            else:
                incorrect[d[0]]+=1
        for i in range(self.nrs):
            if correct[i]<minq or incorrect[i]<minq:
                self.studentmis.append(i)
                #print "student dropped due to no solution", i
        self.removeData()

        
                
    def KCCheck(self,minq):
        kcc=[0]*self.nrkc
        kcf=[0]*self.nrkc
        for d in self.giveData():
            for kc in self.ikc[d[1]]:
                if d[2]:
                    kcc[kc]+=1
                else:
                    kcf[kc]+=1
        for i in range(self.nrkc):
            if (kcc[i]<minq or kcf[i]<minq) and not i in self.kcmis:
                self.kcmis.append(i)
                print "KC dropped", i
        self.removeData()

    def beforeSplitCleaning(self):
        self.studentCheck(1)
        self.forgetMapping()
        
    def splitCleaning(self):
        t=time.time()
        oldlen=0
        while (not oldlen==len(self.data)):
            self.KCCheck(2)
            self.studentCheck(1)
            oldlen=len(self.data)
        olds=self.nrs
        oldkc=self.nrkc
        self.updateMapping()
        print "Time taken by splitcleaning", str(datetime.timedelta(seconds=(time.time()-t)))
        print "Removed %i students and %i kcs"%(olds-self.nrs, oldkc-self.nrkc)
    
    def createTestSet(self,testnr):
        qs=self.countStudentQuestions()
        cqs=[0]*self.nrs
        newdata=[]
        newlabels=[]
        test=[]
        for d in self.giveData():
            if cqs[d[0]]<(qs[d[0]]-testnr):
                newdata.append((d[0],d[1]))
                newlabels.append(d[2])
                cqs[d[0]]+=1
            else:
                test.append(d)
        self.data=newdata
        self.labels=newlabels
        self.testdata=test
    
    def info(self):
        self.splitCleaning()
        print "Display info on edata"
        print "There are %i records in dataset and %i in testset"%(len(self.data),len(self.testdata))
        print "Students(missing): %i(%i)"%(self.nrs,len(self.studentmis))
        print "KCs(missing): %i(%i)"%(self.nrkc,len(self.kcmis))
        print "items:", len(self.ikc)
        kcseen=self.countKCQuestions()
        kccount=defaultdict(int)
        cumkc=[0]
        for i in kcseen:
            kccount[i]+=1
        kccountsorted=sorted(kccount.items(),key=operator.itemgetter(0))
        kccount=[0]
        for i in kccountsorted:
            kccount.append(i[0])
            cumkc.append(cumkc[-1]+i[1])
        plt.figure()
        plt.xlabel("Questions per KC")
        plt.ylabel("KCs with less or equal to questions per KC")
        plt.plot(kccount,cumkc)
        plt.savefig("qkc")
        sseen=self.countStudentQuestions()
        scount=defaultdict(int)
        for i in sseen:
            scount[i]+=1
        scountsorted=sorted(scount.items(),key=operator.itemgetter(0))
        scount=[0]
        cums=[0]
        for i in scountsorted:
            scount.append(i[0])
            cums.append(cums[-1]+i[1])
        plt.figure()
        plt.xlabel("Questions per student")
        plt.ylabel("students with less or equal to questions per student")
        plt.plot(scount,cums)
        plt.savefig("qs")
        kcpq=defaultdict(int)
        for d in self.giveData():
            kcpq[len(self.ikc[d[1]])]+=1
        
        for i,k in kcpq.iteritems():
            print "%i,(%.3f)"%(k,k*1.0/sum(kcpq.values()))
        print "% correct:",sum(self.labels)*1.0/len(self)
        cortest=0
        for d in self.giveTestData():
            if d[2]:
                cortest+=1
        print "%testsetcorrect:",cortest*1.0/len(self.testdata)
#        plt.figure()
#        plt.xlabel("KCs per question")
#        plt.ylabel("Number question")
#        plt.plot(kcpq.keys(),kcpq.values(),"-")
#        kcpi=defaultdict(int)
#        for i in self.ikc:
#            kcpi[len(i)]+=len(self)/len(self.ikc)
#        plt.plot(kcpi.keys(),kcpi.values(),"r-")    
#        plt.savefig("kcp")
        