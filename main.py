#!/usr/bin/ruby
# -*- coding : utf-8 -*-
# author：samge
# data：2023-02-28 14:56
# describe：
import os

from fastapi import Depends, FastAPI, Header

from models.m_openai import OpenaiCalculRequest
from utils import u_http, u_file, u_openai_calcul

# api的简易token验证
access_token = os.environ.get('ACCESS_TOKEN') or eval(u_file.read('config.json')).get('access_token')


async def verify_token(Authorization: str = Header(...)):
    """ token简易验证 """
    if Authorization != f"Bearer {access_token}":
        print(f"认证失败：{Authorization}")
        u_http.fail403(msg='Authorization header invalid')


def check_api_type(font_from) -> bool:
    """检查类型"""
    return True


app = FastAPI(dependencies=[Depends(verify_token)])


@app.post("/openai/calcul")
async def openai_calcul(request: OpenaiCalculRequest):
    if request.max_length > 0:  # 如果该值大于0，则忽略prompt的值
        price_all, result_info = u_openai_calcul.get_tokens_price_by_length(
            max_length=request.max_length,
            model_key=request.model_name,
            context_type=request.context_type,
            exchange_rate=request.exchange_rate
        )
    else:
        price_all, result_info = u_openai_calcul.get_tokens_price(
            prompt=request.prompt,
            result=request.result,
            model_key=request.model_name,
            context_type=request.context_type,
            exchange_rate=request.exchange_rate
        )
    return u_http.success({
        "price_all": price_all,
        "result_info": result_info
    })
