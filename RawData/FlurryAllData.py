import requests,json,time,gzip,threading,datetime
from threading import Thread

apiKey = {'9FMY8P5P9SD6Y3W8DF7K':'daniel-test','NDXMRQX45SYQ3C3BKMCG':'FaceRecognition2',
        'RQFQN9SV4F5GW87SJKDT':'IotService','HXQPGR8J5W62D36DRKZ8':'MiboGarden',
        'ZXTWY93GMZSJSWN7G3NN':'NuWa Space', 'GKFD7GC9R7VTSYXCM52N':'NuwaCamera2',
        '2NZHF4CMWFYKYRP9QTSH':'Nuwa Player','RGDZ6TBJQ8PDYNBN7CGM':'Robot/CameraService/Production',
        'SD3SF227RMJXNG25TYTX':'Robot/FaceHome2','HNWQ6Y9FJ3YHHX7G3JHK':'Robot/HomeService',
        'GCZJDFBG93BVQJZ5C3Z3':'Robot/LiveABC/Production','WV7PHG9V7CGKRDPFFGJC':'Robot/MicroCoding',
        'MV994RHNN4RJV5J79ZKQ':'Robot/NuWaStore','8HVPWV2F4ZV7J2RZGPQ5':'Robot/NuWaStoreMenu',
        '4CF4F83NGF6CXMQ75K8V':'Robot/Quiz','QVV39RN73XM28CTHR54J':'Robot/RubyEnglish',
        'DFMNXC3NHN6VCD65HW2T':'Robot/Tutorial','42HM5TMQ32C9V4ZHRWCM':'Robot/VideoCall',
        '6XWDZY4D3RHG98KYJ69W':'RobotOOBE','XS9TZQ2G2WHJJ46Q3WNF':'RobotTheater'}

class flurry:
    def __init__(self,key,akey):
        self.request_success = False
        self.sDate = time.time()*1000-97200000
        self.eDate = time.time()*1000-10800000
        self.date = datetime.datetime.fromtimestamp(self.sDate/1000).strftime('%Y-%m-%d %H:%M:%S')
        print(key+' '+self.date)
        self.token = '' #FlurryKey
        self.request_h = {'accept':'application/vnd.api+json',
             'authorization': 'Bearer '+self.token,
             'cashe-control':'no-cashe',
             'content-type':'application/vnd.api+json'}
        self.request_d = {"data":{
                    "type":"rawData",
                    "attributes":{
                                'startTime':self.sDate,
                                'endTime':self.eDate,
                                'outputFormat':'JSON',
                                'apiKey':key
                                }
                    }
               }
        self.download_id = self.request_id(key,akey)
        self.download_url = self.request_download()
        self.retrieve(key,akey)
        exit
                
    def request_id(self,key,akey):
        print(akey[key]+' '+self.date+' Downloading')
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

    def retrieve(self,key,akey):
        r = requests.get(self.download_url).content
        dec = gzip.decompress(r)
        d = dec.decode('utf-8')
        file = '/Users/oscarcheng/Downloads/'+str(self.download_id)+'.json'
        with open(file, 'w') as fout:
            fout.write(d)
            fout.close()
        print(akey[key]+' '+self.date+' Download Complete')

def repeat():
    threading.Timer(86400, repeat).start()
    for x in range(len(apiKey)):
        Thread(target=flurry,args=[list(apiKey)[x],apiKey]).start()
        time.sleep(0.3)
    print()
repeat()
