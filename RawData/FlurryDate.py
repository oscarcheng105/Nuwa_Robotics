import requests,json,time,gzip,datetime,sys,bos_sample_conf 
from threading import Thread
from baidubce.services.bos.bos_client import BosClient

sTime = time.time()-97200
eTime = time.time()-10800

'''–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––'''

class flurry:
    def __init__(self, key, sDate=None, eDate=None):
        self.request_success = False
        self.start = int(sDate)
        self.end = int(eDate)
        self.key = key           
        self.bos_client = BosClient(bos_sample_conf.config)
        self.sDisplay = datetime.datetime.fromtimestamp(int(sDate)).strftime('%Y-%m-%d %H:%M:%S')
        self.token = '' #FlurryKey
        self.request_h = {'accept':'application/vnd.api+json',
             'authorization': 'Bearer '+self.token,
             'cashe-control':'no-cashe',
             'content-type':'application/vnd.api+json'
                          }
        self.request_d = {"data":{
                    "type":"rawData",
                    "attributes":{
                                'startTime':self.start*1000,
                                'endTime':self.end*1000,
                                'outputFormat':'JSON',
                                'apiKey':apiKey[self.key]
                                }
                    }
               }
        self.download_id = self.request_id()
        self.download_url = self.request_download()
        self.data = self.retrieve()
        self.upload()
        exit
        
    def request_id(self):
        print(self.key+'_'+str(self.start)+'_'+str(self.end)+' Downloading')
        payload = json.dumps(self.request_d)
        download = requests.post('https://rawdata.flurry.com/pulse/v1/rawData', headers=self.request_h, data=payload)
        download_id = download.json()['data']['id']
        return download_id


    def request_download(self):
        url = 'https://rawdata.flurry.com/pulse/v1/rawData/'+self.download_id+'?fields[rawData]=requestStatus,s3URI'
        get_download = requests.get(url, headers=self.request_h)
        while(self.request_success==False):
            if(get_download.json()['data']['attributes']['requestStatus'] == 'Success'):
                self.request_success = True
                break
            get_download = requests.get(url, headers=self.request_h)
            time.sleep(60)
        download_url = get_download.json()['data']['attributes']['s3URI']
        return download_url

    def retrieve(self):
        r = requests.get(self.download_url).content
        dec = gzip.decompress(r)
        d = dec.decode('utf-8')
        return d

    def upload(self):
        print(self.key+'_'+str(self.start)+'_'+str(self.end)+' Uploading to BaiduCloud')
        file = str(self.key+'_'+str(self.start)+'_'+str(self.end)+'#'+str(time.time())+'.json')
        self.bos_client.put_object_from_string('nuwarobotics-flurry-log', file, self.data)
        print(self.key+'_'+str(self.start)+'_'+str(self.end)+' Upload Complete')

'''–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––'''

def checkEndTime(endD):
    while(True):
        try:
            if(endD == 'default'):
                return eTime
                break
            endD = time.mktime(time.strptime(str(endD), '%Y-%m-%d %H:%M:%S'))
            if(endD<=eTime):
                return endD
                break
        except Exception:
            endD = input("ENDTIME INPUT INVALID\nEndTime cannot be later than DefaultTime (3h before current time)\nPlease reinput in the correct format (yyyy-mm-dd hh:mm:ss): ")

def checkStartTime(startD,endD=None):
    while(True):
        try:
            if(startD == 'default'):
                return sTime
                break
            startD = time.mktime(time.strptime(str(startD), '%Y-%m-%d %H:%M:%S'))
            if(startD < endD):
                return startD
                break
        except Exception:
            startD = input("STARTTIME INPUT INVALID\nStartTime cannot be later than EndTime\nPlease reinput (yyyy-mm-dd hh:mm:ss): ")

def checkApp(app):
    while(True):
        for x in apiKey:
            if(x == app):
                return app
        app = input('Please input a valid app name: ')
                
def checkInitiation():
    if(len(sys.argv)==1): #FlurryDownload.py
        for x in apiKey:
            Thread(target=flurry,args=[x,sTime,eTime]).start()
            time.sleep(0.3)
    elif(len(sys.argv)==3): #FlurryDownload.py, startD, startT
        start = checkStartTime(str(sys.argv[1]+' '+sys.argv[2]), eTime)
        for x in apiKey:
            Thread(target=flurry,args=[x,start,eTime]).start()
            time.sleep(0.3)
    elif(len(sys.argv)==5): #FlurryDownload.py, startD, startT, endD, endT
        end = checkEndTime(str(sys.argv[3]+' '+sys.argv[4]))
        start = checkStartTime(str(sys.argv[1]+' '+sys.argv[2]), end)
        for x in apiKey:
            Thread(target=flurry,args=[x,start,end]).start()
            time.sleep(0.3)
    elif(len(sys.argv)==2): #FlurryDownload.py, APP
        appName = checkApp(sys.argv[1])
        f = flurry(appName,sTime,eTime)
    elif(len(sys.argv)==4): #FlurryDownload.py, APP, startD, startT
        appName = checkApp(sys.argv[1])
        start = checkStartTime(str(sys.argv[2]+' '+sys.argv[3]),eTime)
        f = flurry(appName,start,eTime)
    elif(len(sys.argv)==6): #FlurryDownload.py, APP, startD, startT, endD, endT
        appName = checkApp(sys.argv[1])
        end = checkEndTime(str(sys.argv[4]+' '+sys.argv[5]))
        start = checkStartTime(str(sys.argv[2]+' '+sys.argv[3]), end)
        f = flurry(appName, start, end)

'''–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––'''

checkInitiation()
