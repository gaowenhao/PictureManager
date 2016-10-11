# encoding=utf-8
"""
    @author: gaowenhao
    @email: vevz@163.com
    @description: 
"""

import time

if __name__ == "__main__":
    f1 = open("e://MyPicture/4g.iso", 'rb')
    f2 = open("e://MyPicture/4g_copy.iso", 'wb+')
    buffer_size = 1024 * 10
    start = time.time()
    while True:
        data = f1.read(buffer_size)
        if not data:
            break
        f2.write(data)
    f1.close()
    f2.close()
    end = time.time()

    print(end - start)
