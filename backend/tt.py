from backend.utils.clients import Client
from backend.config import BASE_URL, API_KEY,MODEL_NAME


client = Client(model_name=MODEL_NAME, API_KEY=API_KEY, base_url=BASE_URL)
T = "双肺上叶少许慢性炎症可能；双肺散在结节影，主要结节位于（Se3，Im121），考虑Lung-RADS 分级为 3类，建议6个月CT复查。主动脉钙化。"
G = "双肺下叶少许慢性炎症可能；双肺散在结节影，主要结节位于（Se3，Im121），考虑Lung-RADS 分级为 3类，建议6个月CT复查。主动脉钙化。"

input_data = {
    "desc": "this is a test!",
    "answer": T,
    "pred": G
}

result = client.check_modify(input_data)
print(result)