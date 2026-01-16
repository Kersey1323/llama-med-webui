from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
template_step1 = """
请根据影像描述生成影像诊断
影像描述：```{description}```


"""

template_step2 = """
    【任务说明】
    根据诊断A和诊断B对比，仅修改错误类型，以B和影像描述为标准对A进行修改:
    -方位词错误（如左右、上下）
    -器官词不对应（如肺/肾）
    -术语不完全一致（允许同义词）
    【核心要求】
    若发现上述三类错误之一，请在A中定位到错误位置，并用 [ ] 明确标注出错误词语的整段内容，其余内容保持不变。


    
    【输出要求】
    1. 格式：严格输出JSON，包含以下字段：
    - 是否修改（"是"或"否"）
    - 错误类型
    - 修改建议（若无需修改则填"无"）
    - 分析过程（需明确错误位置及修改依据） 
    - 标注后的真实诊断：：在真实诊断中用 `[ ]` 标注出错误部分，其余内容保持不变

    ```
    诊断A:```{diagnosis_conclusion_A}```
    诊断B:```{diagnosis_conclusion_B}```
    ```
    
"""

template_step3 = """
根据影像诊断A和B的对比，判断诊断A中`[]`标记的术语不一致错误是否合理，并给出最终判断和解释。

并以json格式输出，字段包括：
```输出:
"纠错合理性": "True/False",
"纠错解释": "解释内容"
```

输入
```json：   


"影像描述": ```{description}```
"影像诊断A": ```{diagnosis_conclusion_A}```
"影像诊断B": ```{diagnosis_conclusion_B}```,
```

"""


prompt_step1 = PromptTemplate(
    template=template_step1,
    input_variables=["description"],
)


json_parser = JsonOutputParser()
prompt_step2 = PromptTemplate(
    template=template_step2,
    input_variables=["diagnosis_conclusion_A", "diagnosis_conclusion_B"],
    partial_variables={"format_instructions": json_parser.get_format_instructions()},
)


prompt_step3 = PromptTemplate(
    template=template_step3,
    input_variables=["description", "diagnosis_conclusion_A", "diagnosis_conclusion_B"],
    partial_variables={"format_instructions": json_parser.get_format_instructions()},
)