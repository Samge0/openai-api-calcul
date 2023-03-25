#!/usr/bin/env python3
# -*- coding : utf-8 -*-
# author：samge
# data：2023-03-24 13:01
# describe：
import enum
import math

import tiktoken

from utils import u_dict

"""
openai计费工具类 - 基于tiktoken
github地址：https://github.com/openai/tiktoken/blob/main/README.md

官方计费模拟：https://platform.openai.com/tokenizer
官方计费介绍：https://openai.com/pricing
"""


class ContextType(enum.Enum):
    """
    gpt4 上下文size
    """
    default = "default"
    k8 = "8K"
    k32 = "32K"


class ModelName(enum.Enum):
    """
    tiktoken 计算的模型名称
    """
    gpt2 = "gpt2"
    gpt3 = "gpt-3.5-turbo"  # gpt-3.5-turbo
    gpt4 = "gpt-4"  # gpt-4 / cl100k_base


# 价格字典
price_config = {
    "gpt2": {
        "default": {
            "prompt": 0.002,
            "result": 0.002
        },
        "cn_ratio": 2
    },
    "gpt3": {
        "default": {
            "prompt": 0.002,
            "result": 0.002
        },
        "cn_ratio": 1.3
    },
    "gpt4": {
        "default": {
            "prompt": 0.03,
            "result": 0.06
        },
        "8K": {
            "prompt": 0.03,
            "result": 0.06
        },
        "32K": {
            "prompt": 0.06,
            "result": 0.12
        },
        "cn_ratio": 1.3
    }
}


def _round_price(price) -> float:
    """
    保留8位小数金额

    :param price: 价格
    :return:
    """
    return round(price, 8)


def generate_all_price_info(price_all, prompt_info, result_info, exchange_rate):
    """
    生成总的计费信息

    :param price_all: 总费用
    :param prompt_info: prompt的描述信息
    :param result_info: result的描述信息
    :param exchange_rate: 汇率
    :return:
    """
    body_info = f"{prompt_info}\n\n{result_info}" if prompt_info else result_info
    return f"""
当前汇率：{exchange_rate}
总费用：￥{_round_price(price_all)}，其中：

{body_info}
    """


def generate_price_info(_tokens, _price, _integer_str, _unicode, tag, exchange_rate):
    """
    生成计费信息

    :param _tokens: prompt的tokens数量
    :param _price: prompt的tokens费用
    :param _integer_str: 实际的标记块
    :param _unicode: 转unicode后的标记块
    :param tag: 标签
    :param exchange_rate: 汇率
    :return:
    """
    if _tokens <= 0:
        return ''
    total_price = get_price(_tokens, _price, exchange_rate)
    total_price = _round_price(total_price)
    return f"""
{tag}令牌数：{_tokens}
{tag}价格：${_price} / 1024令牌
{tag}费用：math.ceil({_tokens}/1024) * {_price} * {exchange_rate} = ￥{total_price}

实际的标记块：{_integer_str}

标记块对应的字符：{_unicode}
    """


def generate_info_without_price(prompt_tokens, result_tokens):
    """
    生成信息 - 没有计费

    :param prompt_tokens: prompt的tokens数量
    :param result_tokens: result的tokens数量
    :return:
    """
    return f"""
    该模型暂不做计费，令牌数：
    
    prompt令牌数：{prompt_tokens}
    result令牌数：{result_tokens}
    """


def get_tokens_price_by_length(
        max_length: int,
        model_key: str = ModelName.gpt4.name,
        context_type: str = '8K',
        exchange_rate: float = 7
) -> (float, str):
    """
    计算模拟计费下，指定字数（中文）与模型所需费用

    :param max_length: 最大字数
    :param model_key: 模型名称："gpt-4", "gpt-3.5-turbo", "gpt2", "p50k_base", "cl100k_base"
    :param context_type: 上下文类型（目前只有"gpt-4"需要区分）："8K", "32K"
    :param exchange_rate: 汇率
    :return:
    """
    model_name = ModelName[model_key].value
    cn_ratio = float(u_dict.get_dict_value(price_config, f'{model_key}.cn_ratio') or 2)
    if model_name == ModelName.gpt4.value:
        context_type = context_type or ContextType.k8.value
    else:
        context_type = 'default'
    result_tokens = max_length * cn_ratio
    result_price = float(u_dict.get_dict_value(price_config, f'{model_key}.{context_type}.result'))
    tip = f"当前处于【模拟字数计费模式】，中文令牌转换比例：1中文 ~= {cn_ratio}令牌。"
    price_all = get_price(result_tokens, result_price, exchange_rate)
    result_info = generate_price_info(result_tokens, result_price, tip, tip, "result", exchange_rate)
    return price_all, generate_all_price_info(result_price, '', result_info, exchange_rate)


