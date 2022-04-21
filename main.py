import threading,operator,requests,win32api,platform,base64,proxy,ctypes,json,time,glob,sys,os
from cefpython3 import cefpython as cef
import tkinter as tk
from lxml import etree
'''
IMPORTANT!!!
Please install lxml version below 4.2.5 to make sure
that etree is provided correcty!!!
'''
from urllib.parse import quote
class daili:
    def send_request(self,page):
        base_url = 'https://www.kuaidaili.com/free/inha/{}/'.format(page)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}
        response = requests.get(base_url,headers=headers)
        data = response.content.decode()
        time.sleep(1)
        return data
    def parse_data(self,data):
        html_data =  etree.HTML(data)
        parse_list = html_data.xpath('//table[@class="table table-bordered table-striped"]/tbody/tr')
        return parse_list
    def check_ip(self,proxies_list):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}
        can_use = []
        for proxies in proxies_list:
            try:
                t1 = time.perf_counter()
                response = requests.get('https://music.163.com/',headers=headers,proxies={'http':proxies['HTTP']})
                t2 = time.perf_counter()
                t3=t2-t1
                if response.status_code == 200:
                    proxies['Timeout'] = t3
                    can_use.append(proxies)
            except:
                pass
        can_use = sorted(can_use, key=operator.itemgetter('Timeout'))
        return can_use
    def run(self):
        proxies_list = []
        for page in range(1,5):
            data = self.send_request(page)
            parse_list = self.parse_data(data)
            for tr in parse_list:
                proxies_dict  = {}
                http_type = tr.xpath('./td[4]/text()')
                ip_num = tr.xpath('./td[1]/text()')
                port_num = tr.xpath('./td[2]/text()')
                http_type = ' '.join(http_type)
                ip_num = ' '.join(ip_num)
                port_num = ' '.join(port_num)
                proxies_dict[http_type] = ip_num + ":" + port_num
                proxies_list.append(proxies_dict)
        print("Scraping",len(proxies_list),"Chinese http-proxies from Kuaidaili:")
        pjson = self.check_ip(proxies_list)
        print(len(pjson),"of them are actually active.") 
        return pjson
