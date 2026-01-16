from utils.templates import prompt_step1, prompt_step2, prompt_step3
import json
import re
import requests


class MOE_CLIENT:

    def __init__(self):
        self.url = "http://host.docker.internal:5000/generate/"

    def is_valid_json(self, s: str):
        try:
            cleaned_json_string = re.sub(
                r"^```json\s*|```$", "", s, flags=re.DOTALL
            ).strip()
            json_data = json.loads(cleaned_json_string)  # 尝试解析
            return json_data
        except json.JSONDecodeError:
            return False  # 不是合法的 JSON

    def report_inference(self, des: str) -> str:
        ### step1

        step1_input = prompt_step1.format_prompt(description=des).to_string()

        payload = {
            "model": "qwen",  # 名称随你启动服务设置
            "expert": "report",  # 指定 LoRA 专家
            "prompt": step1_input,
            "temperature": 0,
        }
        response_1 = requests.post(self.url, json=payload).json()["content"]

        print(response_1["assistant"])
        return response_1["assistant"]

    def verify_inference(
        self, diagnosis_conclusion_A: str, diagnosis_conclusion_B: str
    ) -> str:

        step2_input = prompt_step2.format_prompt(
            diagnosis_conclusion_A=diagnosis_conclusion_A,
            diagnosis_conclusion_B=diagnosis_conclusion_B,
        ).to_string()
        payload = {
            "model": "qwen",  # 名称随你启动服务设置
            "expert": "verify",  # 指定 LoRA 专家
            "prompt": step2_input,
            "temperature": 0,
        }
        response_2 = requests.post(self.url, json=payload).json()["content"]

        comparision_result = response_2["assistant"]
        print(comparision_result)
        return comparision_result

    def post_verify_inference(
        self, description: str, step2_output: dict, diagnosis_conclusion_B: str
    ) -> str:

        step3_input_diagnosis_A = step2_output["标注后的真实诊断"]

        step3_input = prompt_step3.format_prompt(
            description=description,
            diagnosis_conclusion_A=step3_input_diagnosis_A,
            diagnosis_conclusion_B=diagnosis_conclusion_B,
        ).to_string()
        payload = {
            "model": "qwen",  # 名称随你启动服务设置
            "expert": "post_verify",  # 指定 LoRA 专家
            "prompt": step3_input,
            "temperature": 0,
        }
        response_3 = requests.post(self.url, json=payload).json()["content"]
        print(response_3["assistant"])
        return response_3["assistant"]

    def __call__(self, description, diagnosis):
        diagnosis_conclusion_B = self.report_inference(description)
        flag = False
        count = 0
        re_pattern = r"^```json\s*|```$"

        while not flag and count < 3:
            print(f"第{count+1}次尝试verify推理")
            verify_response = self.verify_inference(
                diagnosis_conclusion_A=diagnosis,
                diagnosis_conclusion_B=diagnosis_conclusion_B,
            )
            json_data = self.is_valid_json(verify_response)
            if not json_data:
                count += 1
                if count == 3:
                    print("尝试三次失败！")
                    raise Exception("post_verify JOSN解析失败！跳过该条！")
            else:
                flag = False
                count = 0
                verify_json_data = json_data
                break
        if verify_json_data["是否修改"] == "否":
            return {
                "verify_result": verify_json_data,
                "gen_report": diagnosis_conclusion_B,
            }

        while not flag and count < 3:
            print(f"第{count+1}次尝试post_verify推理")
            post_verify_response = self.post_verify_inference(
                description, verify_json_data, diagnosis_conclusion_B
            )
            json_data = self.is_valid_json(post_verify_response)

            if not json_data:
                count += 1
                if count == 3:
                    print("尝试三次失败！")
                    raise Exception("post_verify JOSN解析失败！跳过该条！")
            else:
                flag = False
                count = 0
                post_verify_json_data = json_data
                break
        if post_verify_json_data["纠错合理性"] == "True":
            print("返回verify_result")
            return {
                "verify_result": verify_json_data,
                "gen_report": diagnosis_conclusion_B,
            }
        else:
            post_verify_json_data["是否修改"] = "False"
            return {
                "verify_result": post_verify_json_data,
                "gen_report": diagnosis_conclusion_B,
            }
