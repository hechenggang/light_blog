#coding=utf-8
import time
import hashlib

# 将字符串进行 md5 编码,或者返回时间戳的 md5 编码
def string_to_md5(string=None,mix=False):
    if not string:
        string=time.time()
    string = str(string)
    if mix:
        srting = str(time.time()) + string
    return hashlib.md5(string.encode(encoding='UTF-8')).hexdigest()