def CMCS(exit=1,proxy1="loc",pjson=None):
    if exit==1:
        print('======CMCS BY TUDOOU-ETH======')
    def res():
        exit=0
        re=str(input('是否继续搜索(Y/N)：'))
        if re =='Y' or re =='N' or re =='y' or re =='n':
            if re =='Y' or re == 'y':
                CMCS(exit=0,proxy1=proxy1,pjson=pjson)
            else:
                print('感谢您的使用！')
                time.sleep(1.5)
                exit=1
        else:
            print('错误：请输入Y(是)/N(否)')
            res()
        return exit
    user=str(win32api.GetUserName())
    for y in glob.glob(os.path.join('C:\\Users\\'+user+'\\AppData\\Local\\Temp\\','cmcs_*.htm')):
        os.remove(y)
    def rechk():
        if proxy1 == "loc":
            try:
                requests.get('https://www.baidu.com')
            except:
                print('连接异常，请检查您的网络！')
                time.sleep(3.5)
                exit()
    refr=rechk()
    if proxy1 == "loc":
        rjson=requests.get('http://ip-api.com/json')
        rjson=json.loads(rjson.text,strict=False)
        if rjson["countryCode"] != "CN":
            print("We found that you're not using Chinese ip,")
            print("please hold still...")
            dl=daili()
            pjson=dl.run()
            print('Using proxy...')
            refr=1
    if refr==1:
        proxy1=pjson[0]
        def sp1(po='8029',tho='127.0.0.1',tpo='80'):
            with proxy.Proxy(['--port',po,'--tunnel-hostname',tho,'--tunnel-port',tpo,'--log-level','c']) as p:
                proxy.sleep_loop()
        sp=threading.Thread(target=sp1,args=['8029',proxy1['HTTP'].split(":")[0],proxy1['HTTP'].split(":")[1]])
        sp.start()
    a=quote(str(input("输入您想搜索的音乐:")))
    x=input("键入输出结果的条数:")
    k=0
    try:
        x=int(x)
        if x>100 or x<1:
            print("很抱歉，搜索结果条数范围为1~100!")
            k=1
            time.sleep(4)
            exit()
    except:
        if k==0:
            print("操作失败，请输入整数！")
        exit()
    slk= 'https://music.163.com/api/search/pc?s='+ a +'&offset=0&limit='+str(x)+'&type=1'
    if proxy1 != 'loc':
        mjson = requests.get(slk, cookies={"NMTID":"00OuXADISZEZcV3wE3Bhnrj6-iWv_YAAAF_p4zVZQ"},proxies={'http':proxy1['HTTP']})
    else:
        mjson = requests.get(slk, cookies={"NMTID":"00OuXADISZEZcV3wE3Bhnrj6-iWv_YAAAF_p4zVZQ"})
    mjson=json.loads(mjson.text,strict=False)
    try:
        nml=[]
        for i in range(x):
            mas=str()
            for ats in range(len(mjson["result"]["songs"][i]["artists"])):
                mas=mas+str(mjson["result"]["songs"][i]["artists"][ats]["name"])
                if ats != len(mjson["result"]["songs"][i]["artists"])-1:
                    mas=mas+'/'
            mnm=str(mjson["result"]["songs"][i]["name"])+' - '+str(mas)
            nml.append(mnm)
            vip=mjson["result"]["songs"][i]["fee"]
            mid=mjson["result"]["songs"][i]["id"]
            mpc=mjson["result"]["songs"][i]["album"]["blurPicUrl"]
            mlk='http://music.163.com/song/media/outer/url?id='+str(mid)+'.mp3'
            if int(vip) == 1:
               print(str(i+1)+'. '+mnm+'(vip单曲暂不支持操作)')
            else:
                with open('C:\\Users\\'+user+'\\AppData\\Local\\Temp\\cmcs_'+str(i)+'.htm',"w") as f:
                    f.write('<html><head></head><body><center><img src="'+mpc+'" alt="'+mnm+'" width="256" height="256"><br/><audio controls><source src="'+mlk+'" type="audio/mpeg"></audio><br/><font color="blue"><h2>'+mnm+'</h2><h3><br/>#依赖于网易云音乐API的MP3爬虫#<br/>作者:<a href ="https://github.com/tudou-eth">tudou-eth<a></h3></font><center></body></html>')
                    f.close()
                print(str(i+1)+'. '+mnm)
    except:
        if i==0:
            print("很抱歉，未找到相关结果")
            time.sleep(2.5)
            res()
            if exit == 1:
                exit()
        else:
            pass
    c=input("输入您想操作的结果(1~"+str(i+1)+"):")
    try:
        c=int(c)
        if c>0 and c<i+2:
            fpth='C:/Users/'+user+'/AppData/Local/Temp/cmcs_'+str(c-1)+'.htm'
            if os.path.isfile(fpth):
                sys.excepthook = cef.ExceptHook
                if proxy1 != 'loc':
                    switches = {
                        "enable-media-stream": "",
                        "proxy-server": '127.0.0.1:8029',
                        "disable-gpu": "",
                    }
                    cef.Initialize(switches=switches)
                else:
                    cef.Initialize()
                cef.CreateBrowserSync(url='file:///'+fpth,window_title="歌曲预览/"+nml[c-1])
                cef.MessageLoop()
                print("操作成功，感谢您的使用！")
                re='N'
                time.sleep(1.25)
                res()
                if exit==1:
                    time.sleep(2)
                    exit()
            else:
                print("操作失败，暂不支持vip单曲！")
                res()
                if exit==1:
                    time.sleep(2)
                    exit()
        else:
            print("操作失败，请输入1~"+str(i+1)+"之间的整数！")
            res()
            if exit==1:
                time.sleep(2)
                exit()
    except Exception as exc:
        if exc == "":
            print("操作失败，请输入整数！")
            res()
            if exit==1:
                time.sleep(2)
                exit()
        else:
            print(exc)
            res()
            if exit==1:
                time.sleep(2)
                exit()
if __name__ == '__main__':
    CMCS()
