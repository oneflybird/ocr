# -*- coding: utf-8 -*-
# 数据库
import sqlite3
# base64
import base64
# 调用百度ocr
from aip import AipOcr
# 导入问题


def imp():
    # 创建数据库和游标
    cn = sqlite3.connect('answer.db')
    cursor = cn.cursor()
    # 创建表
    cursor.execute('create table data (question text,answer text)')
    # 调用ocr
    APP_ID = '15487060'
    API_KEY = 'CyIgU1tQyZpd4pRPTyKmRGAK'
    SECRET_KEY = '6zt4hme0z7rE7INmuX71erN1v8nMhHEn'
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    # 打开文件
    for i in range(6):
        i_str = str(i)
        filename = 'D:\py\problem\题'+i_str+'.png'
        filename1 = 'D:\py\problem\题' + i_str + '答案.png'
        # 打开题目文件
        # 读取图片
        with open(filename, "rb") as f1:
            # 调用通用文字识别, 图片参数为本地图片
            results = client.general(f1.read())['words_result']
            global str_list
            str_list = []
            for result in results:
                text = result["words"]
                str_list.append(text)
        # 打开答案文件
        with open(filename1, "rb") as f:
            # 将答案图片进行base64编码
            global ls_f
            ls_f = base64.b64encode(f.read()).decode()
        # 添加数据
        a=''
        cursor.execute('insert into data values(?,?)', (a.join(str_list), ls_f))

    #检查题目和答案是否都保存成功
    cursor = cn.execute('select * from data')
    for(x,y)in cursor.fetchall():
        print(x,y)

    #关闭数据库
    cursor.close()
    cn.commit()
    cn.close()


if __name__ == '__main__':
    # 建立数据库
    imp()
