#!/usr/bin/env python3
# -*- coding : utf-8 -*-
# author：samge
# data：2023-03-24 16:02
# describe：

"""
字典相关操作工具类，主要可用符号.链式读取字典中的值
"""


def get_dict_value(_dict: dict, key: str):
    """
    获取字典的值，适配了多层级数据读取
    :param _dict: 字典对象
    :param key: 需要提取的key，如果有多层级请用.连接，例如：data.html.text
    :return:
    """
    if not _dict or not key:
        return None
    if '.' not in key:
        return _dict.get(key) or ''
    try:
        for k in key.split('.'):
            _dict = _dict.get(k)
        return _dict
    except Exception as e:
        print(f'get_dict_value异常：{e}')
        return None


def get_dict_lst_first(_dict: dict, key: str):
    """
    获取字典中某个列表的首个值

    :param _dict: 字典对象
    :param key: 需要提取的key，如果有多层级请用.连接，例如：data.html.text
    :return:
    """
    lst = get_dict_value(_dict, key) or []
    if len(lst) == 0:
        return None
    return lst[0]
