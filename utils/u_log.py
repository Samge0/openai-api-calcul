#!/usr/bin/ruby
# -*- coding : utf-8 -*-
# author：samge
# data：2023-02-28 17:24
# describe：


# 是否调试模式
IS_DEBUG = False


def i(msg):
    _print(msg)


def _print(msg):
    if not IS_DEBUG:
        return
    print(msg)
