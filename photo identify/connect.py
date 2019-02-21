# 网络连接
import socket
# 线程
import threading
import time
# 数据库
import sqlite3
# base64
import base64
import hashlib
from hashlib import sha1
import os
import struct


# 网上搜集到的各种应对图片格式错误的方法
def rev(data):
    import re
    data= re.sub("[\n\r\s///+]", "", data.decode('utf-8'))
    data = re.sub("\\+","%2B",data)
    data = "image="+data
    return data


# 从response中获取json格式文本
def getjsontext(response):
    import json
    res = json.loads(response.read())
    return res


# 进行粗略文字对比，返回相似率
def string_similar(s1, s2):
    import difflib
    return difflib.SequenceMatcher(None, s1, s2).quick_ratio()


# 使用api方式调用
def baidu_ocr(image):
    import urllib.parse
    import urllib.request
    import urllib
    # 获取access_token
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=CyIgU1tQyZpd4pRPTyKmRGAK&client_secret=6zt4hme0z7rE7INmuX71erN1v8nMhHEn'
    request = urllib.request.Request(host)
    request.add_header('Content-Type', 'application/json; charset=UTF-8')
    response = urllib.request.urlopen(request)
    res = getjsontext(response)
    access_token=res['access_token']
    data = base64.b64encode(image)
    # print(data)
    params = {"image": data}
    params = urllib.parse.urlencode(params)
    url = 'https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic'
    # url="https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic"
    # url='https://aip.baidubce.com/rest/2.0/ocr/v1/general'
    url=url+"?access_token="+access_token
    req = urllib.request.Request(url, params.encode())
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    # req.add_header(API_KEY, SECRET_KEY)
    resp = urllib.request.urlopen(req)
    content=getjsontext(resp)
    print(content)
    str_list = get_words(content["words_result"])
    return str_list


# 使用SDK方式调用百度ocr：
def sdk_ocr(image):
    from aip import AipOcr
    # 连接ocr
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    results = client.basicGeneral(image)["words_result"]
    str_list = get_words(results)
    return str_list


# 得到通过百度ocr调用的答案
def get_words(results):
    str_list = []
    for result in results:
        text = result["words"]
        str_list.append(text)
    a = ''
    str_list = a.join(str_list)
    print(str_list)
    return str_list

# 与数据库进行匹配
def get_num(str_list):
    # 连接数据库answer
    cn = sqlite3.connect('answer.db')
    # 获取表中内容
    cursor = cn.execute('select * from data')
    max = 0
    cnt1 = cnt = 0
    for (x, y) in cursor.fetchall():
        rate = string_similar(x, str_list)
        if rate >= max:
            # print(y)
            max = rate
            cnt1 = cnt
        cnt = cnt + 1
    print(cnt1)
    cursor.close()
    cn.close()
    return cnt1

# 使用python自带的文字识别进行调用
def pt(image):
    from PIL import Image
    import pytesseract
    text = pytesseract.image_to_string(Image.open(image), lang='chi_sim')
    print(text)
    return text


def sendlink(sock,addr,num):
    print('Accept new connection from %s:%s...' % addr)
    # 连接数据库answer
    cn = sqlite3.connect('answer.db')
    # 获取表中内容
    cursor = cn.execute('select * from data')
    cnt = 0
    for (x, y) in cursor.fetchall():
        if num == cnt:
            # 向客户端发送查询结果
            # print(y.encode())
            sock.send(y.encode())
            sock.close()
            break
        cnt = cnt + 1
    cursor.close()
    cn.close()


def tcplink(sock, addr):
    # 连接数据库answer
    cn = sqlite3.connect('answer.db')
    # 获取表中内容
    cursor = cn.execute('select * from data')
    # 接收数据
    try:
        print('Accept new connection from %s:%s...' % addr)
        receivedData = str(sock.recv(2048))
        print(receivedData)
        entities = receivedData.split("\\r\\n")
        Sec_WebSocket_Key = entities[12].split(":")[1].strip() + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        print(Sec_WebSocket_Key)
        # print("key ", Sec_WebSocket_Key)
        response_key = base64.b64encode(hashlib.sha1(bytes(Sec_WebSocket_Key, encoding="utf8")).digest())
        response_key_str = str(response_key)
        response_key_str = response_key_str[2:30]
        # print(response_key_str)
        response_key_entity = "Sec-WebSocket-Accept: " + response_key_str + "\r\n"
        sock.send(bytes("HTTP/1.1 101 Web Socket Protocol Handshake\r\n", encoding="utf8"))
        sock.send(bytes("Upgrade: websocket\r\n", encoding="utf8"))
        sock.send(bytes(response_key_entity, encoding="utf8"))
        sock.send(bytes("Connection: Upgrade\r\n\r\n", encoding="utf8"))
        print("send the hand shake data")
        buffer = []
        while True:
            data = sock.recv(1024)
            print(data)

            if not data:
                break
            buffer.append(data)
            # print(buffer)
        data = b''.join(buffer)
        print(data)
        sock.close()
        # 通过百度ocr调用得到文字
        str_list=baidu_ocr(data)
        # str_list = sdk_ocr(image)
        # 进行模糊匹配获取题目编号
        num = get_num(str_list)
        # 重新建立连接
        s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s1.bind(('157.230.175.161',port+1))
        # s1.bind(('127.0.0.1', port+1))
        s1.listen(1)
        print("success!")
        sock,addr= s1.accept()
        # 创建新线程来返回答案图片:
        t = threading.Thread(target=sendlink, args=(sock, addr,num))
        t.start()
    except:
        print("error")
        sock.close()

if __name__ == '__main__':
    APP_ID = '15487060'
    API_KEY = 'CyIgU1tQyZpd4pRPTyKmRGAK'
    SECRET_KEY = '6zt4hme0z7rE7INmuX71erN1v8nMhHEn'


    # 采用tcp协议
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port=1243
    s.bind(('157.230.175.161',port))
    # s.bind(('127.0.0.1', port))
    print(port)
    # 允许等待连接的最大数量
    s.listen(6)
    print("success!")
    while True:
        # 接受一个新连接:
        sock, addr = s.accept()
        print(addr)
        # 创建新线程来处理TCP连接:
        t = threading.Thread(target=tcplink, args=(sock, addr))
        t.start()
