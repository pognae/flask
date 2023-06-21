from io import BytesIO

from flask import Flask
from flask import render_template
import json
import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import util
from urllib import request
from PIL import Image
from io import BytesIO
import os
import urllib.request


app = Flask(__name__)

# tistory
client_id = "7691b3b1da8d9da0a280f54da72e946e"
client_secret = "7691b3b1da8d9da0a280f54da72e946e6ed455a4e577ac13b0c9e461425fda6108cd8ddb"
code = "cdf012454cdbb4b926ca627288b5e3be5a5ce7ae09ee7d8bebe6949f39269cb57f8eb478"
redirect_uri = "http://gumdrop.tistory.com"
grant_type="authorization_code" # authorization_code 고정
access_token = "c9b1a2862fb270174114e073bf1b0793_270d34f4b4ccf2a8a5f0f2a09b6e1fff"
blogName = "gumdrop"

# twitter


@app.route('/index')
def index1():
    return 'Hello data'


@app.route('/')
def index():
    return render_template('index.html', to="data~~~~~~~~~~~~~~~~~~~~~~~~~~~")


@app.route('/api')
def api():
    d = {"text": "Hello data"}
    return json.dumps(d)


def getAccessToken():
    # 토큰 생성
    url = "https://www.tistory.com/oauth/access_token?"

    data = url
    data += "client_id="+client_id+"&"
    data += "client_secret="+client_secret+"&"
    data += "redirect_uri="+redirect_uri+"&"
    data += "code="+code+"&"
    data += "grant_type="+grant_type

    print(data)
    return requests.get(data)


@app.route('/get-category')
def getCategoryID():
    # 블로그 카테고리 가져오기
    url = "https://www.tistory.com/apis/category/list?"
    output = "json"

    data = url
    data += "access_token=" + access_token + "&"
    data += "output=" + output + "&"
    data += "blogName=" + blogName

    res = requests.get(data)

    print(data)
    # return requests.get(data)
    # return json.dumps(data)
    return render_template('getData.html', to=res.text)


@app.route('/write')
def postWriting(title="No Title", content="No Content"):
    url = "https://www.tistory.com/apis/post/write?"
    output = "json"

    data = url
    data += "access_token=" + access_token + "&"
    data += "output=" + output + "&"
    data += "blogName=" + blogName + "&"
    data += "title=" + title + "&"
    data += "content=" + content + "&"
    data += "category=1167012"  #핫딜 카테고리

    # res = requests.get(data) #get
    headers = {'Content-Type': 'application/json; chearset=utf-8'}
    data = {'access_token': access_token, 'output': output, 'blogName': blogName, 'title': title, 'content': content, 'category': '1167012'}
    res = requests.post(url, data=json.dumps(data), headers=headers) #post
    print(str(res.status_code) + " | " + res.text)

    print(data)
    # return requests.post(data)
    return render_template('getData.html', to=res.text)


# @app.route('/getDeal')
def getDeal_old():
    # 핫딜 정보 가져오기(ChromeDriverManager 사용)
    # html = urlopen("https://www.fmkorea.com/hotdeal")
    # bsObject = BeautifulSoup(html, "html.parser")
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))   #error

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")
    # UserAgent값을 바꿔줍시다!
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")

    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)

    # 교보문고의 베스트셀러 웹페이지를 가져옵니다.
    driver.get("https://www.fmkorea.com/hotdeal")
    bsObject = BeautifulSoup(driver.page_source, 'html.parser')

    print(bsObject.find_all('table', 'notice_pop1'))

    # 책의 상세 웹페이지 주소를 추출하여 리스트에 저장합니다.
    book_page_urls = []
    for item in bsObject.find_all('table', 'notice_pop1'):
        url = item.select('a')[0].get('href')
        book_page_urls.append(url)
        print(url)

    # 웹페이지로부터 필요한 정보를 추출합니다.
    detail_info = []
    for index, book_page_url in enumerate(book_page_urls):
        html = urlopen(book_page_url)
        bsObject = BeautifulSoup(html, "html.parser")
        title = bsObject.find('span', 'np_18px_span').text
        # author = bsObject.find('h3', 'title_heading').a.span.text
        image = bsObject.find('meta', {'property': 'og:image'}).get('content')
        url = bsObject.find('meta', {'property': 'og:url'}).get('content')
        # price = bsObject.find('span', 'prod_info_price').span.text

        # print(index + 1, title, author, image, url, price)
        # print(index + 1, title, image, url)
        detail_info.append([index + 1, title, image, url])

    driver.quit()

    return render_template('getData.html', to=detail_info)



