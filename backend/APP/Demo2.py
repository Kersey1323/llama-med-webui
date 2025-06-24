import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
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


# 组合两种方法：先拼音校正，再GPT校正
def combined_corrector(input_text, corrections, user_dict_files, queue):
    # 1. 拼音规则纠错
    first_pass_correction = correct_text_with_pinyin(input_text, corrections, user_dict_files)

    # 2. 使用GPT校正拼音校正后的文本
    def gpt_thread():
        gpt_corrector(first_pass_correction, queue)

    thread = Thread(target=gpt_thread)
    thread.start()


# 计算纠错前后的差异（按词对比）
def get_diff(original, corrected, user_dict_files):
    # 加载自定义词典
    for dict_file in user_dict_files:
        jieba.load_userdict(dict_file)

    # 1. 分词
    original_words = jieba.lcut(original)
    corrected_words = jieba.lcut(corrected)

    diff = []
    i, j = 0, 0
    while i < len(original_words) and j < len(corrected_words):
        if original_words[i] == corrected_words[j]:
            diff.append(('same', original_words[i]))  # 字符相同，不修改
            i += 1
            j += 1
        else:
            diff.append(('diff', corrected_words[j]))  # 字符不同，标红
            i += 1
            j += 1

    # 处理剩余部分（可能是多余或缺失的词）
    while j < len(corrected_words):
        diff.append(('diff', corrected_words[j]))
        j += 1
    while i < len(original_words):
        diff.append(('same', original_words[i]))
        i += 1

    return diff


# 主程序
def main():
    # 初始化主窗口
    root = tk.Tk()
    root.title("智能影像学检错助手 v1.0")
    root.geometry("1000x600")

    # 加载词典文件
    corrections_file = r"D:\workspace\code\python\corrector\APP\corrections.txt"  # 路径根据实际情况调整
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

    # 左上角标题
    title_label = ttk.Label(root, text="智能影像学检错助手 v1.0", font=("Arial", 20))
    title_label.place(x=10, y=10)

    # 加载图片函数
    def load_image(path, max_width, max_height):
        try:
            image = Image.open(path)
            ratio = min(max_width / image.width, max_height / image.height)
            new_size = (int(image.width * ratio), int(image.height * ratio))
            return ImageTk.PhotoImage(image.resize(new_size, Image.Resampling.LANCZOS))
        except Exception as e:
            print(f"加载图片失败: {e}")
            return ImageTk.PhotoImage(Image.new('RGB', (max_width, max_height), color='lightgray'))

    # 图片路径
    image1_path = "img/img_1.png"  # 替换为实际图片路径
    image2_path = "img/img_2.png"  # 替换为实际图片路径

    # 加载图片并保存引用
    root.image1 = load_image(image1_path, 400, 200)
    root.image2 = load_image(image2_path, 400, 200)

    # 显示图片
    image1_label = ttk.Label(root, image=root.image1, text="", compound="center", background="lightgray")
    image1_label.place(x=50, y=50, width=400, height=200)
    image2_label = ttk.Label(root, image=root.image2, text="", compound="center", background="lightgray")
    image2_label.place(x=500, y=50, width=400, height=200)

    # 输入文本框
    input_text = tk.Text(root, height=15, width=45, wrap="word", font=("Arial", 12))
    input_text.place(x=50, y=300)

    # 后端返回文本框（可复制的只读文本框）
    output_text = tk.Text(root, height=15, width=45, wrap="word", font=("Arial", 12))
    output_text.place(x=500, y=300)
    output_text.config(state="disabled")  # 设置为只读

    # 定义队列和定时器
    queue = Queue()
    timer = None

    # 文本更新逻辑
    def process_text():
        input_text_content = input_text.get("1.0", "end-1c")  # 获取输入框内容
        thread = Thread(target=combined_corrector, args=(input_text_content, corrections, user_dict_files, queue))
        thread.start()

        # 检查线程结果
        def check_result():
            if not queue.empty():
                corrected_output = queue.get()
                diff = get_diff(input_text_content, corrected_output, user_dict_files)
                update_output(diff)
            else:
                root.after(100, check_result)

        check_result()

    # 更新输出框内容并高亮显示差异
    def update_output(diff):
        output_text.config(state="normal")  # 允许修改
        output_text.delete("1.0", "end")  # 清空之前的内容

        for diff_type, text in diff:
            if diff_type == 'diff':
                output_text.insert("end", text, "highlight")  # 高亮显示
            else:
                output_text.insert("end", text)  # 正常显示

        output_text.config(state="disabled")  # 设置为只读

    # 键盘事件处理函数
    def on_text_change(event=None):
        nonlocal timer
        if timer is not None:
            root.after_cancel(timer)  # 取消之前的定时器
        timer = root.after(2000, process_text)  # 延迟 2 秒调用文本处理函数

    # 创建标签用于高亮显示不同部分
    output_text.tag_configure("highlight", foreground="red")

    # 绑定键盘事件
    input_text.bind("<KeyRelease>", on_text_change)

    # 主循环
    root.mainloop()


if __name__ == "__main__":
    main()
