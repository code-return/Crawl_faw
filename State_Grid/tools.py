# -*- coding:utf-8 -*-
import os
import re
import csv
import xlwt
import pymysql
import urllib.error
import urllib.request
import random
import datetime
import json
import http.cookiejar 
from bs4 import BeautifulSoup     ###tools文件 是用beautifulSoup来解析的，还有get和post的请求函数  标题和时间的判断函数 
# 关闭ssl认证（北京报错）
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

most_kw_arr = ['车']
pos_kw_arr =  ['购', '采', '招标','租','服务']  ##需要的标题内容
neg_kw_arr = ['中标', '合同', '更正', '废标','流标', '保险', '成交', '车间', '车牌','车库','停车场',
             '推车式','车载','车床','单一来源','结果公告','配件', '维修', '变更', '实验室','实训', '工程']
                                             ##不需要的标题内容
def time_restrant(date): # 时间判断函数
    thisYear = int(datetime.date.today().year)  
    thisMonth = int(datetime.date.today().month)
    thisday = int(datetime.date.today().day)
    year = int(date.split('-')[0])
    month = int(date.split('-')[1])
    day = int(date.split('-')[2])
    #if ((thisYear - year <= 1) or (thisYear - year == 2 and month >= thisMonth)):  # 爬取24个月内的信息
    # if (thisYear == year and month == thisMonth and day == thisday):  # 这里是设置时间的地方
    #if (thisYear == year and month == thisMonth): 
    if (thisYear == year):
    #if thisYear == year:
        return True
    else:
        return False

def title_restraint(title,car_count, true_count):  # 标题判断函数
    global most_kw_arr
    global pos_kw_arr
    global neg_kw_arr
    car_count += 1
    if title.find(u"车") == -1:  # or title.find(u"采购公告"):
        return False,car_count, true_count
    else:
        #car_count += 1
        neg_sign = 0
        pos_sign = 0

        for neg_i in neg_kw_arr:
            if title.find(neg_i) != -1:  # 出现了d_neg_kw中的词
                neg_sign = 1
                break

        for pos_i in pos_kw_arr:
            if title.find(pos_i) != -1:  # 出现了d_pos_kw中的词
                pos_sign = 1
                break

        if neg_sign == 1:
            return False,car_count, true_count
        else:
            if pos_sign == 0:
                return False,car_count, true_count
            elif pos_sign == 1:
                true_count += 1
                return True,car_count, true_count

def init_get(thisurl,encoding = "utf-8"):  # 爬取网页并返回BeautifulSoup对象
    print("init:")
    print(thisurl)
    try:
        uapools = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 Safari/537.36 SE 2.X MetaSr 1.0",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)",
        ]

        #利用cookie Jar实例对象 来保存cookie
        cjar = http.cookiejar.CookieJar()
        #利用urllib库中的request的HTTPCookieProcessor 来创建cookie处理器
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cjar))
        thisua = random.choice(uapools) #在上面的uapools中 随即获得一个 
        ua = ("User-Agent", thisua) ##要把随机出来的选择 组成一个 headers
        opener.addheaders = [ua] ##在opener添加headers
        urllib.request.install_opener(opener)
        req = urllib.request.Request(thisurl) 
        html = urllib.request.urlopen(req,timeout=20).read().decode(encoding, "ignore") 
        soup = BeautifulSoup(html, 'html.parser')
        return soup

    except urllib.error.HTTPError as e:
        print(e.code)
        print(e.reason)
    except urllib.error.URLError as e:
        print(e.reason)
    except Exception as e:
        print(e)

def init_post(thisurl,post_dict,encoding = "utf-8"):  # 爬取网页并返回BeautifulSoup对象
    print("init:")
    print(thisurl)
    try:
        uapools = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 Safari/537.36 SE 2.X MetaSr 1.0",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)",
        ]
        postdata = urllib.parse.urlencode(post_dict).encode('utf-8') ##post_dict 需要post的参数
        #proxy = urllib.request.ProxyHandler({proxy: proxy_addr}) # 代理
        cjar = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cjar))#proxy,urllib.request.HTTPHandler)

        thisua = random.choice(uapools) # user-agent
        ua = ("User-Agent", thisua)
        opener.addheaders = [ua]

        urllib.request.install_opener(opener)
        req = urllib.request.Request(thisurl, postdata)
        html = urllib.request.urlopen(req,timeout=20).read().decode(encoding, "ignore")  ###获取到html源码

        soup = BeautifulSoup(html, 'html.parser')
        return soup

    except urllib.error.HTTPError as e:
        print(e.code)
        print(e.reason)
    except urllib.error.URLError as e:
        print(e.reason)
    except Exception as e:
        print(e)

