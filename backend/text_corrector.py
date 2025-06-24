from flask import Flask, request, jsonify, Blueprint
import jieba
from threading import Thread
from queue import Queue
from pypinyin import lazy_pinyin
from GPT import GPT_API
from flask_cors import CORS

corrector_routes = Blueprint('corrector_routes', __name__)

# 加载词典文件
def load_corrections(file_path):
    corrections = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            wrong, right = line.strip().split(',')
            corrections[wrong] = right
    return corrections

# 获取一个词的拼音
def get_pinyin(word):
    return ''.join(lazy_pinyin(word))

# 拼音规则校正，并在校正部分添加引号
def correct_text_with_pinyin(text, corrections, user_dict_files):
    # 加载自定义词典
    for dict_file in user_dict_files:
        jieba.load_userdict(dict_file)

    words = jieba.lcut(text)
    corrected_words = []
    for word in words:
        word_pinyin = get_pinyin(word)
        corrected_word = word  # 默认不修改
        for wrong, right in corrections.items():
            if get_pinyin(wrong) == word_pinyin:  # 拼音匹配
                corrected_word = f'"{right}"'  # 将修改的部分加上引号
                break
        corrected_words.append(corrected_word)
    return ''.join(corrected_words)

# GPT 校正函数，确保校正的部分用引号标注
def gpt_corrector(input_text, queue):
    seg_list = jieba.cut(input_text, cut_all=False)
    messages = [
        {
            'role': 'user',
            'content': (
                "你是一个针对中文医学影像科多字少字错别字纠错机器人，接下来，我会给你一段文字，加一段用jieba分词后的一段字符串，"
                "请你结合分词和语义去解决文本中的多字少字错别字问题。\n"
                f"原文字：{input_text}\n"
                f"jieba分词：{'/'.join(seg_list)}\n"
                "请你直接告诉我修改后的文字，只根据我给你的那一段文字去修改，要在原文字的基础上改，不要自己去加，不要改变顺序。"
                "只要修改后的文字。"            )
        }
    ]
    try:
        gpt_output = GPT_API.gpt_api(messages)
        corrected_output = gpt_output.strip()

        # 确保GPT校正部分也用引号标注
        if corrected_output != input_text:
            corrected_output = ''.join([word if word != input_text else word for word in corrected_output.split()])

        queue.put(corrected_output)  # 将结果放入队列
    except Exception as e:
        queue.put(f"错误: {e}")

# 先拼音校正，再GPT校正
def combined_corrector(input_text, corrections, user_dict_files, queue):
    # 1. 拼音规则纠错
    first_pass_correction = correct_text_with_pinyin(input_text, corrections, user_dict_files)
    print(first_pass_correction)
    # 2. 使用GPT校正拼音校正后的文本
    def gpt_thread():
        gpt_corrector(first_pass_correction, queue)

    thread = Thread(target=gpt_thread)
    thread.start()


@corrector_routes.route('/correct_text', methods=['POST'])
def correct_text():
    try:
        # 接收前端传来的文本和文件路径
        corrections_file = 'APP/corrections.txt'
        data = request.json
        input_text = data.get("text")
        user_dict_files = [
            "./data/dict/smile医学影像学词库.txt",
            "./data/dict/X光诊断，描述模板.txt",
            "./data/dict/X线诊断模板（放射科模板）.txt",
            "./data/dict/影像学词汇大全.txt",
            "./data/dict/核医学词库.txt",
            "./data/dict/自创词典.txt"
        ]

        if not input_text:
            return jsonify({"status": "error", "message": "No input text provided"}), 400

        if not user_dict_files:
            return jsonify({"status": "error", "message": "No corrections file provided"}), 400

        # 加载拼音纠正词典
        corrections = load_corrections(corrections_file)

        # 使用队列接收最终的GPT校正结果
        queue = Queue()

        # 进行拼音校正和GPT校正
        combined_corrector(input_text, corrections, user_dict_files, queue)

        # 等待结果返回
        while True:
            if not queue.empty():
                corrected_output = queue.get()
                print(corrected_output)
                return jsonify({"status": "success", "corrected_text": corrected_output})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
