import requests
import time
import chaojiying
from emailsend import emailsend
from bs4 import BeautifulSoup
from lxml import etree

#http://111.160.75.143:9081/KWService/yjcjjg.do
#202.113.160.165:9081
# code_url = 'http://202.113.160.165:9081/KWService/servlet/ImageServlet?d='
# post_url = 'http://202.113.160.165:9081/KWService/yscjjg.do'
#收件箱地址
server = ''
web_url = 'http://111.160.75.143:9081/KWService/cjcx_G02.do'
code_url = 'http://111.160.75.143:9081/KWService/servlet/ImageServlet?d='
post_url = 'http://111.160.75.143:9081/KWService/'


class Score(object):
    
    r = requests.session()
    
    def __init__(self,ksbh,sfzh):
        self.ksbh = ksbh
        self.sfzh = sfzh

    def get_times(self):
        t = time.localtime()  
        year = str(t.tm_year)
        month = '0' + str(t.tm_mon)
        day = str(t.tm_mday)
        hour = str(t.tm_hour)
        minute = str(t.tm_min)
        second = str(t.tm_sec)
        time_ = year+month+day+hour+minute+second
        return time_
    
    def get_code(self):
        img = self.r.get(code_url + self.get_times())
        cap = chaojiying.run(img.content) 
        return cap
    
    def get_body(self,postUrl,email):
        #webbrowser.open(web_url)
        code = self.get_code()
        headers = {
                'Connection': 'keep - alive',
                'Host': '111.160.75.143:9081',
                'Referer': 'http://111.160.75.143:9081/KWService/cjcx_G02.do',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3486.0 Safari/537.36',
            }
        self.r.headers = headers
        parms = {
            'ksbh':self.ksbh,
            'zjhm':self.sfzh,
            'code': code,
        }
        
        response = self.r.post(postUrl,data=parms)
        res = response.text
        score = []
        if '总分' in res:
            soup = BeautifulSoup(response.content, 'lxml')
            trs = soup.find(id="result_output").findAll("tr")
            for tds in trs:
                th = tds.find('th')
                td = tds.find('td')
                score.append(th.string + td.string)
            print(''.join(score))
            emailsend(''.join(score),email)
        elif '验证码' in res:
            print('验证码错误!')
            #emailsend(res,email)
        elif '系统未能查询到符合条件的数据' in res:
            print('系统未能查询到符合条件的数据,请核对您输入的查询信息后重新查询！')
            #emailsend(res,email)
        else:
            print('Something Wrong!')
            #emailsend(res,email)
 
def send(text_):
    data = {
        'text':'开通了',
        'desp':text_
    }
    requests.post('https://sc.ftqq.com/'+server+'.send',data=data)   
    
def get_post_url(email):
    web_body = requests.get(web_url,allow_redirects=False)
    if web_body.status_code == 200:
        try:
            selector = etree.HTML(web_body.content)
            body_title = selector.xpath('//*[@id="main_content"]/form')[0].attrib['action']
            
            post_url_end = post_url + body_title
            return post_url_end
        except:
            emailsend('开通了请手动查询'+web_url,email)
            send('开通了请手动查询')
            return 'nothing'
        finally:
            #emailsend('开通了请手动查询'+web_url,email)
            pass
    else:
        return 'nothing'

    
def main(ksbh,sfzh,email):
    postUrl =  get_post_url(email)
    if postUrl == 'nothing':
        print('还没有开通...')
        return
    else:
        pscore = Score(ksbh,sfzh)
        pscore.get_body(postUrl,email)
        print('30S后退出！')
        time.sleep(30)
        exit()

if __name__ == "__main__":

    ksbh = ''
    sfzh = ''
    email = ''
    while True:
        main(ksbh,sfzh,email)
        print('40S后重新获取！')
        time.sleep(40)