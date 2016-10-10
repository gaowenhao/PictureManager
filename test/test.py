# encoding=utf-8
"""
    @author: gaowenhao
    @email: vevz@163.com
    @description: 
"""
import time
import threading


def fib():
    a, b = 0, 1
    while 1:
        yield b
        a, b = b, a + b


def fib_again():
    print('here we go')
    for num in fib():
        print num,
        time.sleep(1)


if __name__ == "__main__":
    cont = 1
    for num in fib():
        print num,
        time.sleep(1)
        cont += 1
        if cont % 8 == 0:
            break
