# -*- coding: utf-8 -*-


import sqlite3
import base64
#导入答案
def ima():
    #创建photo_database数据库和表
    cn = sqlite3.connect('answer.db')
    cursor = cn.cursor()
    #创建题目和答案表
    cursor.execute('create table data (question text,answer text)')
    for i in range(6):
        i_str = str(i)
        filename = 'D:\py\problem\题'+i_str+'答案.png'
        with open(filename,"rb") as f:
        #将答案图片进行base64编码
            global ls_f
            ls_f = base64.b64encode(f.read()).decode()
        #print(ls_f)
            a=0
            cursor.execute('insert into data values(?,?)',(a,ls_f))
    #检查答案是否保存成功
    cursor = cn.execute('select * from data')
    for(x,y)in cursor.fetchall():
        print(x,y)
    #关闭数据库
    cursor.close()
    cn.commit()
    cn.close()

if __name__ == '__main__':
    ima()