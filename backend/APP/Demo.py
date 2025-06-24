import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import jieba
from threading import Thread
from queue import Queue
from GPT import GPT_API

jieba.load_userdict("../data/dict/smile医学影像学词库.txt")
jieba.load_userdict("../data/dict/X光诊断，描述模板.txt")
jieba.load_userdict("../data/dict/X线诊断模板（放射科模板）.txt")
jieba.load_userdict("../data/dict/影像学词汇大全.txt")
jieba.load_userdict("../data/dict/核医学词库.txt")
jieba.load_userdict("../data/dict/自创词典.txt")


# 主程序函数
def main():
    # 初始化主窗口
    root = tk.Tk()
    root.title("智能影像学检错助手 v1.0")
    root.geometry("1000x600")

    # 左上角标题
    title_label = ttk.Label(root, text="智能影像学检错助手 v1.0", font=("Arial", 20))
    title_label.place(x=10, y=10)

    # 模拟后端处理函数
    def corrector(input_text, queue):
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
        thread = Thread(target=corrector, args=(input_text_content, queue))
        thread.start()

        # 检查线程结果
        def check_result():
            if not queue.empty():
                corrected_output = queue.get()
                update_output(corrected_output)
            else:
                root.after(100, check_result)

        check_result()

    # 更新输出框内容
    def update_output(corrected_output):
        output_text.config(state="normal")  # 允许修改
        output_text.delete("1.0", "end")  # 清空之前的内容

        # 遍历输出文字
        for i, output_char in enumerate(corrected_output):
            # 计算原文字的上下文范围（上下5个字）
            input_text_content = input_text.get("1.0", "end-1c")
            start = max(0, i - 5)
            end = min(len(input_text_content), i + 5)
            surrounding_text = input_text_content[start:end]

            # 判断是否在原文字上下5个字范围内存在此字符
            if output_char not in surrounding_text:
                output_text.insert("end", output_char, "highlight")  # 高亮显示
            else:
                output_text.insert("end", output_char)  # 正常显示

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
