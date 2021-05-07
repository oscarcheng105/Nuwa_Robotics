import requests,sys,bos_sample_conf
from baidubce.services.bos.bos_client import BosClient
from ProcessedParameters import table as tb

class Flurry:
    def __init__(self):
        self.url = 'https://api-metrics.flurry.com/public/v1/data'
        self.token='' #FlurryKey
        self.bos_client = BosClient(bos_sample_conf.config)
        self.setParams()
        self.data = self.requestData()
        self.uploadBaidu()

    def setParams(self):
        self.table = self.setTable()
        self.time = self.setTimeGrain()
        self.setDimensions()
        self.setMetrics()
        self.setDateRange()
        self.setSort()
        self.setFilter()
        self.setHavings()
        self.url+=self.token
        #print(self.url)

    def requestData(self):
        d = requests.get(self.url).text
        #for x in d['rows']:
            #print(x)
        return d

    def uploadBaidu(self):
        file = 'processedSample'+'.json'
        self.bos_client.put_object_from_string('nuwarobotics-flurry-log', file, self.data)
        print('processedSample'+' Upload Complete')
        
    def setTable(self):
        for i in range(1,len(info)):
            for x in tb:
                if(x == info[i]):
                    self.url += '/'+info[i]
                    return info[i]
                
    def setTimeGrain(self):
        for i in range(1,len(info)):
            for x in tb[self.table]['timeGrain']:
                if(x == info[i]):
                    self.url += '/'+info[i]
                    return info[i]
            
    def setDimensions(self):
        for i in range(1,len(info)):
            if(info[i].find('|')>-1):
                self.setFields(i)
            else:
                for x in tb[self.table]['dimension']:
                    if(x == info[i]):
                        self.url += '/'+info[i]

    def setFields(self,index):
        main = info[index][0:info[index].find('|')]
        sub = info[index][info[index].find('|')+1:len(info[index])]
        for i in range(1,index):
            if(info[i] == main):
                for x in tb[self.table]['dimension'][main]:
                    if(x == info[index]):
                        if(self.url.find(main+';show=')==-1):
                            self.url += ';show='+sub
                        else:
                            self.url += ','+sub

    def setMetrics(self):
        for x in tb[self.table]['metrics']:
            for i in range(1,len(info)):
                if(x == info[i]):
                    if (self.url.find('?metrics=')==-1):
                        self.url+='?metrics='+info[i]
                    else:
                        self.url += ','+info[i]

    def setDateRange(self):
        for x in info:
            if (len(x)>=20):
                if(x[4]=='-' and x[7]=='-' and x[10]=='/' and
                   x[15]=='-' and x[18]=='-'):
                    self.url += '&dateTime='+x
                    break
    
    def setSort(self):
        self.setTopN()
        for x in range(len(info)):
            if(info[x].find('sort=')>-1):
                field = info[x][info[x].find('=')+1:info[x].find('|')]
                main = info[x][info[x].find('=')+1:len(info[x])]
                for i in range(x):
                    if (info[i]==field):                      
                        if(self.url.find('&sort=')==-1):
                            self.url+='&sort='+main
                        else:
                            self.url+=','+main

    def setTopN(self):
        for x in info:
            if(x.find('topN=')>-1):
                self.url += '&'+x

    def setFilter(self):
        for x in range(len(info)):
            if(info[x].find('filters=')>-1):
                field = info[x][info[x].find('=')+1:info[x].find('-')]
                main = info[x][info[x].find('=')+1:len(info[x])]
                for i in range(x):
                    if (info[i]==field):                      
                        if(self.url.find('&filters=')==-1):
                            self.url+='&filters='+main
                        else:
                            self.url+=','+main

    def setHavings(self):
        for x in range(len(info)):
            if(info[x].find('having=')>-1):
                field = info[x][info[x].find('=')+1:info[x].find('-')]
                main = info[x][info[x].find('=')+1:len(info[x])]
                for i in range(x):
                    if (info[i]==field):                      
                        if(self.url.find('&having=')==-1):
                            self.url+='&having='+main
                        else:
                            self.url+=','+main
                                
info = sys.argv
f = Flurry()
