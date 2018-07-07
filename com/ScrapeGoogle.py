import requests
from bs4 import BeautifulSoup
import time
import re
import os
from com.Properties import Properties
import datetime
import xlsxwriter


USER_AGENT = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

# info.properties配置文件
infoFile = os.path.dirname(os.path.abspath(__file__)) + os.sep + "info.properties"
properties = Properties(infoFile)

def parse_results(html, keyword, google_url):

    pattern = re.compile(r"[\d\.]+")

    soup = BeautifulSoup(html, 'html.parser')

    found_results = []

    result_block = soup.find_all('div', attrs={'class': 'g'})
    for result in result_block:

        link = result.find('a', href=True)
        rating = result.find('div', attrs={'class': 'slp f'})
        title = result.find('h3', attrs={'class': 'r'})
        if link and rating:
            link = link['href']
            rating = str(rating.get_text())
            title = title.get_text()

            if rating.strip() != "":
                rating = pattern.findall(rating)[0]
                if float(rating) > float(properties.get("rating")):
                    if link != '#':
                        found_results.append({"google_url":google_url, 'keyword': keyword,
                                              'link': link, 'rating': rating, 'title': title})
    return found_results


def fetch_results(search_term, number_results, language_code, start):
    assert isinstance(search_term, str), 'Search term must be a string'
    assert isinstance(number_results, int), 'Number of results must be an integer'
    escaped_search_term = search_term.replace(' ', '+')

    # 谷歌地址
    googleUrl = properties.get("googleUrl")
    # 亚马逊地址
    amazonUrl = properties.get("amazonUrl")

    google_url = '{}/search?q=site:{}+{}+currently+unavailable&num={}&start={}'\
        .format(googleUrl, amazonUrl, escaped_search_term, number_results,start)
    response = requests.get(google_url,headers=USER_AGENT)
    response.raise_for_status()

    return search_term, response.text, google_url


def scrape_google(search_term, number_results, language_code, start):
    try:
        keyword, html, google_url = fetch_results(search_term, number_results, language_code, start)
        results = parse_results(html, keyword, google_url)
        return results
    except AssertionError:
        raise Exception("Incorrect arguments parsed to function")
    except requests.HTTPError:
        raise Exception("You appear to have been blocked by Google")
    except requests.RequestException:
        raise Exception("Appears to be an issue with your connection")

def writeToExcel(datas):

    nowTime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    filename = nowTime + "_" + properties.get("products")

    resultFilePath = properties.get("resultFilePath")

    if not os.path.exists(resultFilePath):
        os.makedirs(resultFilePath)

    workbook = xlsxwriter.Workbook(os.path.abspath(resultFilePath) + os.sep + filename + ".xlsx")
    worksheet = workbook.add_worksheet()


    row = 0
    worksheet.write(row, 0, "网址")
    worksheet.write(row, 1, "评分")
    worksheet.write(row, 2, "标题")

    row = row + 1

    for data in datas:
        worksheet.write(row, 0, data.get("link"))
        worksheet.write(row, 1, data.get("rating"))
        worksheet.write(row, 2, data.get("title"))
        row = row + 1



if __name__ == '__main__':

    # 获取程序开始执行的时间
    starttime = datetime.datetime.now()

    print("程序开始执行!!!")

    # 获取产品列表
    products = []
    productList = properties.get("products")
    if productList.find(",") > 0:
        products = productList.split(",")
    else:
        products.append(productList)

    datas = []
    for product in products:
        try:
            for i in range(0, 10):
                print("开始获取第{}页数据!!!".format(str(i+1)))
                results = scrape_google(product, 100, "en", i*100)
                for result in results:
                    datas.append(result)
                time.sleep(int(properties.get("interval")))
                print("第{}页数据获取完毕!!!".format(str(i+1)))
        except Exception as e:
            print(e)
        finally:
            time.sleep(10)

    print("所有数据获取完毕，开始生成结果文件!!!")
    writeToExcel(datas)
    print("结果文件生成完毕!!!")

    # 打开文件夹尽在Windows系统下有效
    os.system("start explorer " + properties.get("resultFilePath"))

    # 获取程序执行结束的时间
    endtime = datetime.datetime.now()
    intervalTime = str(endtime - starttime)
    minute = intervalTime.split(":")[1]
    seconds = intervalTime.split(":")[2].split(".")[0]
    print("程序共运行{}分{}秒".format(minute,seconds))
