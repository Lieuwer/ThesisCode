import random as r
import math as m
import matplotlib.pyplot as plt
import numpy as np

class modelFitter:


    def __init__(self,nrs,nrkc,ikc,data):
        #store the kc's belonging to each item
        self.ikc=[]
        #lists that will hold the parameters of items and students
        self.ca=[]
        self.cg=[]
        self.cr=[]
        self.cb=[]
        self.st=[]
        self.se=[]
        #linkage of kcs to items is known
        self.ikc=ikc
        self.data=data
        #create student parameter estimates, now done in same fashion as generating data
        for i in range(nrs):
            self.st.append(r.normalvariate(0,1))
            self.se.append(r.uniform(.04,.2))

        #create knowledge component parameter estimates, idem as above
        for i in range(nrkc):
            self.ca.append(r.uniform(.5,2))
            g=r.uniform(.5,2)
            self.cg.append(g)
            self.cr.append(g*r.uniform(.2,.8))
            self.cb.append(r.normalvariate(0,1))

    def iterate(self,maxiterations=250):
        delist=[]
        dtlist=[]
        erlist=[]

        dalist=[]
        dglist=[]
        drlist=[]
        dblist=[]


        # this method performs iterative alternating logarithmic optamilatization of the logit of p for all datapoints
        for i in range(1):

            #first estimate the user parameters
            for j in range(maxiterations):
                totalerror=0.0
                #keep track of the derivative in parameters
                dst=[0]*len(self.st)
                dse=[0]*len(self.st)
                #keep track of questions answered correctly and questions answered wrongly
                kcc = [0]*len(self.ca)
                kcf = [0]*len(self.ca)
                for d in self.data:
                    s=d[0]
                    it=d[1]
                    x=0
                    k=float(len(self.ikc[it]))
                    numse=0
                    numte=0
                    for c in self.ikc[it]:
                        x+=self.ca[c]*self.st[s]/k+(kcf[c]*self.cr[c]+kcc[c]*self.cg[c])*self.se[s]-self.cb[c]
                        numte+=self.ca[c]/k
                        numse+=(kcc[c]*self.cg[c]+kcf[c]*self.cr[c])
                        if d[2]:
                            kcc[c]+=1
                        else:
                            kcf[c]+=1
                    big=m.exp(x)+1
                    if d[2]:
                        totalerror+=1/big
                        dst[s]+=numte/big
                        dse[s]+=numse/big
                    else:
                        totalerror+=1-(1/big)
                        dst[s]-=numte*(big-1)/big
                        dse[s]-=numse*(big-1)/big
                #finally update the parameters
                totaldert=0
                totaldere=0
                #First get the size of the gradients
                totaldert=sum(np.power(dst,2))
                totaldere=sum(np.power(dse,2))
                step=((maxiterations-i)/maxiterations)**3
                #step=1
                #Better alternative below
##                for s in range(len(self.st)):
##                    self.st[s]+=dst[s]/m.sqrt(totaldert)*step*.1
##                    self.se[s]+=dse[s]/m.sqrt(totaldere)*step*.01

                self.st=np.add(self.st,np.multiply(dst,step*.1/m.sqrt(totaldert)))
                self.se=np.add(self.se,np.multiply(dse,step*.01/m.sqrt(totaldere)))
                dtlist.append(sum(np.abs(dst)))
                delist.append(sum(np.abs(dse)))
                erlist.append(totalerror/len(self.data))


