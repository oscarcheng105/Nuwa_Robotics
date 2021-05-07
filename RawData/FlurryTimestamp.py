import requests,json,time,gzip,datetime,sys,bos_sample_conf 
from threading import Thread
from baidubce.services.bos.bos_client import BosClient

apiKey = {'daniel-test':'9FMY8P5P9SD6Y3W8DF7K','FaceRecognition2':'NDXMRQX45SYQ3C3BKMCG',
                    'IotService': 'RQFQN9SV4F5GW87SJKDT','MiboGarden':'HXQPGR8J5W62D36DRKZ8',
                    'NuWaSpace':'ZXTWY93GMZSJSWN7G3NN', 'NuwaCamera2':'GKFD7GC9R7VTSYXCM52N',
                    'NuwaPlayer':'2NZHF4CMWFYKYRP9QTSH','Robot/CameraService/Production':'RGDZ6TBJQ8PDYNBN7CGM',
                    'Robot/FaceHome2':'SD3SF227RMJXNG25TYTX','Robot/HomeService':'HNWQ6Y9FJ3YHHX7G3JHK',
                    'Robot/LiveABC/Production':'GCZJDFBG93BVQJZ5C3Z3','Robot/MicroCoding':'WV7PHG9V7CGKRDPFFGJC',
                    'Robot/NuWaStore':'MV994RHNN4RJV5J79ZKQ','Robot/NuWaStoreMenu':'8HVPWV2F4ZV7J2RZGPQ5',
                    'Robot/Quiz':'4CF4F83NGF6CXMQ75K8V','Robot/RubyEnglish':'QVV39RN73XM28CTHR54J',
                    'Robot/Tutorial':'DFMNXC3NHN6VCD65HW2T','Robot/VideoCall':'42HM5TMQ32C9V4ZHRWCM',
                    'RobotOOBE':'6XWDZY4D3RHG98KYJ69W','RobotTheater':'XS9TZQ2G2WHJJ46Q3WNF'
                  }

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
        if(int(endD)<=int(eTime)):
            return endD
        else:
            endD = input("ENDTIME INPUT INVALID\nEndTime cannot be later than DefaultTime (3h before current time)\nPlease reinput timestamp: ")

def checkStartTime(startD,endD):
    while(True):
        if(int(startD) < int(endD)):
            return startD
        else:
            startD = input("STARTTIME INPUT INVALID\nStartTime cannot be later than EndTime\nPlease reinput timestamp: ")

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
    elif(len(sys.argv)==2): #FlurryDownload.py, start
        try:
            s = int(sys.argv[1])
            start = checkStartTime(sys.argv[1], eTime)
            for x in apiKey:
                Thread(target=flurry,args=[x,start,eTime]).start()
                time.sleep(0.3)
        except ValueError: #FlurryDownload.py, APP
            appName = checkApp(sys.argv[1])
            f = flurry(appName,sTime,eTime)
    elif(len(sys.argv)==3): #FlurryDownload.py, start, end
        try:
            s = int(sys.argv[1])
            end = checkEndTime(sys.argv[2])
            start = checkStartTime(sys.argv[1], end)
            for x in apiKey:
                Thread(target=flurry,args=[x,start,end]).start()
                time.sleep(0.3)
        except ValueError: #FlurryDownload.py, APP, start
            appName = checkApp(sys.argv[1])
            start = checkStartTime(sys.argv[2],eTime)
            f = flurry(appName,start,eTime)
    elif(len(sys.argv)==4): #FlurryDownload.py, APP, start, end
        appName = checkApp(sys.argv[1])
        end = checkEndTime(sys.argv[3])
        start = checkStartTime(sys.argv[2], end)
        f = flurry(appName, start, end)

'''–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––'''

checkInitiation()


