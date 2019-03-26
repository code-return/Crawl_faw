"""
中国邮政
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
    base_url = 'http://www.chinapost.com.cn'
    province = '中国邮政'
    province_file = '中国邮政'

    selector = etree.HTML(html)

    time = selector.xpath("//*[@id='ReportIDIssueTime']/text()")
    title = selector.xpath("//*[@id='ReportIDname']/a/@title")
    href = selector.xpath("//*[@id='ReportIDname']/a/@href")

    for i in range(0,len(time)):
    #     infos.append(time[i]+title[i]+href[i])
    # print(infos)
    # for info in infos:
    #     print(info)

        try:
            if time_restrant(time[i]) == True:#判断时间是否符合要求
                sign, car_count, true_count = title_restraint(title[i], car_count, true_count)
                if sign == False:
                    continue
                else:
                    try:
                        new_url = base_url + href[i]#拼接二级页面的url
                        content = str(getContent(new_url))#获取二级页面的内容
                        # print(type(content))
                        # print(content.strip())

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
    lastPage = selector.xpath("//*[@class='new_list']/ul/li[@id='PageNum']/a[@id='CBLast']/@href")
    # return page_num[1][-3:]
    # return int(page_num[1][-3:])
    page_num = re.findall("-(\d+).",str(lastPage))[0]
    return int(page_num)

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
        div = soup.find_all('div','new_text')[0].get_text()

        #用xpath提取标签中的全部文本
        selector = etree.HTML(div)
        content = selector.xpath('string(.)')

        return content

def main():
    """
    urls中分别对应着集团公司，省邮政分公司，邮政储蓄银行，中邮保险，集团公司直属单位
    """
    urls = ['7294-','7331-','7338-','7345-','7360-']
    for i in range(0,len(urls)):
        strPost = '1.htm'#url后缀
        base_url = "http://www.chinapost.com.cn/html1/category/181313/" + str(urls[i])
        url = base_url + strPost
        html = get_one_page(url)
        # print(html)
        parse_one_page(html)
        page_num = getMaxpage(html)
        getMaxpage(html)
        for i in range(2,page_num + 1):
            next_url = base_url + strPost.replace('1',str(page_num))
            next_html = get_one_page(next_url)
            parse_one_page(next_html)


if __name__ == '__main__':
    main()