"""
中国石油化工集团有限公司
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
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cookie':'ASP.NET_SessionId=5vrlfc2vtgxe1z1yjcfo3ait',
            'Host': 'ebidding.sinopec.com',
            'Upgrade-Insecure-Requests':1,
            'Origin': 'http://www.dyyscx.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
            }
        #参数： verify：Ture/False，默认是Ture，用于验证SSL证书开关
        #中石化网站需要安全证书
        requests.packages.urllib3.disable_warnings()
        response = requests.get(url, headers=headers,verify=False)
        # 加一个判断，判断请求URL是否成功
        if response.status_code == 200:
        #中石油网页的编码方式为gbk，直接爬取会出现乱码，这里采用网页编码重新解决
            html =  response.content.decode('gbk','ignore')

            return html
        return None
    except RequestException:
        return None

# #解析网页
def parse_one_page(html):

    infos = []
    car_count = 0
    true_count = 0
    time_out = False  ### 时间判断
    base_url = 'https://ebidding.sinopec.com'
    province = '中国石油化工集团有限公司'
    province_file = '中国石油化工集团有限公司'

    selector = etree.HTML(html)

    time = selector.xpath("//*[@id='form1']/ul/li[@class='ewb-list-node clearfix']/span/text()")
    title = selector.xpath("//*[@id='form1']/ul/li[@class='ewb-list-node clearfix']/a/@title")
    href = selector.xpath("//*[@id='form1']/ul/li[@class='ewb-list-node clearfix']/a/@href")

    for i in range(0,len(time)):
        infos.append(time[i].strip() + title[i] + href[i])
        # print(infos)
    # for info in infos:
    #     print(info)
        try:
            if time_restrant(time[i]) == True:#判断时间是否符合要求
                # if title_restraint(time[i],car_count, true_count) == True:
                sign, car_count, true_count = title_restraint(title[i], car_count, true_count)
                if sign == False:
                    continue
                else:
                    try:
                        new_url = base_url + href[i].strip()#拼接二级页面的url
                        # urls.append(new_url)
                        # infos.append(time[i].strip() + title[i].strip() + new_url)
                        content = str(getContent(new_url)).strip()#获取二级页面的内容
                        # print(content[0]+title[0]+time[0]+new_url[0])
                        # print(content)
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
    lastPage = selector.xpath("//*[@id='form1']/div/div/table/tr/td/@title")[-1]
    page_num = re.findall('\d+',str(lastPage))
    return int(page_num[0])
    # return int(page_num[1][-3:])

#获取二级页面的文本内容
def getContent(url):

    # 参数： verify：Ture/False，默认是Ture，用于验证SSL证书开关
    # 中石化网站需要安全证书
    requests.packages.urllib3.disable_warnings()
    response = requests.get(url, verify=False)
    # 加一个判断，判断请求URL是否成功
    if response.status_code == 200:
        html = response.content.decode('gbk', 'ignore')#网页转码，不加则文本出现乱码

        """下面将二级页面的源代码爬取下来，并用bs4提取属于文章部分的标签,
        并用xpath提取标签中全部的文本"""

        soup = BeautifulSoup(html,'html.parser')
        #从网页源代码中挑选出公告主体部分的div标签,标签类型为<class 'bs4.element.Tag'>
        # 用get_text()将其转换为str
        div = soup.find_all('div','ewb-article-info')[0].get_text()

        #用xpath提取标签中的全部文本
        selector = etree.HTML(div)
        content = selector.xpath('string(.)')

        return content

def main():
    #是ajax异步加载的。查看源代码看到的是直接从服务器下载的源代码，但是看不到之后js动态修改和加载的代码。
    url = "https://ebidding.sinopec.com/TPWeb4AAA/showinfo/shgg_more.aspx?categoryNum=002002&Paging=1"
    html = get_one_page(url)
    parse_one_page(html)
    page_num = getMaxpage(html)
    # print(html)
    # 拼接翻页的url，并返回翻页的源代码
    for i in range(2,page_num + 1):
        next_url = "https://ebidding.sinopec.com/TPWeb4AAA/showinfo/shgg_more.aspx?categoryNum=002002&Paging=" + str(i)
        next_html = get_one_page(next_url)
        parse_one_page(next_html)


if __name__ == '__main__':
    main()