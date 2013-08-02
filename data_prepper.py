#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      6193870
#
# Created:     20-06-2013
# Copyright:   (c) 6193870 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
'''
Do some questions have different (number) of kcs associated with them at different times?
Because the distribution of number of kcs per question includes up to 7 when 
running on all steps, but only up to 5 when only looking at the first time a 
question appears.
'''
import cPickle as pickle

from collections import defaultdict
data=[]
ikc=defaultdict(list)


def main():
    trainfile="D:\\scriptie\\Thesisdata\\algebra_2005_2006\\algebra_2005_2006_train.csv"
    testfile="D:\Thesisdata\KDD\algebra_2005_2006"
    f = open(trainfile, 'r')
    #Stop is used to stop early in testing
    stop=0
    #Steps will count for each item, how often it occurs
    steps={}
    #kcs counts for every kc how often it occurs
    kcs=defaultdict(int)
    #kcq counts how many questions are associated with a certain number of kcs (the key)
    kcq=defaultdict(int)
    #First line has the headers
    line=f.readline()
    '''for j in range(2):
        line=f.readline()
        parts=line.split('\t')
        for word in parts:
            print word
    '''
    #ikc links question # to KC #
    icounter=0
    #kcsmap maps a written kc to a unique number
    kcsmap={}
    #items maps a problem name plus step name to a unique item number
    items={}
    #sid maps a student to a int id
    sid={}
    
    for line in f:
        stop+=1
#        if stop>5:
#            break
        parts=line.split('\t')
        addkc=False
        if not sid.has_key(parts[1]):
            sid[parts[1]]=len(sid)
        if steps.has_key(parts[3]):
            if steps[parts[3]].has_key(parts[5]):
                steps[parts[3]][parts[5]]+=1
            else:
                addkc=True
                steps[parts[3]][parts[5]]=1
                items[parts[3]][parts[5]]=icounter
                icounter+=1
        else:
            addkc=True
            steps[parts[3]]={}
            items[parts[3]]={}
            steps[parts[3]][parts[5]]=1
            items[parts[3]][parts[5]]=icounter
            icounter+=1
        
        kccount=0
        if addkc:
            for kcp in parts[17].split('~~'):
                kccount+=1
                if kcp.find(";")>=0:
                    kc = kcp[12:kcp.index(";")]
                else:
                    kc=kcp
                if not kcsmap.has_key(kc):
                    kcsmap[kc]=len(kcs)
                ikc[items[parts[3]][parts[5]]].append(kcsmap[kc])
                kcs[kc]+=1
            kcq[kccount]+=1
        data.append((sid[parts[1]],items[parts[3]][parts[5]],int(parts[13])))
    print "number of items: ", icounter
    print "number of records: ", stop
    print "number of kcs: ", len(kcs)
    print "number of students: ", len(sid)
    print "#kcs #items"
    for k,v in kcq.iteritems():
        print k,v
    print len(ikc.keys())
#    for kc in kcs.keys():
#        print kc
    filehandle= open ("datatest.rdata","wb")
    pickle.dump(data,filehandle)
    filehandle.close()
    filehandle= open ("ikc.ikc","wb")
    pickle.dump(ikc,filehandle)
    filehandle.close()

if __name__ == '__main__':
    main()
