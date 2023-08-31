from flask import Flask, after_this_request
from flask import render_template
from urllib.request import urlopen
from bs4 import BeautifulSoup
import json
import requests
import util
import os
import urllib.request
from multiprocessing import Process
from apscheduler.schedulers.background import BackgroundScheduler
from flask_sqlalchemy import SQLAlchemy
from models import db, Post, Word, Blog
import tweepy

# import win32serviceutil
# import servicemanager
# import ctypes
# import sys
# import time

# OutputDebugString = ctypes.windll.kernel32.OutputDebugStringW

app = Flask(__name__)


# 현재있는 파일의 디렉토리 절대경로
base_dir = os.path.abspath(os.path.dirname(__file__))

# basdir 경로안에 DB파일 만들기
db_file = os.path.join(base_dir, 'db.sqlite')

# SQLAlchemy 설정
# 내가 사용 할 DB URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_file

# 비지니스 로직이 끝날때 Commit 실행(DB반영)
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

# 수정사항에 대한 TRACK
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY'] = 'aldkfjaoermqeoifalkdjfnalkdsfjjkdk'


# sqlite
db.init_app(app)
db.app = app
# db.create_all()
with app.app_context():
    db.create_all()



@app.route('/index')
def index1():
    return 'Hello data'


@app.route('/')
def index():
    return render_template('index.html', to="data~~~~~~~~~~~~~~~~~~~~~~~~~~~")


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

    # return requests.post(data)
    return render_template('getData.html', to=res.text)


@app.route('/getDeal')
def getDeal():
    returnStr = {}

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
        print(book_page_url)
        bsObject = BeautifulSoup(html, "html.parser")
        title = bsObject.find('span', 'np_18px_span').text
        image_url = None

        try:
            image_url = bsObject.find('meta', {'property': 'og:image'}).get('content')
        except AttributeError as e:
            print(e)

        url = bsObject.find('meta', {'property': 'og:url'}).get('content')
        key = url.split('/')[3]
        post_url = bsObject.find('a', 'hotdeal_url')["href"]
        # print("111111111111:" + post_url)

        # print(index + 1, title, image, url, key)
        # detail_info.append([index + 1, title, image, url])

        # 블로깅 지정 단어
        # words = Word.query.all()
        # title_list = title.split(' ')
        # search_words = list(set(words) - set(title_list))

        # if title_list in words: # 검색어가 있는지?
        #     post_list = Post.query.filter(Post.post_key == key)
        #     print(post_list)
        #
        #     if post_list is None:   #이전에 등록했는지?
        #         post_write(title, image_url, post_url, key)
        #         post = Post(post_key=key)
        #         db.session.add(post)
        post_list = Post.query.filter(Post.post_key == key).first()
        # print(post_list)
        # print(key)
        if post_list is None:   #이전에 등록했는지?
            # post_write(title, image_url, post_url, key)
            returnStr = post_write(title, image_url, post_url, key)
            post = Post(post_key=key)
            db.session.add(post)
            db.session.commit()

    # return render_template('getData.html', to=detail_info)
    return render_template('getData.html', to=returnStr)


