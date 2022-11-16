import requests
from bs4 import BeautifulSoup
import httpx
import json
import csv
import time

wb_dic = {}
requests = requests.session()
#cookie = "_T_WM=54e6e475ad6ab2e59965a22eb3c77b5d; SUB=_2A25PNQ21DeRhGeFJ71UQ9CrIzz6IHXVs2ZP9rDV6PUJbktCOLXjmkW1Nf9otYiHHa7e1YdaZfBaSW57us8joUaXE; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFu_oRCZxqrfRMeSUlcJ2QI5NHD95QNS0BNeKBXShBEWs4DqcjMi--NiK.Xi-2Ri--ciKnRi-zNS0MXS02XShBXentt; SSOLoginState=1647410661"
cookie = 'PC_TOKEN=31aa003456; _s_tentry=-; Apache=9028487006834.46.1668589040046; SINAGLOBAL=9028487006834.46.1668589040046; ULV=1668589040048:1:1:1:9028487006834.46.1668589040046:; SUB=_2A25OcNZBDeRhGeFJ71UQ9CrIzz6IHXVtBECJrDV8PUNbmtAKLUTdkW9Nf9otYk365qlaIiuc04HxmJK6JIQiEwc2; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFu_oRCZxqrfRMeSUlcJ2QI5JpX5KzhUgL.FoMNShMpShBXShz2dJLoIp7LxKML1KBLBKnLxKqL1hnLBoMNS0BNeKBXShBE; ALF=1700125072; SSOLoginState=1668589073'
headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cookie': cookie,
    'referer': 'https://weibo.com/2750621294/KAf1AFVPD',
    'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'traceparent': '00-5b5f81f871c6ff6846bf3a92f1d5efed-1ab32a39ad75711a-00',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
    'x-xsrf-token': '7yIZGS_IPx7EteZ6TT86YYAZ',
}

def get_wb_dic(url):
    res = requests.get(url,headers = headers)
    bs = BeautifulSoup(res.content,'lxml')
    content = bs.find_all('div',class_ = 'card-wrap')
    for each in content:
        user_msg = each.find_all('a',class_ = "name")
        if user_msg != []:
            try:
                mid = each['mid']
            except:
                pass
            else:
                user_name = user_msg[0].text
                uid = str(each.find('div', class_="avator").find('a')['href']).split('/')[-1].split("?")[0]  # 获取UID
                user_index = "https:" + user_msg[0]['href']  # 用户主页
                user_from = str(each.find('p', class_="from").text).replace(' ', '').replace('\n', '')  # 时间和发布终端设备名称
                weibo_content = str(each.find('p', class_="txt").text).replace(' ', '').replace('\n', '')  # 微博内容
                data = [weibo_content, user_name, user_from, user_index, mid, uid]
                wb_dic[mid] = data
                print("用户："+data[1]+'  mid：'+mid+'\n发布时间：'+data[2]+'\n内容：\n'+data[0]+'\n')
    


def get_comment_level1(mid, max_id):
    uid = wb_dic[mid][5]
    url = "https://weibo.com/ajax/statuses/buildComments?"

    par = {
        'id': mid,
        'is_show_bulletin': '2',
        'is_mix': '0',
        'max_id': max_id,
        'count': '20',
        'uid': uid,
    }
    client = httpx.Client(http2=True, verify=False)
    response = client.get(url, params=par, headers=headers)
    jsondata = json.loads(response.text)
    max_id = jsondata['max_id']  # 获取下一页mid
    content = jsondata['data']
    if not content:
        print("暂无更多评论")
    for each in content:
        created_at = each['created_at']  # 评论时间
        struct_time = time.strptime(created_at, '%a %b %d %H:%M:%S %z %Y')  # 评论时间
        comment_time = time.strftime("%Y-%m-%d %H:%M:%S", struct_time)  # 评论时间
        comment_text = each['text_raw']  # 评论内容
        comment_user = each['user']['screen_name']  # 评论人名称
        weibo_comment_data =[comment_user,comment_text, comment_time]
        print(comment_user+'：'+comment_text+'\n'+comment_time+'\n')
        saveCsv(wb_dic[mid][0][0:10], weibo_comment_data)

    if max_id == 0:
        pass
    else:
        get_comment_level1(wb_dic[mid][4], max_id)

def saveCsv(filename, content):
    fp = open(f"{filename}.csv", 'a+', encoding='utf-8-sig', newline='')
    csv_fp = csv.writer(fp)
    csv_fp.writerow(content)
    fp.close()
    
if __name__ == '__main__':
    if_exit = True
    while(if_exit):
        search = input("请输入搜索的内容：")
        page_num = int(input("请输入想查看的页数："))
        for  i in range(1,page_num+1):
            print("第"+str(i)+"页内容")
            url = "https://s.weibo.com/weibo?q=" + search+"&page="+str(i)
            get_wb_dic(url)
        search_mid = input("\n\n输入你要查看评论微博的mid：")
        print('\n')
        max_id = 0
        get_comment_level1(search_mid,max_id)
        if(input("是否退出？（Y/N）:") in ['Y','y']):
            if_exit = False
