import json
import queue
from flask import  request, jsonify, Blueprint
from openai import OpenAI
import ollama
import re
# 创建蓝图
medLLM_routes = Blueprint('medLLM_routes', __name__)

# 流式输出的生成函数
def api_generate(text: str):
    print(f'提问：{text}')

    # 自定义 One-shot Prompt 示例，优化后的版本
    one_shot_prompt = """
        你是一个针对中文医学影像科方位词器官词纠错的专家，接下来我会给你两段医学影像描述\n
       以下是生成诊断与真实诊断纠错示例(只需要更正方位词以及器官词，症状或病情不需要更正，无需修改其他医学术语)：\n

       问：生成诊断(A): 右肺下叶背段结节灶，考虑肿瘤性病变可能大，建议：多学科会诊。右肺胸膜处见多发类圆形结节影，考虑多发炎性结节，转移待排。
       真实诊断(T): 1. 左肺下叶富血供结节，周围型肺癌可能性大，不除外肉芽肿性病变。2. 右中叶结节考虑陈旧性或慢性炎症性病变。
       答：建议将T中“左肺下叶富血供结节”修改为“右肺下叶富血供结节”。将错误的方位词或器官词用引号标注出来则为：1. "左"肺下叶富血供结节，周围型肺癌可能性大，不除外肉芽肿性病变。2. 右中叶结节考虑陈旧性或慢性炎症性病变。

       问：生成诊断(A): 左侧外踝及左侧跟骨前上缘骨折，左侧踝关节腔内积液，左侧踝关节周围软组织肿胀。
       真实诊断(T): 右侧内踝及右侧跟骨前上缘撕脱骨折伴左侧踝关节腔内积液、左侧踝关节周围软组织肿胀。
       答：建议将“右侧内踝及右侧跟骨”修改为“左侧外踝及左侧跟骨”。将错误的方位词或器官词用引号标注出来则为："右侧内踝"及"右侧跟骨"前上缘撕脱骨折伴左侧踝关节腔内积液、左侧踝关节周围软组织肿胀。

       问：生成诊断(A): 双肺多发小结节，倾向良性；左肺下叶索条。
       真实诊断(T): 双肾多发小结节，倾向良性；右肺中叶索条。
       答：建议将“双肾多发小结节”修改为“双肺多发小结节”，并将“右肺中叶索条”修改为“左肺下叶索条”。将错误的方位词或器官词用引号标注出来则为：双"肾"多发小结节，倾向良性；"右肺中叶索条"。

       以生成诊断为标准请检查以下真实诊断，找出其中的错误并用引号标出(给出分析过程，最后将(特定的方位词或器官的一字或词以引号引出标注)标注后的真实诊断分别单独列一行(必须确保进行了引号标注!!!标注好的内容以json格式输出,大括号的内容不要换行,"output":""),如果没有方位词以及器官词错误则直接给出原诊断)：
       输入：{} 
    """.format(text)

    # 使用 Ollama 模型生成回答
    stream = ollama.generate(
        stream=True,
        model='qwen2.5:7b',
        prompt=one_shot_prompt
    )

    response_text = ''
    for chunk in stream:
        if not chunk['done']:
            response_text += chunk['response']
        else:
            break


    return response_text



base_url = "http://192.168.123.194:8000/v1"

client = OpenAI(
        api_key="0",
        base_url=base_url,  # Use the IP address of the server
        )

def toJson(text):
    try:
        match = re.search(r'({.*})', text)
        if match:
            json_str = match.group(0)
            parsed_json = json.loads(json_str)  # 将字符串转换为 JSON 对象
            return parsed_json
        else:
            print(text)
            return "无修改"
    except Exception as e:
        return e
@medLLM_routes.route('/process', methods=['POST'])
def process_description():
    try:
        data = request.json
        description = {
            "desc": data.get("desc"),
            "true_report": data.get("true_report"),
        }


        message_content = description['desc']
        messages = [{"role": "user", "content": message_content}]

        # 模拟与 GPT 的对话生成影像报告
        result = client.chat.completions.create(messages=messages, model="test")
        answer_report = result.choices[0].message.content

        # 拼接影像描述和影像诊断
        input_text = 'A:' + answer_report + 'T:' + description['true_report']
        print(result.choices[0].message.content)


        # 调用 api_generate 生成最终报告
        api_generate(text=input_text)
        # 调用 api_generate 生成最终报告
        response_text = api_generate(text=input_text)
        # 正则表达式提取 JSON 内容
        parsed_json = toJson(response_text)

        # 返回处理结果
        return jsonify({"status": "success", "message": "Processed successfully", "generated_report": parsed_json})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


