import requests

def getAccessToken():
    url = "https://www.tistory.com/oauth/access_token?"
    client_id = "[앱 관리] - APP ID"
    client_secret = "[앱 관리] - Secret Key"
    code = "2번에서 허가하기를 눌러 받은 code 값"
    redirect_uri = "[앱 관리]에서 설정한 값"
    grant_type="authorization_code" # authorization_code 고정

    data = url
    data += "client_id="+client_id+"&"
    data += "client_secret="+client_secret+"&"
    data += "redirect_uri="+redirect_uri+"&"
    data += "code="+code+"&"
    data += "grant_type="+grant_type
    print(data)
    return  requests.get(data)

# if __name__ == "__main__":
#     token = getAccessToken().content
#     print(token.decode('utf-8'))