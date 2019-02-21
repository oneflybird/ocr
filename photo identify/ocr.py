
from aip import AipOcr

if __name__ == '__main__':
    APP_ID = '15487060'
    API_KEY = 'CyIgU1tQyZpd4pRPTyKmRGAK'
    SECRET_KEY = '6zt4hme0z7rE7INmuX71erN1v8nMhHEn'

    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    """ 读取图片 """
    for i in range(6):
        i_str = str(i)
        filename = 'D:\py\problem\题' + i_str + '.png'
        with open(filename, "rb") as f1:
            # 调用通用文字识别, 图片参数为本地图片
            results = client.general(f1.read())["words_result"]
            str_list = []
            for result in results:
                text = result["words"]
                print(str_list)
                str_list.append(text)
                print(str_list)
                print(text)
            a = ''
            print(str_list)
            print(a.join(str_list))