##            for j in range(maxiterations):
##                totalerror=0.0
##                #keep track of the derivative in parameters
##                dca=[0]*len(self.st)
##                dcg=[0]*len(self.st)
##                dcr=[0]*len(self.st)
##                dcb=[0]*len(self.st)
##                #keep track of questions answered correctly and questions answered wrongly
##                kcc = [0]*len(self.ca)
##                kcf = [0]*len(self.ca)
##                for d in self.data:
##                    s=d[0]
##                    it=d[1]
##                    x=0
##                    k=float(len(self.ikc[it]))
##                    for c in self.ikc[it]:
##                        x+=self.ca[c]*self.st[s]/k+(kcf[c]*self.cr[c]+kcc[c]*self.cg[c])*self.se[s]-self.cb[c]
##                    big=m.exp(x)+1
##                    for c in self.ikc[it]:
##                        if d[2]:
##                            totalerror+=(1/(big))/k
##                            dca[c]+=(self.st[s]/k)/big
##                            dcg[c]+=self.se[s]*kcc[c]/big
##                            dcr[c]+=self.se[s]*kcf[c]/big
##                            dcb[c]-=1/big
##                            kcc[c]+=1
##                        else:
##                            totalerror+=(1-(1/big))/k
##                            dca[c]-=(self.st[s]/k)*(big-1)/big
##                            dcg[c]-=self.se[s]*kcc[c]*(big-1)/big
##                            dcr[c]-=self.se[s]*kcf[c]*(big-1)/big
##                            dcb[c]+=(big-1)/big
##                            kcf[c]+=1
##                #finally update the parameters
##                totaldca=0
##                totaldcg=0
##                totaldcr=0
##                totaldcb=0
##                #First get the size of the gradients
##                for c in range(len(self.ca)):
##                    totaldca+=dca[c]**2
##                    totaldcg+=dcg[c]**2
##                    totaldcr+=dcr[c]**2
##                    totaldcb+=dcb[c]**2
##                step=((maxiterations-i)/maxiterations)**2
##                #step=1
##                for c in range(len(self.ca)):
##                    self.ca[c]+=dca[c]/m.sqrt(totaldca)*step*.02
##                    self.cg[c]+=dcg[c]/m.sqrt(totaldcg)*step*.01
##                    self.cr[c]+=dcr[c]/m.sqrt(totaldcr)*step*.01
##                    self.cb[c]+=dcb[c]/m.sqrt(totaldcb)*step*.01
##                #print totaldca,totaldcg,totaldcr, totaldcb
##                dalist.append(m.sqrt(totaldca))
##                dglist.append(m.sqrt(totaldcg))
##                drlist.append(m.sqrt(totaldcr))
##                dblist.append(m.sqrt(totaldcb))
##                erlist.append(totalerror/len(self.data))

        plt.figure(1)
        plt.subplot(311)
        plt.plot(dtlist)
        plt.ylabel('dt')
        plt.subplot(312)
        plt.plot(delist)
        plt.ylabel('de')
        plt.subplot(313)
        plt.plot(erlist)
        plt.ylabel('error')
        plt.show()

##        plt.figure(2)
##        plt.subplot(231)
##        plt.plot(dalist)
##        plt.ylabel('da')
##        plt.subplot(232)
##        plt.plot(dglist)
##        plt.ylabel('dg')
##        plt.subplot(233)
##        plt.plot(drlist)
##        plt.ylabel('dr')
##        plt.subplot(234)
##        plt.plot(dalist)
##        plt.ylabel('db')
##        plt.subplot(235)
##        plt.plot(erlist)
##        plt.ylabel('error')
##        plt.show()
##        print "a,b,g,r,e and t stats", np.average(self.ca), np.std(self.ca), np.average(self.cb), np.std(self.cb), np.average(self.cg), np.std(self.cg), np.average(self.cr), np.std(self.cr), np.average(self.se), np.std(self.se), np.average(self.st), np.std(self.st)
##        print "max values", max(self.ca), max(self.cb), max(self.cg), max(self.cr), max(self.se),max(self.st)
##        plt.plot(erlist)
        #plt.show()





    def normalizegre(self):
        i=1
#old mistaken stuff
#dst[s]+=self.ca[c]/(-self.cb[c]*len(self.ikc[it])
                        #                               +(kcf[c]*self.cr[c]+kcc[c]*self.cg[c])*self.se[s]*len(self.ikc[it])
                        #                               + self.st[s]*self.ca[c])
                        #dse[s]+=(kcf[c]*self.cr[c]+kcc[c]*self.cg[c])*len(self.ikc[it])/(-self.cb[c]*len(self.ikc[it])
                        #                               +(kcf[c]*self.cr[c]+kcc[c]*self.cg[c])*self.se[s]*len(self.ikc[it])
                        #                              + self.st[s]*self.ca[c])