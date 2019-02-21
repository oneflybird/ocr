from flask import Flask, render_template, url_for, request, json,jsonify
import sqlite3

app = Flask(__name__)
#设置编码
app.config['JSON_AS_ASCII'] = False

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
    # data = base64.b64encode(image)
    # print(data)
    params = {"image": image}
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


@app.route('/sendDate', methods=['GET', 'POST'])
def form_data():
    # 从request中获取表单请求的参数信息
    base64 = request.form['base64']
    print(base64)
    str_list=baidu_ocr(base64)
    num = get_num(str_list)
    # 连接数据库answer
    cn = sqlite3.connect('answer.db')
    # 获取表中内容
    cursor = cn.execute('select * from data')
    cnt = 0
    for (x, y) in cursor.fetchall():
        if num == cnt:
            # 向客户端发送查询结果
            return jsonify({'value': y})
        cnt = cnt + 1
    cursor.close()
    cn.close()
if __name__ == '__main__':
    app = Flask(__name__)
    app.run(host='0.0.0.0:8080')