def post_write(title, image_url, post_url, key):
    url = "https://www.tistory.com/apis/post/write?"
    output = "json"
    test_image = ""
    image_file_name = ""

    if image_url is not None:
        # 이미지 다운로드
        image_file_name = key + ".jpg"
        urllib.request.urlretrieve(image_url, image_file_name)

        # 이미지 업로드
        files = {'uploadedfile': open(image_file_name, 'rb')}
        params = {'access_token': access_token, 'blogName': blogName, 'targetUrl': blogName, 'output': 'json'}
        rd = requests.post('https://www.tistory.com/apis/post/attach', params=params, files=files)
        item = json.loads(rd.text)
        test_image = item["tistory"]["replacer"]

    # 본문
    visibility = 3  #0: 비공개 - 기본값, 1: 보호, 3: 발행
    title_str = title.split(' ')
    tags = "핫딜," + ','.join(title_str)  # 태그는 쉼표로 구분
    content = '<p>' + test_image + '</p>'
    content += '<p data-ke-size="size16">출처 : <a href="' + post_url + '" target="_blank" rel="noopener">' + post_url + '</a></p>'

    data = url
    data += "access_token=" + access_token + "&"
    data += "output=" + output + "&"
    data += "blogName=" + blogName + "&"
    data += "title=" + title + "&"
    data += "content=" + content + "&"
    data += "category=1167012"  #핫딜 카테고리

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
    print(str(res.status_code) + " | " + res.text)

    # 트위터 글쓰기
    # update_tweet(title)
    
    # 이미지 삭제 - 프로세스가 잡고 있는 에러 발생
    # if image_url is not None:
    #     os.remove(image_file_name)
    @after_this_request
    def cleanup(response):
        os.remove(image_file_name)
        return response

    # return render_template('getData.html', to={'test'})
    # return render_template('getData.html', to=res.text)
    blog_write(title, res.text)
    return str(res.status_code) + " | " + res.text


def blog_write(title, response_txt):
    jsonObject = json.loads(response_txt)
    blogObject = jsonObject.get("tistory")
    postId = blogObject.get("postId")
    status = jsonObject.get("tistory").get("status")
    url = jsonObject.get("tistory").get("url")

    blog_list = Blog.query.filter(Blog.postId == postId).first()
    if blog_list is None:  # 이전에 등록했는지?
        blog = Blog(postId=postId, status=status, url=url)
        db.session.add(blog)
        db.session.commit()

        update_tweet(title + " " + url)



## 트위터 api와 연결
# def connect_api():
#     consumer_key = 'consumer_key'
#     consumer_secret = 'consumer_secret'
#     access_token = 'access_token'
#     access_token_secret = 'access_token_secret'
#
#     auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
#     auth.set_access_token(access_token, access_token_secret)
#     api = tweepy.API(auth)
#
#     return api


# 트위터 api와 연결
def update_tweet(tweet):
    # 트위터 작성
    # auth = tweepy.OAuthHandler(twitter_api_key, twitter_api_key_secret)
    # auth.set_access_token(twitter_access_token, twitter_access_token_secret)
    # api = tweepy.API(auth)
    # api.update_status(tweet)

    api = tweepy.Client(consumer_key=twitter_api_key,
                           consumer_secret=twitter_api_key_secret,
                           access_token=twitter_access_token,
                           access_token_secret=twitter_access_token_secret)

    # mediaID1 = mediaID = api.media_upload("media1.png")
    # mediaID2 = mediaID = api.media_upload("image2.png")
    # mediaID3 = mediaID = api.media_upload("image3.png")
    #
    # api.create_tweet(text='I want to Post 3 Photos and description',
    #                  media={media_ids=[mediaID1,mediaID2,mediaID3]})
    response = api.create_tweet(text=tweet)
    print(response)



# 스케줄
sched = BackgroundScheduler(daemon=True)
sched.add_job(getDeal, 'interval', minutes=60)
sched.start()


# class MyServiceFramework(win32serviceutil.ServiceFramework):
#     _svc_name_ = 'MyPythonService'
#     _svc_display_name_ = 'My Python Service'
#     is_running = False
#
#     def SvcStop(self):
#         OutputDebugString("MyServiceFramework __SvcStop__")
#         self.is_running = False
#
#     def SvcDoRun(self):
#         self.is_running = True
#         while self.is_running:
#             OutputDebugString("MyServiceFramework __loop__")
#             time.sleep(1)


if __name__ == "__main__":
    # token = getAccessToken().content
    # print(token.decode('utf-8'))
    app.run(host='127.0.0.1', port=5000, debug=True)
    # win32serviceutil.HandleCommandLine(MyServiceFramework)