def getText(item): # 获得item标签下的所有文本
    print("getText:")
    return item.get_text()

def removeBlank(text):
    print("removeBlank:")
    text = re.split("\r|\n", text.strip()) # 不使用空格分隔
    line = [re.sub("(\t|\s| )+", " ",i.strip()) for i in text] # 移除空格，空格至少出现两次的话替换成一个空格

    for i in line: # 去除空行，虽然还会存在空行
        if i.strip() == "":
            line.remove(i)

    for i in range(0,len(line)):
        if re.search("([\u4e00-\u9fa5]+$)|([A-Za-z0-9]+$)",line[i]): # 匹配到以中文，数字，字母结尾的句子
            line[i] = line[i] + " "
        else:
            continue

    return "".join(line)


def mySQL(datebase,sql,title,date,province):  ####数据库pydb建立后 用户名和密码的调整 根据自己来修改
    conn = pymysql.Connect(host="127.0.0.1", port=3306, user="root", passwd="root", db="pydb", charset="utf8")
    conn.autocommit(False)
    cursor = conn.cursor()
    state = True
    #cursor.execute(sql)
    #conn.commit()
    query_sql = "select * from nbd_message where title = '%s' and time = '%s' and province = '%s'" % (title, date, province)
    cursor.execute(query_sql)
    if cursor.rowcount == 0:
        cursor.execute(sql)
        print("sql_rowcount = ", cursor.rowcount)
        conn.commit()
    else:
        print("alreadly existed !",title,date,province)
        state = False
    cursor.close()
    return state

def excute_sql(datebase,sql):   ###数据库连接 pydb建立后 需要修改的是 用户名和密码  根据个人
    conn = pymysql.Connect(host="127.0.0.1", port=3306, user="root", passwd="root", db="pydb", charset="utf8")
    conn.autocommit(False)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    cursor.close()

def removeSingleQuote(title,content):
    title = title.replace("'", "")
    content = content.replace("'", "")
    return title, content

def store(title, date, content, province, url): # 向nbd_message表存储 
    title, content = removeSingleQuote(title, content)
    sql = "insert into nbd_message (title,time,content,province,href) values('%s','%s','%s','%s','%s')" % (
    title, date, content, province, url)
    return mySQL("pydb", sql, title, date, province)


def store_nbd_log(car_count, true_count, province_file): # 向nbd_spider_log表存储
    sql = "insert into nbd_spider_log (total_num,get_num,pro_name,spider_time) values('%d','%d','%s','%s')" % (
    car_count, true_count, province_file,str(datetime.date.today()))
    excute_sql("pydb", sql)

# def write_csv(file_out,head,List):   ##csv的函数 操作 用不上
#     print("write_csv:")
#     with open(file_out,"w",newline='') as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow(head)
#         #writer.writerows(List)
# 
#         for line in List:
#             try:
#                 writer.writerow(line)
#             except Exception as e:
#                 print(e)

# def excel_init(sheet_name='province',myencode='utf-8'):   ####这四个函数 是xlwt的表格操作    用不上  
#     workbook = xlwt.Workbook(encoding=myencode)
#     worksheet = workbook.add_sheet(sheet_name)
#     return workbook,worksheet
# 
# def addSheet(row,data,worksheet):
#     for i in range(len(data)) :
#         worksheet.write(row,i,data[i])
# 
# def saveExcel(workbook,name):
#     workbook.save(name)
# 
# def write_excel(filename,head,List):
#     workbook, worksheet = excel_init(sheet_name=filename, myencode='utf-8')
# 
#     addSheet(0, head, worksheet)
#     for line in range(len(List)):
#         try:
#             addSheet(line+1,List[line],worksheet)
#         except Exception as e:
#             print(e)
# 
#     saveExcel(workbook, filename)