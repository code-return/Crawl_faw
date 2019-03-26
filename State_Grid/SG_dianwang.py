"""
国家电网有限公司
"""
from lxml import etree

import requests
from requests import RequestException
from tools import *

#获取首页内容
def get_one_page(url):

    try:
        # 需要重置requests的headers。
        headers = {
            "user-agent": 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
        response = requests.get(url, headers=headers)
        # 加一个判断，判断请求URL是否成功
        if response.status_code == 200:
            response.encoding = 'utf-8'
            return response.text
        return None
    except RequestException:
        return None

#解析网页
def parse_one_page(html):

    infos = []
    car_count = 0
    true_count = 0
    time_out = False  ### 时间判断
    base_url = 'http://ecp.sgcc.com.cn/html/project/'
    province = '国家电网有限公司'
    province_file = '国家电网有限公司'

    selector = etree.HTML(html)

    time = selector.xpath("//*[@class='content']/div/table[@class='font02 tab_padd8']/tr/td[4]/text()")
    time = time[1:]
    title = selector.xpath("//*[@class='content']/div/table[@class='font02 tab_padd8']/tr/td/a/@title")
    hrefAttr = selector.xpath("//*[@class='content']/div/table[@class='font02 tab_padd8']/tr/td/a/@onclick")

    # for i in range(0,len(time)):
    #     infos.append(time[i] +  title[i] + hrefAttr[i])
    # #print(infos)
    # for info in infos:
    #     print(info)
    for i in range(0,len(hrefAttr)):
        #获取二级页面的跳转参数，以便进行二级页面url拼接
        string = str(hrefAttr[i])
        attr1 = re.findall("\d+",string)[0]
        attr2 = re.findall("\d+",string)[1]
        # print(attr1)
        # print(attr2)
        try:
            if time_restrant(time[i]) == True:#判断时间是否符合要求
                #if title_restraint(time[i],car_count, true_count) == True:
                sign, car_count, true_count = title_restraint(title[i], car_count, true_count)
                if sign == False:
                    continue
                else:
                    try:
                        new_url = base_url + attr1 + "/" + attr2 + ".html"#拼接二级页面的url
                        # urls.append(new_url)
                        #infos.append(time[i].strip() + title[i].strip() + new_url)
                        content = str(getContent(new_url))#获取二级页面的内容
                        # print(type(content))
                        # print(content.strip())
                        # state = store(title[i], time[i], content, new_url,corporation='中国海洋石油集团有限公司')
                        #存储标题，时间，二级页面内容，公司名，二级页面url
                        state = store(title[i], time[i], content, province, new_url)

                        if state == False:  # 数据库中存在该数据
                            time_out = True
                            print("time_out!")
                            break
                    except Exception as e:
                        print(e)
            else:
                time_out = True
                print("time_out!")
                break
        except Exception as e:
            print(e)
        if time_out == True:
            break

        store_nbd_log(car_count, true_count, province_file)#存储日志信息


#获取最大页码
def getMaxpage(html):

    selector = etree.HTML(html)
    #浏览器会对html文本进行规范化，会在路径中自动添加tbody，导致读取失败，此处在xpath中直接去除tbody即可
    # page_num = selector.xpath("//*[@id='categorypagingcontent']/div/div/table/tr/td[@class='huifont']/text()")
    page_num = selector.xpath("//*[@class='contentRight']/div/a/text()")
    # return page_num[1][-3:]
    return int(page_num[-1])

#获取二级页面的文本内容
def getContent(url):

    response = requests.get(url)
    # 加一个判断，判断请求URL是否成功
    if response.status_code == 200:
        response.encoding = 'utf-8' #网页转码，不加则文本出现乱码

        """下面将二级页面的源代码爬取下来，并用bs4提取属于文章部分的标签,
        并用xpath提取标签中全部的文本"""

        soup = BeautifulSoup(response.text,'html.parser')
        #从网页源代码中挑选出公告主体部分的div标签,标签类型为<class 'bs4.element.Tag'>
        # 用get_text()将其转换为str
        table = soup.find_all('table','font02')[0].get_text()

        #用xpath提取标签中的全部文本
        selector = etree.HTML(table)
        content = selector.xpath('string(.)')

        return content

def main():

    url = "http://ecp.sgcc.com.cn/project_list.jsp?site=global&column_code=014001001&project_type=1"
    html = get_one_page(url)
    parse_one_page(html)
    page_num = getMaxpage(html)
    # print(page_num)
    # 拼接翻页的url，并返回翻页的源代码
    for i in range(2,page_num + 1):
        next_url = url + "&company_id=&status=&project_name=&pageNo=" + str(i)
        next_html = get_one_page(next_url)
        parse_one_page(next_html)


if __name__ == '__main__':
    main()