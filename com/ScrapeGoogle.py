import requests
from bs4 import BeautifulSoup
import time
import re
import os


USER_AGENT = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

def parse_results(html, keyword, google_url, baserate):

    pattern = re.compile(r"[\d\.]+")

    soup = BeautifulSoup(html, 'html.parser')

    found_results = []

    result_block = soup.find_all('div', attrs={'class': 'g'})
    for result in result_block:

        link = result.find('a', href=True)
        rating = result.find('div', attrs={'class': 'slp f'})
        if link and rating:
            link = link['href']
            rating = str(rating.get_text())

            if rating.strip() != "":
                rating = pattern.findall(rating)[0]
                if float(rating) > float(baserate):
                    if link != '#':
                        found_results.append({"google_url":google_url, 'keyword': keyword, 'link': link, 'rating.txt': rating})
    return found_results

def fetch_results(search_term, number_results, language_code, start):
    assert isinstance(search_term, str), 'Search term must be a string'
    assert isinstance(number_results, int), 'Number of results must be an integer'
    escaped_search_term = search_term.replace(' ', '+')

    google_url = 'https://www.google.co.jp/search?q=site:amazon.com+{}+currently+unavailable&num={}&hl={}&start={}'\
        .format(escaped_search_term, number_results, language_code,start)
    response = requests.get(google_url, headers=USER_AGENT)
    response.raise_for_status()

    return search_term, response.text, google_url

def scrape_google(search_term, number_results, language_code, start, rating):
    try:
        keyword, html, google_url = fetch_results(search_term, number_results, language_code, start)
        results = parse_results(html, keyword, google_url, rating)
        return results
    except AssertionError:
        raise Exception("Incorrect arguments parsed to function")
    except requests.HTTPError:
        raise Exception("You appear to have been blocked by Google")
    except requests.RequestException:
        raise Exception("Appears to be an issue with your connection")


if __name__ == '__main__':
    keywords = []
    rating = 0
    try:
        product = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "product.txt"
        rating = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "rating.txt"
        f1 = open(product, "r")
        f2 = open("rating.txt", "r")
        lines = f1.readlines()
        rating = f2.read()
    finally:
        f1.close()
        f2.close()

    for line in lines:
        keywords.append(line)
    # keywords = ['bark collar']
    datas = []
    for keyword in keywords:
        try:
            for i in range(0,2):
                results = scrape_google(keyword, 100, "en", i*100, rating)
                for result in results:
                    datas.append(result)
                time.sleep(15)
        except Exception as e:
            print(e)
        finally:
            time.sleep(10)

    for data in datas:
        print(data.get("link") + "\t" + data.get("rating.txt"))