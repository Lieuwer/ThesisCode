'''
Do some questions have different (number) of kcs associated with them at different times?
Because the distribution of number of kcs per question includes up to 7 when 
running on all steps, but only up to 5 when only looking at the first time a 
question appears.
'''
from edata import edata
from collections import defaultdict
#data=[]
ikc=defaultdict(list)


def main():
    trainfile="D:\\scriptie\\Thesisdata\\algebra_2005_2006\\algebra_2005_2006_train.csv"
    testfile="D:\\scriptie\\Thesisdata\\algebra_2005_2006\\algebra_2005_2006_master.csv"
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
    icounter=0
    #kcsmap maps a written kc to a unique number
    kcsmap={}
    #items maps a problem name plus step name to a unique item number
    items={}
    #sid maps a student to a int id
    sid={}
    data=[]
    labels=[]
    rawkcitem={}
    total=0
    error=0
    for line in f:
        total+=1
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
            rawkcitem[items[parts[3]][parts[5]]]=(parts[17],parts[0])
            for kcp in parts[17].split('~~'):
                kccount+=1
                if kcp.find(";")>=0:
                    kc = kcp[12:kcp.index(";")]
                else:
                    kc=kcp
                if kc=="":
                    continue
                if not kcsmap.has_key(kc):
                    kcsmap[kc]=len(kcs)
                ikc[items[parts[3]][parts[5]]].append(kcsmap[kc])
                kcs[kc]+=1
            kcq[kccount]+=1
        else:
            for kcp in parts[17].split('~~'):
                kccount+=1
                if kcp.find(";")>=0:
                    kc = kcp[12:kcp.index(";")]
                else:
                    kc=kcp
                if kc=="":
                    continue
                if not kcsmap.has_key(kc):
                    kcsmap[kc]=len(kcs)
                    #print "warning kc that should be found is not found!", kc
                if not kcsmap[kc] in ikc[items[parts[3]][parts[5]]]:
                    #print "Kc NF!", kc
                    #print rawkcitem[items[parts[3]][parts[5]]]
                    error+=1
                    ikc[items[parts[3]][parts[5]]].append(kcsmap[kc])
                    
                    kcs[kc]+=1
                #
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
    print len(ikc.keys())
#    for kc in kcs.keys():
#        print kc

    
    
    f = open(testfile, 'r')
    # get rid of headers
    f.readline()
    #clear all data
    data=[]
    labels=[]
    skipcount=0
    for line in f:
        parts=line.split('\t')
        if not sid.has_key(parts[1]):
            print "Warning: student not seen"
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
        data.append((sid[parts[1]],items[parts[3]][parts[5]]))
        labels.append(int(parts[13]))
    print "Number of records: ", len(data) ," records skipped: " ,skipcount

    print float(error)/total
        
            
if __name__ == '__main__':
    main()
