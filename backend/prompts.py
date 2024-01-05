from typing import List, Union

from openai.types.chat import ChatCompletionMessageParam, ChatCompletionContentPartParam

from imported_code_prompts import (
    IMPORTED_CODE_BOOTSTRAP_SYSTEM_PROMPT,
    IMPORTED_CODE_IONIC_TAILWIND_SYSTEM_PROMPT,
    IMPORTED_CODE_REACT_TAILWIND_SYSTEM_PROMPT,
    IMPORTED_CODE_TAILWIND_SYSTEM_PROMPT,
    IMPORTED_CODE_SVG_SYSTEM_PROMPT,
)
from screenshot_system_prompts import (
    BOOTSTRAP_SYSTEM_PROMPT,
    IONIC_TAILWIND_SYSTEM_PROMPT,
    REACT_TAILWIND_SYSTEM_PROMPT,
    TAILWIND_SYSTEM_PROMPT,
    SVG_SYSTEM_PROMPT,
    TEST_BASIC_SYSTEM_PROMPT,
    TEST_BASIC_HTML_SYSTEM_PROMPT,
)


USER_PROMPT = """
Generate code for a web page that looks exactly like this.
"""

USER_PROMPT_D0 = """
Generate code for a web page that looks exactly like this.
The text needed to put in the page is: " {\n  "prodName": "JC35W2",\n  "prodBrief": "浙江捷昌线性驱动 科技股份有限公司专业生产销售JC35W2, JC35W2, 医疗床, 护理床。JC35W2价格低廉，质量上乘，欢迎新老客户咨询。",\n  "productKeyword": "JC35W2,医疗床,护理 床,Jiecang电动推杆,移位器",\n  "productCategory": "医疗康护",\n  "ProductFeatures": "最大负载：3000N，防护等级：IPX4",\n  "prodAttribute": "负载推力：3000N、2000N、1000N负载拉力：3000N、2000N、1000N颜色：银灰色防护等级：IPX4行程长度：3000N：50-250mm（幅度为4mm）2000N：50-400mm（幅度为4mm）1000N ：50-400mm（幅度为4mm）安装尺寸：L=170（S≤50）L=S+120（50＜S≤400）噪音水平：≤48dB（环境噪音≤40dB）双霍尔反馈：可选内置电子限位开关重量：约1.7kg（不 同行程/安装距，重量存在差异）静态弯矩：不予许侧向负载",\n  "productText": "JC35W2 · 最大负载：3000N · 防护等级：IPX4 状态： 询价 产品描述 产品规格书 2D/3D 负载推力：3000N、2000N、1000N负载拉力：3000N、2000N、1000N颜色：银 灰色防护等级：IPX4行程长度：3000N：50-250mm（幅度为4mm）2000N：50-400mm（ 幅度为4mm）1000N：50-400mm（幅度为4mm）安装尺寸：L=170（S≤50）L=S+120（50 ＜S≤400）噪音水平：≤48dB（环境噪音≤40dB）双霍尔反馈：可选内置电子限位开关 重量：约1.7kg（不同行程/安装距，重量存在差异）静态弯矩：不予许侧向负载",\n  "prodImg": ""\n}"
put the text above in proper place. You may also need to use some text in the image.
"""

SVG_USER_PROMPT = """
Generate code for a web page that looks exactly like this.
"""


def assemble_imported_code_prompt(
    code: str, stack: str, result_image_data_url: Union[str, None] = None
) -> List[ChatCompletionMessageParam]:
    system_content = IMPORTED_CODE_TAILWIND_SYSTEM_PROMPT
    if stack == "html_tailwind":
        system_content = IMPORTED_CODE_TAILWIND_SYSTEM_PROMPT
    elif stack == "react_tailwind":
        system_content = IMPORTED_CODE_REACT_TAILWIND_SYSTEM_PROMPT
    elif stack == "bootstrap":
        system_content = IMPORTED_CODE_BOOTSTRAP_SYSTEM_PROMPT
    elif stack == "ionic_tailwind":
        system_content = IMPORTED_CODE_IONIC_TAILWIND_SYSTEM_PROMPT
    elif stack == "svg":
        system_content = IMPORTED_CODE_SVG_SYSTEM_PROMPT
    else:
        raise Exception("Code config is not one of available options")

    user_content = (
        "Here is the code of the app: " + code
        if stack != "svg"
        else "Here is the code of the SVG: " + code
    )
    return [
        {
            "role": "system",
            "content": system_content,
        },
        {
            "role": "user",
            "content": user_content,
        },
    ]
    # TODO: Use result_image_data_url


def assemble_prompt(
    image_data_url: str,
    generated_code_config: str,
    result_image_data_url: Union[str, None] = None,
) -> List[ChatCompletionMessageParam]:
    # Set the system prompt based on the output settings
    system_content = TAILWIND_SYSTEM_PROMPT
    if generated_code_config == "html_tailwind":
        system_content = TAILWIND_SYSTEM_PROMPT
    elif generated_code_config == "react_tailwind":
        system_content = REACT_TAILWIND_SYSTEM_PROMPT
    elif generated_code_config == "bootstrap":
        system_content = BOOTSTRAP_SYSTEM_PROMPT
    elif generated_code_config == "ionic_tailwind":
        system_content = IONIC_TAILWIND_SYSTEM_PROMPT
    elif generated_code_config == "svg":
        system_content = SVG_SYSTEM_PROMPT
    elif generated_code_config == "test_basic":
        system_content = TEST_BASIC_SYSTEM_PROMPT
    elif generated_code_config == "test_basic_html":
        system_content = TEST_BASIC_HTML_SYSTEM_PROMPT
    else:
        raise Exception("Code config is not one of available options")

    user_prompt = USER_PROMPT if generated_code_config != "svg" else SVG_USER_PROMPT

    user_content: List[ChatCompletionContentPartParam] = [
        {
            "type": "image_url",
            "image_url": {"url": image_data_url, "detail": "high"},
        },
        {
            "type": "text",
            "text": user_prompt,
        },
    ]

    # Include the result image if it exists
    if result_image_data_url:
        user_content.insert(
            1,
            {
                "type": "image_url",
                "image_url": {"url": result_image_data_url, "detail": "high"},
            },
        )
    return [
        {
            "role": "system",
            "content": system_content,
        },
        {
            "role": "user",
            "content": user_content,
        },
    ]
