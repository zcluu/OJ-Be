#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import time


def get_file_md5(file_name):
    """
    计算文件的md5
    :param file_name:
    :return:
    """
    m = hashlib.md5()  # 创建md5对象
    with open(file_name, 'rb') as fobj:
        while True:
            data = fobj.read(4096)
            if not data:
                break
            m.update(data)  # 更新md5对象

    return m.hexdigest()  # 返回md5对象


def get_str_md5(content):
    """
    计算字符串md5
    :param content:
    :return:
    """
    m = hashlib.md5(content)  # 创建md5对象
    return m.hexdigest()


