import jieba
from threading import Thread
from queue import Queue
from pypinyin import lazy_pinyin
from GPT import GPT_API


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


# 拼音规则校正
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
                corrected_word = right
                break
        corrected_words.append(corrected_word)
    return ''.join(corrected_words)


# GPT 校正函数
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
                "只要修改后的文字。"
            )
        }
    ]
    try:
        gpt_output = GPT_API.gpt_api(messages)
        queue.put(gpt_output.strip())  # 将结果放入队列
    except Exception as e:
        queue.put(f"错误: {e}")


# 先拼音校正，再GPT校正
def combined_corrector(input_text, corrections, user_dict_files, queue):
    # 1. 拼音规则纠错
    first_pass_correction = correct_text_with_pinyin(input_text, corrections, user_dict_files)

    # 2. 使用GPT校正拼音校正后的文本
    def gpt_thread():
        gpt_corrector(first_pass_correction, queue)

    thread = Thread(target=gpt_thread)
    thread.start()



def console_main():
    # 加载词典文件
    corrections_file = "corrections.txt"  # 路径根据实际情况调整
    corrections = load_corrections(corrections_file)

    # 自定义词典文件路径（根据实际文件路径调整）
    user_dict_files = [
        "../data/dict/smile医学影像学词库.txt",
        "../data/dict/X光诊断，描述模板.txt",
        "../data/dict/X线诊断模板（放射科模板）.txt",
        "../data/dict/影像学词汇大全.txt",
        "../data/dict/核医学词库.txt",
        "../data/dict/自创词典.txt"
    ]


    input_text = input("请输入待处理的文本：")
    queue = Queue()


    combined_corrector(input_text, corrections, user_dict_files, queue)
    while True:
        if not queue.empty():
            corrected_output = queue.get()
            print(f"纠正后的文本：\n{corrected_output}")
            break


if __name__ == "__main__":
    console_main()
