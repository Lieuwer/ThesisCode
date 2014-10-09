'''
Do some questions have different (number) of kcs associated with them at different times?
Because the distribution of number of kcs per question includes up to 7 when 
running on all steps, but only up to 5 when only looking at the first time a 
question appears.
'''
import sys
sys.path.append('..\models')
from edata import edata
from collections import defaultdict




def main():
    trainfile="D:\\scriptie\\Thesisdata\\bridge_to_algebra_2006_2007\\bridge_to_algebra_2006_2007_train.txt"
    testfile="D:\\scriptie\\Thesisdata\\bridge_to_algebra_2006_2007\\bridge_to_algebra_2006_2007_master.txt"
    f = open(trainfile, 'r')
    #Steps will count for each item, how often it occurs
    steps={}
    #kcs counts for every kc how often it occurs
    kcs=defaultdict(int)
    #kcq counts how many questions are associated with a certain number of kcs (the key)
    kcq=defaultdict(int)
    #First line has the headers
    line=f.readline()
    #ikc links question # to KC #
    ikc=[]
    icounter=0
    #kcsmap maps a written kc to a unique number
    kcsmap={}
    #items maps a problem name plus step name to a unique item number
    items={}
    #sid maps a student to a int id
    sid={}
    data=[]
    labels=[]
    testdata=[]
    for line in f:
        parts=line.split('\t')
        addkc=False
        if len(parts[17])<3: continue
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
            kclist=[]
            for kcp in parts[17].split('~~'):
                
                if kcp.find(";")>=0:
                    kc = kcp[12:kcp.index(";")]
                else:
                    kc=kcp
                if kc=="":
                    continue
                kccount+=1
                if not kcsmap.has_key(kc):
                    kcsmap[kc]=len(kcs)
                kclist.append(kcsmap[kc])
                kcs[kc]+=1
#            if len(kclist)==0:
#                print "wtf", line
#                exit()
            ikc.append(kclist)
            kcq[kccount]+=1
        else:
            for kcp in parts[17].split('~~'):
                if kcp.find(";")>=0:
                    kc = kcp[12:kcp.index(";")]
                else:
                    kc=kcp
                if kc=="":
                    continue
                if not kcsmap.has_key(kc):
                    kcsmap[kc]=len(kcs)
                if not kcsmap[kc] in ikc[items[parts[3]][parts[5]]]:
                    #print "Kc NF!", kc
                    #print rawkcitem[items[parts[3]][parts[5]]]
                    ikc[items[parts[3]][parts[5]]].append(kcsmap[kc])                    
                    kcs[kc]+=1
        data.append((sid[parts[1]],items[parts[3]][parts[5]]))
        labels.append(int(parts[13]))
    print "number of items: ", icounter
    print "number of records: ", len(data)
    print "number of kcs: ", len(kcs)
    print "number of students: ", len(sid)
    print "#kcs #items"
    for k,v in kcq.iteritems():
        print k,v
    
    kcq=defaultdict(int)
    for l in ikc:
        kcq[len(l)]+=1
    print "#kcs #items after taking things into account"
    print "number of items", len(ikc)
    for k,v in kcq.iteritems():
        print k,v
#    for kc in kcs.keys():
#        print kc
    
    datafile=edata()
    datafile.initialize(ikc, len(sid),len(kcsmap),data,labels)
    datafile.save("train.edata")
    
    f = open(testfile, 'r')
    # get rid of headers
    f.readline()
    #clear all data
    testdata=[]
    
    skipcount=0
    for line in f:
        parts=line.split('\t')
        if not sid.has_key(parts[1]):
            print "Warning: student not seen", parts[1]
            skipcount+=1
            continue
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
            kclist=[]
            for kcp in parts[17].split('~~'):
                
                if kcp.find(";")>=0:
                    kc = kcp[12:kcp.index(";")]
                else:
                    kc=kcp
                if kc=="":
                    continue
                kccount+=1
                if not kcsmap.has_key(kc):
                    kcsmap[kc]=len(kcs)
                kclist.append(kcsmap[kc])
                kcs[kc]+=1
            ikc.append(kclist)
            kcq[kccount]+=1
        testdata.append((sid[parts[1]],items[parts[3]][parts[5]],int(parts[13])))
    print "Number of records: ", len(testdata) ," records skipped: " ,skipcount
    dataset=edata()    
    dataset.initialize(ikc, len(sid),len(kcsmap),data,labels,testdata)
    dataset.save("bridge.edata")

            
if __name__ == '__main__':
    main()
