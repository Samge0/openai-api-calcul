#!/usr/bin/ruby
# -*- coding : utf-8 -*-
# author：samge
# data：2023-02-28 15:11
# describe：
from typing import Optional
from pydantic import BaseModel

from utils import u_openai_calcul


class OpenaiCalculRequest(BaseModel):
    """openai的接口计费请求体"""
    prompt: str  # 提问的内容
    result: str  # 回复的内容
    max_length: Optional[int] = 0  # 模拟计费的最大长度，如果该值大于0，则忽略prompt跟result的值
    exchange_rate: Optional[float] = 7.0  # 汇率
    model_name: Optional[str] = u_openai_calcul.ModelName.gpt4.name  # 模型名称
    context_type: Optional[str] = u_openai_calcul.ContextType.k8.name  # 上下文类型，gpt4需要
