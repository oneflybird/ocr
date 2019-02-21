# 导入socket库:
import socket


if __name__ == '__main__':
    # 创建一个socket:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 建立连接:
    port=1245
    s.connect(('157.230.175.161',port))
    # s.connect(('127.0.0.1', port))
    filename = 'D:\py\problem\题' + '2' + '.png'
    # file_head = struct.pack('128sl',os.stat(filename).st_size)
    with open(filename, "rb") as f1:
        data1=f1.read()
        num=len(data1)
        print(num)
        s.send(data1)
        s.close()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            s.connect(('157.230.175.161', port+1))
            data = s.recv(5000000)
            break
        except:
            pass
    print(data)
    # if result.encode() == data:
    #     print("ok")
    # print(data.decode())
    s.close()
    print(123)