def get_price(_tokens, _price, exchange_rate: float = 7):
    """
    获取价格
    :param _tokens: 总令牌数
    :param _price: 价格
    :param exchange_rate: 汇率
    :return:
    """
    return math.ceil(_tokens/1024) * _price * exchange_rate


def get_tokens_price(
        prompt: str,
        result: str,
        model_key: str = ModelName.gpt4.name,
        context_type: str = '8K',
        exchange_rate: float = 7
) -> (float, str):
    """
    计算tokens令牌与模型所需费用

    :param prompt: 用户输入的字符串
    :param result: 模型生成的字符串
    :param model_key: 模型名称："gpt-4", "gpt-3.5-turbo", "gpt2", "p50k_base", "cl100k_base"
    :param context_type: 上下文类型（目前只有"gpt-4"需要区分）："8K", "32K"
    :param exchange_rate: 汇率
    :return: (tokens数量, tokens费用)
    """
    model_name = ModelName[model_key].value

    if model_name == ModelName.gpt4.value:
        context_type = context_type or ContextType.k8.value
    else:
        context_type = 'default'

    if model_key not in price_config.keys():
        return 0.0, f"没有该model_key（{model_key}）对应的价格信息，跳过。"

    prompt_tokens, prompt_integer_str, prompt_unicode = get_tokens_info(value=prompt, model=model_name)
    result_tokens, result_integer_str, result_unicode = get_tokens_info(value=result, model=model_name)
    try:
        prompt_price = float(u_dict.get_dict_value(price_config, f'{model_key}.{context_type}.prompt') or 0)
        result_price = float(u_dict.get_dict_value(price_config, f'{model_key}.{context_type}.result') or 0)

        if prompt_price == 0 or result_price == 0:
            return 0.0, f"获取价格失败，请检查参数是否正确：model_key={model_key}, context_type={context_type}"

        price_all = get_price(prompt_tokens, prompt_price, exchange_rate) + get_price(result_tokens, result_price, exchange_rate)
        prompt_info = generate_price_info(prompt_tokens, prompt_price, prompt_integer_str, prompt_unicode, "prompt", exchange_rate)
        result_info = generate_price_info(result_tokens, result_price, result_integer_str, result_unicode, "result", exchange_rate)
        return price_all, generate_all_price_info(price_all, prompt_info, result_info, exchange_rate)
    except Exception as e:
        return 0.0, f"处理异常，请联系开发人员或刷新页面重试: {e}"


def get_tokens_info(value: str, model: str = ModelName.gpt4.value) -> (int, str):
    """
    获取tokens令牌计算

    :param value: 待计算的字符串
    :param model: 模型名："gpt-4", "gpt-3.5-turbo", "gpt2", "p50k_base", "cl100k_base"
    :return: (tokens数量, tokens字符串)
    """
    encoding = tiktoken.encoding_for_model(model)
    token_integers = encoding.encode(value)
    num_tokens = len(token_integers)
    token_bytes = [encoding.decode_single_token_bytes(token) for token in token_integers]
    print(f"{model}: {num_tokens} tokens")
    print(f"token integers: {token_integers}")
    print(f"token bytes: {token_bytes}")
    return num_tokens, str(token_integers), str(token_bytes).replace('b', '')


def __test():
    """测试token计算"""
    print('tokens令牌计算：\n')
    model = ModelName.gpt4.value
    test_words = [
        "我",
        "sameworld",
    ]
    for test_v in test_words:
        num, integer_str, char_str  = get_tokens_info(value=test_v, model=model)
        print(f"{num} => {test_v}")
    print('操作完成')


if __name__ == '__main__':
    __test()