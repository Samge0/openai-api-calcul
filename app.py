#!/usr/bin/env python3
# -*- coding : utf-8 -*-
# author：samge
# data：2023-03-24 17:50
# describe：
import gradio as gr
from utils import u_openai_calcul
from utils.u_openai_calcul import ModelName, ContextType

"""
gradio界面
参考：https://blog.csdn.net/LuohenYJ/article/details/127489768
官方文档：https://github.com/gradio-app/gradio
"""


def handler(result, exchange_rate, max_length, model_name, context_type):
    """
    处理响应事件，返回openai api的计费结果

    :param exchange_rate: 汇率
    :param result: 输入框的值
    :param max_length: 模拟计费的最大长度，如果该值大于0，则忽略prompt的值
    :param model_name: 模型名称
    :param context_type: 上下文类型，gpt4需要
    :return:
    """

    if max_length == 0 and len(result or '') == 0:
        result_info = "【温馨提示】左侧内容跟右侧“模拟字数计费”选项，二者必选其一哦~"
    else:
        if max_length > 0:  # 如果该值大于0，则忽略prompt的值
            price_all, result_info = u_openai_calcul.get_tokens_price_by_length(max_length=max_length, model_key=model_name, context_type=context_type, exchange_rate=exchange_rate)
        else:
            price_all, result_info = u_openai_calcul.get_tokens_price(prompt='', result=result, model_key=model_name, context_type=context_type, exchange_rate=exchange_rate)
    return result_info


with gr.Blocks() as app:
    gr.Markdown("## ChatGPT接口费用计算器")
    with gr.Column():
        with gr.Row():
            with gr.Column(scale=3):
                txt = gr.Textbox(
                    label="模拟计费的文本内容（如果右侧“模拟字数计费”的值大于0，则自动忽略本输入框内容））",
                    placeholder="请输入需要模拟计费的文本内容（或者可以直接留空，使用右侧的“模拟字数计费”）",
                    lines=20
                ).style(show_copy_button=True)
            with gr.Column(scale=1):
                exchange_rate = gr.Slider(0, 20, value=7.0, step=0.2, label="汇率：", interactive=True)
                max_length = gr.Slider(0, 1000 * 10000, value=0, step=1.0, label="模拟字数计费（默认按中文计算）：", interactive=True)
                model_name_dropdown = gr.components.Dropdown(
                    choices=[member.name for member in ModelName],
                    value=ModelName.gpt4.name,
                    label="请选择模型："
                )
                context_type_dropdown = gr.components.Dropdown(
                    choices=[member.value for member in ContextType],
                    value=ContextType.default.value,
                    label="请选择上下文size（仅在gpt-4有效）："
                )
                button = gr.Button("开始计算")
        txt_result = gr.Textbox(
            label="结果展示",
            placeholder="这里展示计算结果",
            lines=12,
            interactive=True
        ).style(show_copy_button=True)
    button.click(handler, [txt, exchange_rate, max_length, model_name_dropdown, context_type_dropdown], outputs=[txt_result])

app.launch(share=False, inbrowser=False, debug=True, server_name="0.0.0.0")
