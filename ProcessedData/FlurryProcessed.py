from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from baidubce.services.bos.bos_client import BosClient
import requests,sys,bos_sample_conf

class Flurry:
    def __init__(self):
        self.options = Options()
        self.options.add_argument('--headless')
        self.browser = webdriver.Chrome(chrome_options=self.options)
        self.browser.get('http://querybuilder.flurry.com/')
        self.bos_client = BosClient(bos_sample_conf.config)
        self.basicParams()
        self.url = self.getUrl()
        self.browser.quit()
        self.customParams()
        print('Initializing Download')
        self.data = requests.get(self.url).text
        print('Begin Upload')
        self.uploadBaidu()
        print('processedSample'+' Upload Complete')

    def basicParams(self):
        self.verify(info[1])
        self.verify(info[2])
        for i in range(3,len(info)):
            self.verify(info[i])

    def customParams(self):
        self.setDateRange()
        self.setSort()
        self.setFilters()
        self.setHaving()
        self.url+='' #FlurryKey
    
    def uploadBaidu(self):
        file = 'processedSample'+'.json'
        self.bos_client.put_object_from_string('nuwarobotics-flurry-log', file, self.data)
    
    def verify(self,word):
        try:
            check = self.browser.find_element_by_xpath('//button[text()="'+word+'"]')
            check.click()
        except Exception:
            pass

    def getUrl(self):
        check = self.browser.find_element_by_xpath('//input[@class="reqString"]')
        return check.get_attribute('value')

    def setDateRange(self):
        for x in info:
            if (x == 'Today' and x == 'Last 7 Days' and x == 'Last 30 Days' and x == 'Last 90 Days' and x == 'Last Year' and x == 'Custom'):
                break
            elif(len(x)>=20):
                if(x.find('/')>-1):
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

    def setFilters(self):
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

    def setHaving(self):
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