@app.route('/getDeal')
def getDeal():
    # 핫딜 정보 가져오기(beautifulsoup4 사용)
    hotdeal_info_url = "https://www.fmkorea.com/hotdeal"
    response = requests.get(hotdeal_info_url)

    if response.status_code != 200:
        print(response.status_code)

    html = response.text
    bsObject = BeautifulSoup(html, 'html.parser')

    # 책의 상세 웹페이지 주소를 추출하여 리스트에 저장합니다.
    book_page_urls = []
    for item in bsObject.find_all('tr', {'class': util.cond}):
        url = item.select('a')[0].get('href')
        book_page_urls.append(url)
        # print(url)

    # 웹페이지로부터 필요한 정보를 추출합니다.
    detail_info = []
    for index, book_page_url in enumerate(book_page_urls):
        html = urlopen("https://www.fmkorea.com/" + book_page_url)
        bsObject = BeautifulSoup(html, "html.parser")
        title = bsObject.find('span', 'np_18px_span').text
        image_url = bsObject.find('meta', {'property': 'og:image'}).get('content')
        url = bsObject.find('meta', {'property': 'og:url'}).get('content')
        key = url.split('/')[3]

        # print(index + 1, title, image, url, key)
        # detail_info.append([index + 1, title, image, url])
        if index == 2:
            post_write(title, image_url, url, key)

    # return render_template('getData.html', to=detail_info)
    return render_template('getData.html', to={'posting success'})


def post_write(title, image_url, post_url, key):
    url = "https://www.tistory.com/apis/post/write?"
    output = "json"

    # 이미지 다운로드
    image_file_name = key + ".jpg"
    os.system("curl " + image_url + " > " + image_file_name)

    # 이미지 업로드
    files = {'uploadedfile': open(image_file_name, 'rb')}
    params = {'access_token': access_token, 'blogName': blogName, 'targetUrl': blogName, 'output': 'json'}
    rd = requests.post('https://www.tistory.com/apis/post/attach', params=params, files=files)
    item = json.loads(rd.text)
    # print(image_file_name, item)
    test_image = item["tistory"]["replacer"]
    # print(test_image)

    # 본문
    # content = image + " " + post_url
    visibility = 0  #0: 비공개 - 기본값, 1: 보호, 3: 발행
    tags = "테스트1, 테스트2, 테스트3, 테스트4"  # 태그는 쉼표로 구분
    content = '<p>' + test_image + '</p>'
    content += '<p data-ke-size="size16">출처 : ' + post_url + '</p>'

    data = url
    data += "access_token=" + access_token + "&"
    data += "output=" + output + "&"
    data += "blogName=" + blogName + "&"
    data += "title=" + title + "&"
    data += "content=" + content + "&"
    data += "category=1167012"  #핫딜 카테고리

    # res = requests.get(data) #get
    headers = {'Content-Type': 'application/json; chearset=utf-8'}
    data = {'access_token': access_token,
            'output': output,
            'blogName': blogName,
            'title': title,
            'content': content,
            'category': '1167012',
            'visibility': visibility,
            'tag': tags
            }
    res = requests.post(url, data=json.dumps(data), headers=headers) #post
    # print(str(res.status_code) + " | " + res.text)
    #
    # print(data)
    # # return requests.post(data)
    return render_template('getData.html', to=res.text)
    # return render_template('getData.html', to={'1'})


if __name__ == "__main__":
    # token = getAccessToken().content
    # print(token.decode('utf-8'))
    app.run(host='127.0.0.1', port=5000, debug=True)