import os
from openai import OpenAI
import re
import json
from typing import Optional, List, Mapping, Any
import regex
import pandas as pd
SYSTEM_PROMPT = """
    【任务说明】
    根据生成诊断（G）和真实诊断（T）对比，仅修改错误类型，以T为标准对G进行修改:
    -方位词错误（如左右、上下）
    -器官词不对应（如肺/肾）
    -术语不完全一致（允许同义词）
    【核心要求】
    若发现上述三类错误之一，请在**真实诊断（T）中定位到错误位置，并用 [ ] 明确标注出错误词语的整段内容**，其余内容保持不变。

    
    【输出要求】
    1. 格式：严格输出JSON，包含以下字段：
    - 是否修改（"是"或"否"）
    - 修改建议（若无需修改则填"无"）
    - 分析过程（需明确错误位置及修改依据）
    - 标注后的真实诊断：：在真实诊断中用 `[ ]` 标注出错误部分，其余内容保持不变
    2. 示例：
    {
    "是否修改": "是"/"否",
    "错误类型":"方位词错误"/"无",
    "修改建议": "建议将真实诊断中“左肺下叶”修改为“右肺下叶”",
    "分析过程": "生成诊断中病灶位于右肺下叶，而真实诊断误写为左肺下叶，方位词需对齐"
    "标注后的真实诊断":"[左肺上叶少许慢性炎症可能]；双肺散在结节影，主要结节位于（Se3，Im121），考虑Lung-RADS 分级为 3类，建议6个月CT复查。主动脉钙化"
    }


    【输入格式】
    问：生成诊断(G): {G诊断内容}
    真实诊断(T): {T诊断内容}
    答：
    """
SYSTEM_PROMPT_DESC = """
你作为医学影像学质控专家，需按严格标准判断是否接受改写描述（M），规则如下：

【错误分级】
▶ Ⅲ类（可接受修正）
  - 笔误：重复/缺失字符（如"淋巴巴结→淋巴结"）
  - 同音错别字（如"伪影干扰→伪影感染"）
▶ 非Ⅲ类（拒绝修正）
  - 术语替换（如"支气管血管束→支气管隔缘束"）
  - 描述方式变更（如"未见增大→未见扩大"）
  - 新增错误（如将正确表述改错）

【评估守则】
1. 双重验证机制：
   - 检查M是否修正了T中的Ⅲ类错误
   - 确认M自身未引入新错误（含Ⅲ类与非Ⅲ类）

2. 接受条件（同时满足）：
   a) M正确修正T中的Ⅲ类错误
   b) M未添加新错误
   c) M未进行非Ⅲ类修改

3. 拒绝条件（满足任一）：
   a) M将正确术语改错（即使修正其他错误）
   b) 包含非Ⅲ类修改
   c) 修正后的描述出现新错误

【输出规范】
{
  "是否修改": "是/否",
  "错误类型": "Ⅲ类/非Ⅲ类/混合型/无",
  "修改建议": "具体修改项"/"原词→建议词"/"无",
  "分析过程": "分点说明每个差异点的错误类型及处理依据(以字符串的形式给出)"
}

【关键示例】
▶ 示例1（应拒绝）：
T："纵隔内未见明显肿大淋巴结"
M："纵隔内未见明显肿大淋巴巴结"
分析：
- M将正确"淋巴结"改错为"淋巴巴结"（新增Ⅲ类错误）
- 即使其他修改正确也须拒绝

▶ 示例2（应拒绝）：
T："支气管血管束走行正常"
M："支气管隔缘束走行正常"
分析：
- "隔缘束"为错误术语（Ⅱ类错误）
- 该修改破坏描述准确性

【输入格式】
问：改写描述(M): {M_content}
真实描述(T): {T_content}
答：
"""


def extract_json_from_text(text: str) -> Optional[dict]:
    try:
        json_pattern = r'\{.*?"是否修改":\s*"[^"]+",.*?"错误类型":\s*"[^"]+",.*?"修改建议":\s*"[^"]*",.*?"分析过程":\s*"[^"]*",.*?"标注后的真实诊断":\s*"[^"]*"\s*\}'
        match = regex.search(json_pattern, text, flags=regex.DOTALL)
        return json.loads(match.group()) if match else None
    except Exception:
        return None


def validate_json(data: dict) -> bool:
    required = {"是否修改", "错误类型", "修改建议", "分析过程","标注后的真实诊断"}
    return all(k in data for k in required)


def batch_write_to_excel(entries_list: List[dict], output_path) -> None:
    try:
        df = pd.DataFrame(entries_list)
        df.to_excel(output_path, index=False, engine='openpyxl')
        print(f"成功写入{len(df)}条记录")
    except Exception as e:
        print(f"写入失败：{str(e)}")


class Client:
    def __init__(self, model_name, API_KEY, base_url):
        self.SYSTEM_PROMPT = SYSTEM_PROMPT
        self.model_name = model_name
        self.client = OpenAI(
            api_key=API_KEY,
            base_url=base_url,
        )
    def generate(self, input_dat) -> str:
        messages = [{"role": "user", "content": input_dat}]
        return self.client.chat.completions.create(messages=messages, model=self.model_name).choices[0].message.content

    def check_desc_modify(self, input_data):
        json_data = ""
        count = 0
        flag = False
        modify = 'M:' + input_data['gen_desc']
        true = 'T:' + input_data['desc']
        messages = [{"role": "system", "content": SYSTEM_PROMPT_DESC}, {"role": "user", "content": modify},
                    {"role": "user", "content": true}]
        try:
            while not flag and count < 3:
                result = self.client.chat.completions.create(messages=messages, model="deepseek-chat")
                json_data = extract_json_from_text(result.choices[0].message.content)
                print(json_data)
                if json_data == None:
                    print(result.choices[0].message.content)
                    count += 1
                    continue
                flag = validate_json(json_data)
                count += 1
        except Exception as e:
            print(e)
        if count == 3:
            return False
        return json_data

    def check_modify(self, input_data) -> json:
        json_data = ""
        count = 0
        flag = False

        ## 检查描述是否错误并修改
        # is_desc_modify = self.check_desc_modify(input_data)
        # if not is_desc_modify and is_desc_modify['是否修改'] == '是':
        #     is_desc_modify["影像描述"] = input_data["desc"]
        #     is_desc_modify["影像诊断"] = input_data["answer"]
        #     return json.dumps(is_desc_modify, indent=4, ensure_ascii=False)

        answer = 'T:' + input_data['answer']
        pred = 'G:' + input_data['pred']
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}, {"role": "user", "content": answer},
                    {"role": "user", "content": pred}]
        try:
            while not flag and count < 3:
                result = self.client.chat.completions.create(messages=messages, model="deepseek-chat")
                json_data = extract_json_from_text(result.choices[0].message.content)
                print(json_data)
                if  json_data == None:
                    print(result.choices[0].message.content)
                    count += 1
                    continue
                flag = validate_json(json_data)
                count += 1
        except Exception as e:
            print(e)
        if count == 3:
            return False
        json_data["影像描述"] = input_data["desc"]
        json_data["生成诊断"] = input_data['pred']

        return json.dumps(json_data, indent=4, ensure_ascii=False)


class LocalClient:
    def __init__(self, model_name, API_KEY, base_url):
        self.SYSTEM_PROMPT = None,
        self.model_name = model_name
        self.client = OpenAI(
            api_key=API_KEY,
            base_url=base_url,
        )

    def generate(self, input_dat) -> str:
        messages = [{"role": "user", "content": input_dat}]
        return self.client.chat.completions.create(messages=messages, model=self.model_name).choices[0].message.content

