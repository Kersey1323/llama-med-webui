import jieba
import math
from multiprocessing import Pool, cpu_count
from functools import partial
from Levenshtein import ratio as levenshtein_ratio
import json
import re


DICT_PATH = "C:/Users/49270/Desktop/llama_med_webui/backend/utils/old_and_1234.txt"


def split_medical_text(text):
    """医学文本智能分句（支持嵌套标点处理）"""
    # 使用正则表达式匹配中文标点（，；。）作为分隔符
    # 使用正向预查保留可能存在的嵌套结构（如括号内的标点）
    split_pattern = r'([，；。])'

    # 执行分割并保留标点符号
    segments = re.split(split_pattern, text)

    # 合并标点与内容（处理医学报告中的特殊格式）
    processed_segments = []
    buffer = ''
    for s in segments:
        if s in ['，', '；', '。']:
            if buffer:
                processed_segments.append(buffer)
                buffer = ''
            processed_segments.append(s)
        else:
            buffer += s
    if buffer:
        processed_segments.append(buffer)

    # 生成带标点的分句结果（符合医学报告阅读习惯）
    sentences = []
    current_sentence = ''
    for seg in processed_segments:
        current_sentence += seg
        if seg in ['，', '；', '。']:
            sentences.append(current_sentence.strip())
            current_sentence = ''

    return sentences

def print_pretty_json(data):
    """格式化打印JSON数据（带中文支持）"""
    formatted_json = json.dumps(
        data,
        indent=4,
        ensure_ascii=False,  # 禁用ASCII转义以显示中文
        sort_keys=False      # 保持字典原有键顺序
    )
    # print("\n实体关系可视化：")
    # print(formatted_json)
    # print("-" * 60)

def build_pinyin_index():
    """构建拼音-词汇倒排索引，并添加长度索引"""
    pinyin_index = {}
    length_index = defaultdict(list)  # {拼音长度: [对应拼音列表]}

    with open(DICT_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            word = line.strip()
            if word:
                key = ''.join(lazy_pinyin(word, style=Style.NORMAL))
                if key not in pinyin_index:
                    pinyin_index[key] = []
                pinyin_index[key].append(word)
                length_index[len(key)].append(key)

    return pinyin_index, length_index


# 单词语处理函数（供并行化使用）
def process_word(args, similarity_threshold=0.8):
    """处理单个词的相似拼音查找"""
    word, pinyin_index, length_index = args
    original_pinyin = ''.join(lazy_pinyin(word, style=Style.NORMAL))
    original_len = len(original_pinyin)

    # 根据相似度阈值计算长度范围
    max_edit_distance = math.floor((1 - similarity_threshold) * original_len)
    min_length = max(1, original_len - max_edit_distance)
    max_length = original_len + max_edit_distance

    # 生成候选长度范围
    candidate_lengths = list(range(min_length, max_length + 1))

    candidates = []
    # 遍历所有可能长度的拼音
    for length in candidate_lengths:
        for target_pinyin in length_index.get(length, []):
            # 计算相似度
            similarity = levenshtein_ratio(original_pinyin, target_pinyin)

            if similarity >= similarity_threshold:
                candidates.extend(pinyin_index.get(target_pinyin, []))

    # 去重并排序（优先首字母匹配，再按词长倒序）
    unique_candidates = sorted(
        list(set(candidates)),
        key=lambda x: (x[0] != word[0], -len(x))
    )

    return (word, unique_candidates)


def query_engine(seg_list, pinyin_index):
    """查询引擎"""
    do_not_exit_words = []
    for word in seg_list:
        if word in {'。', '，', '、', '：'}:
            continue

        # 生成查询键
        key = ''.join(lazy_pinyin(word, style=Style.NORMAL))
        # 执行查询
        results = pinyin_index.get(key, None)
        # 输出结果
        if results:
            if word not in results:
                do_not_exit_words.append(word)

            continue
        else:
            do_not_exit_words.append(word)

    return do_not_exit_words


def participle(text):
    jieba.load_userdict(DICT_PATH)
    seg_generator = jieba.cut(text, cut_all=True)
    seg_list = list(seg_generator)
    # print("Full Mode: " + "/ ".join(seg_list))  # 全模式
    return seg_list


def keyword_typo(do_not_exit_words, pinyin_index):
    """键盘误触智能纠错引擎"""
    # 构建专业医学键盘映射表（基于放射科工作站常见布局优化）
    KEYBOARD_PROXIMITY = {
        'A': ['Q', 'W', 'S', 'X', 'Z'],
        'B': ['V', 'F', 'G', 'H', 'N'],
        'C': ['X', 'S', 'D', 'F', 'V'],
        'D': ['W', 'E', 'R', 'F', 'C', 'X', 'S'],
        'E': ['R', 'F', 'D', 'S', 'W'],
        'F': ['E', 'R', 'T', 'G', 'B', 'V', 'C', 'D'],
        'G': ['R', 'T', 'Y', 'H', 'N', 'B', 'F'],
        'H': ['T', 'Y', 'U', 'J', 'M', 'N', 'G', 'B'],
        'I': ['O', 'L', 'K', 'J', 'U', 'Y'],
        'J': ['Y', 'U', 'I', 'K', 'M', 'N', 'H'],
        'K': ['U', 'I', 'O', 'L', 'J', 'M'],
        'L': ['I', 'O', 'P', 'K'],
        'M': ['N', 'H', 'J', 'K'],
        'N': ['B', 'G', 'H', 'J', 'M'],
        'O': ['P', 'L', 'K', 'I'],
        'P': ['O', 'L'],
        'Q': ['W', 'A', 'S'],
        'R': ['T', 'F', 'D', 'E'],
        'S': ['W', 'E', 'D', 'X', 'A', 'Z', 'C'],
        'T': ['Y', 'G', 'F', 'R'],
        'U': ['Y', 'I', 'J', 'H', 'K'],
        'V': ['C', 'D', 'F', 'B'],
        'W': ['E', 'S', 'A', 'Q'],
        'X': ['S', 'D', 'C', 'Z'],
        'Y': ['T', 'U', 'H', 'G'],
        'Z': ['A', 'S', 'X']
    }

    typo_suggestions = {}

    for word in do_not_exit_words:
        original_pinyin = ''.join(lazy_pinyin(word, style=Style.NORMAL))
        if len(original_pinyin) < 1:
            typo_suggestions[word] = []
            continue

        candidate_pinyins = set()

        # 生成三级候选拼音（优先首字母，再核心韵母）
        for pos in range(len(original_pinyin)):
            current_char = original_pinyin[pos]
            neighbors = KEYBOARD_PROXIMITY.get(current_char.upper(), [])

            # 特殊处理医学常见误触组合
            for replace_char in neighbors:
                # 构建新拼音时保持长度一致
                new_pinyin = (
                        original_pinyin[:pos] +
                        replace_char.lower() +
                        original_pinyin[pos + 1:]
                )
                candidate_pinyins.add(new_pinyin)

        # 多维度候选词筛选
        suggestions = []
        for cp in candidate_pinyins:
            # 获取索引词并过滤多音字自身
            candidates = [
                w for w in pinyin_index.get(cp, [])
                if w != word and len(w) == len(word)
            ]
            suggestions.extend(candidates)

        # 智能排序策略：优先首字母错误，再按词频排序
        unique_suggestions = sorted(
            list(set(suggestions)),
            key=lambda x: (
                x[0] != word[0],  # 首字母不同的优先
                -len(x)  # 长度相同的优先
            )
        )

        typo_suggestions[word] = unique_suggestions
        # if unique_suggestions:
        #     print(f"▌潜在错误词：{word}（{original_pinyin}）")
        #     print(f"▌建议候选：{' | '.join(unique_suggestions)}")
        #     print(f"─── 基于{len(candidate_pinyins)}种拼音变体分析 ───\n")

    return typo_suggestions


def not_familiar(do_not_exit_words, pinyin_index):
    """处理因平卷舌或前后鼻音错误导致的未识别词"""
    # 定义替换规则（长模式优先）
    replace_rules = [
        # 平卷舌错误规则（长模式在前）
        ('ch', 'c'),
        ('zh', 'z'),
        ('sh', 's'),
        # 前后鼻音错误规则（长模式在前）
        ('ang', 'an'),
        ('eng', 'en'),
        ('ing', 'in'),
        # 平卷舌错误规则（短模式在后）
        ('c', 'ch'),
        ('z', 'zh'),
        ('s', 'sh'),
        # 前后鼻音错误规则（短模式在后）
        ('an', 'ang'),
        ('en', 'eng'),
        ('in', 'ing'),
    ]

    pron_suggestions = {}  # 存储结果 {词: [候选建议]}

    for word in do_not_exit_words:
        original_pinyin = ''.join(lazy_pinyin(word, style=Style.NORMAL))
        pron_suggestions[word] = []  # 初始化条目

        if not original_pinyin:
            continue

        variant_pinyins = set()

        # 生成所有可能的拼音变体
        for origin, replacement in replace_rules:
            origin_len = len(origin)
            # 滑动窗口遍历所有可能的起始位置
            for i in range(len(original_pinyin) - origin_len + 1):
                # 匹配需要替换的拼音片段
                if original_pinyin[i:i + origin_len] == origin:
                    # 生成新拼音并加入集合
                    new_pinyin = (
                            original_pinyin[:i] +
                            replacement +
                            original_pinyin[i + origin_len:]
                    )
                    variant_pinyins.add(new_pinyin)

        # 移除原始拼音避免重复
        variant_pinyins.discard(original_pinyin)

        # 收集所有候选词
        suggestions = []
        for vp in variant_pinyins:
            suggestions.extend(pinyin_index.get(vp, []))

        # 去重并智能排序
        unique_suggestions = sorted(
            list(set(suggestions)),
            key=lambda x: (
                x[0] != word[0],  # 首字母不同的优先
                -len(x)  # 长度相同的优先
            )
        )

        pron_suggestions[word] = unique_suggestions

    return pron_suggestions


def different_tones(do_not_exit_words, pinyin_index):
    """声调纠错（基于无声调索引）"""
    tones_suggestions = {}

    for word in do_not_exit_words:
        # 生成原词带声调的拼音（如："jie3jie3"）
        original_tone = ''.join(lazy_pinyin(word, style=Style.TONE))
        # 生成原词标准拼音（如："jiejie"）
        original_normal = ''.join(lazy_pinyin(word, style=Style.NORMAL))

        # 获取所有同音词（无声调匹配）
        same_pinyin_words = pinyin_index.get(original_normal, [])

        # 筛选声调不同的词
        suggestions = []
        for candidate in same_pinyin_words:
            # 生成候选词带声调拼音
            candidate_tone = ''.join(lazy_pinyin(candidate, style=Style.TONE))
            # 排除自身且声调不同
            if candidate != word:
                suggestions.append(candidate)

        # 去重排序（优先首字母匹配）
        unique_suggestions = sorted(
            list(set(suggestions)),
            key=lambda x: (x[0] != word[0], -len(x))
        )

        tones_suggestions[word] = unique_suggestions


    return tones_suggestions


def process_word(args, similarity_threshold=0.8):
    """处理单个词的相似拼音查找（带相似度）"""
    word, pinyin_index, length_index = args
    original_pinyin = ''.join(lazy_pinyin(word, style=Style.NORMAL))
    original_len = len(original_pinyin)

    max_edit_distance = math.ceil(
        (1 - similarity_threshold) * original_len / similarity_threshold
    )
    min_length = max(1, original_len - max_edit_distance)
    max_length = original_len + max_edit_distance

    candidate_dict = {}  # 改用字典存储 {候选词: 最高相似度}

    for length in range(min_length, max_length + 1):
        for target_pinyin in length_index.get(length, []):
            similarity = levenshtein_ratio(original_pinyin, target_pinyin)

            if similarity >= similarity_threshold:
                for candidate in pinyin_index.get(target_pinyin, []):
                    # 保留最高相似度
                    if candidate not in candidate_dict or similarity > candidate_dict[candidate]:
                        candidate_dict[candidate] = similarity

    # 排除自身
    candidate_dict.pop(word, None)

    # 排序策略：相似度降序 -> 首字母匹配 -> 词长倒序
    sorted_candidates = sorted(
        candidate_dict.items(),
        key=lambda x: (
            -x[1],  # 相似度降序
            x[0][0] != word[0],  # 首字母匹配优先
            -len(x[0])  # 长词优先
        )
    )

    return (word, [(candidate, round(similarity, 2)) for candidate, similarity in sorted_candidates])

def similar_pinyin(do_not_exit_words, pinyin_index, length_index, similarity_threshold=0.8):
    """并行化相似拼音查找"""
    # 准备并行化参数
    args = [(word, pinyin_index, length_index) for word in do_not_exit_words]

    # 根据词数量动态分配进程数
    num_words = len(do_not_exit_words)
    num_processes = min(cpu_count(), max(1, num_words // 2))  # 每2个词分配1个进程

    with Pool(processes=num_processes) as pool:
        # 使用偏函数传递阈值参数
        results = pool.map(partial(process_word, similarity_threshold=similarity_threshold), args)

    # 转换为字典格式
    similar_suggestions = dict(results)


    return {
        word: dict(candidates)  # 自动继承process_word中的四舍五入结果
        for word, candidates in results
    }


def repeat_words(text):
    """检测连续重复字词并生成修正文本"""
    # 参数设置
    max_window_size = 5  # 最大检测词长（根据医学文本特点优化）
    original_text = text
    n = len(original_text)
    delete_intervals = []

    # 多粒度重复检测（从长词到单字）
    for window_size in range(max_window_size, 0, -1):
        i = 0
        while i <= n - 2 * window_size:
            # 提取当前窗口和下一窗口内容
            current_segment = original_text[i:i + window_size]
            next_segment = original_text[i + window_size:i + 2 * window_size]

            # 排除包含标点的内容（基于医学报告特点）
            if any(c in ',.;:!?（）' for c in current_segment):
                i += 1
                continue

            if current_segment == next_segment:
                # 记录需要删除的区间（保留第一个，删除第二个）
                delete_intervals.append((i + window_size, i + 2 * window_size))
                # 跳过已标记区域继续检测
                i += 2 * window_size
            else:
                i += 1

    # 智能区间合并（处理重叠和嵌套情况）
    delete_intervals.sort()
    merged_intervals = []
    for start, end in delete_intervals:
        if not merged_intervals:
            merged_intervals.append([start, end])
        else:
            last_start, last_end = merged_intervals[-1]
            if start <= last_end:  # 处理重叠区间
                merged_intervals[-1][1] = max(last_end, end)
            else:
                merged_intervals.append([start, end])

    # 生成修正文本
    corrected_text = []
    last_pos = 0
    for start, end in merged_intervals:
        corrected_text.append(original_text[last_pos:start])
        last_pos = end
    corrected_text.append(original_text[last_pos:])

    # 提取候选删除项（保持原始顺序）
    delete_candidates = []
    seen = set()
    for start, end in merged_intervals:
        candidate = original_text[start:end]
        if candidate not in seen:
            seen.add(candidate)
            delete_candidates.append(candidate)

    return {
        '重复字词': delete_candidates,
        '去重': ''.join(corrected_text)
    }


def missing_words(seg_list, do_not_exit_words, pinyin_index, length_index):
    missing_suggestions = {}

    # 收集所有词典词汇（带拼音）
    all_dict_words = set()
    for key in pinyin_index.values():
        all_dict_words.update(key)

    # 遍历每个可能漏字的分词
    for i, word in enumerate(seg_list):
        if word not in do_not_exit_words:
            continue

        # 尝试与左侧组合
        if i > 0:
            combined = seg_list[i - 1] + word
            candidates = []
            for dict_word in all_dict_words:
                # 双重匹配条件：完全匹配或子集关系
                if combined == dict_word or combined in dict_word:
                    similarity = levenshtein_ratio(combined, dict_word)
                    candidates.append((dict_word, similarity))

            # 去重并排序
            if candidates:
                unique = list({w[0]: w for w in candidates}.values())
                # 排序逻辑：相似度降序 -> 词长降序 -> 字典序
                unique.sort(key=lambda x: (-x[1], -len(x[0]), x[0]))
                missing_suggestions[combined] = [w[0] for w in unique]

        # 尝试与右侧组合
        if i < len(seg_list) - 1:
            combined = word + seg_list[i + 1]
            candidates = []
            for dict_word in all_dict_words:
                if combined == dict_word or combined in dict_word:
                    similarity = levenshtein_ratio(combined, dict_word)
                    candidates.append((dict_word, similarity))

            if candidates:
                unique = list({w[0]: w for w in candidates}.values())
                unique.sort(key=lambda x: (-x[1], -len(x[0]), x[0]))
                missing_suggestions[combined] = [w[0] for w in unique]

    return missing_suggestions


def wrong_segmentation(seg_list, do_not_exit_words, pinyin_index, length_index):
    segmentation_suggestions = {}
    # 遍历每个不在词典中的词
    for word in do_not_exit_words:
        # 找到所有该词在seg_list中的位置
        indices = [i for i, w in enumerate(seg_list) if w == word]
        for i in indices:
            # 新策略：分别向左和向右遍历寻找满足条件的候选词
            left_candidate = None
            for j in range(i - 1, -1, -1):
                candidate = seg_list[j]
                # 条件：双方都不为对方的子集（即 candidate 不包含 word 且 word 不包含 candidate）
                if not (word in candidate or candidate in word):
                    left_candidate = candidate
                    break

            right_candidate = None
            for j in range(i + 1, len(seg_list)):
                candidate = seg_list[j]
                if not (word in candidate or candidate in word):
                    right_candidate = candidate
                    break

            # 根据新策略生成组合词：左侧只取一个合适的词，右侧同理
            combinations = []
            if left_candidate:
                combinations.append(left_candidate + word)   # 左组合
            if right_candidate:
                combinations.append(word + right_candidate)   # 右组合
            if left_candidate and right_candidate:
                combinations.append(left_candidate + word + right_candidate)  # 左右组合

            # 对每个组合词根据原有逻辑进行拼音匹配查词
            for combo in combinations:
                original_pinyin = ''.join(lazy_pinyin(combo, style=Style.NORMAL))
                original_len = len(original_pinyin)
                similarity_threshold = 0.8

                max_edit_distance = math.floor((1 - similarity_threshold) * original_len)
                min_length = max(1, original_len - max_edit_distance)
                max_length = original_len + max_edit_distance
                candidate_lengths = range(min_length, max_length + 1)

                # 收集候选词及其相似度
                candidates = []
                for length in candidate_lengths:
                    for target_pinyin in length_index.get(length, []):
                        similarity = levenshtein_ratio(original_pinyin, target_pinyin)
                        if similarity >= similarity_threshold:
                            for candidate_word in pinyin_index.get(target_pinyin, []):
                                candidates.append((candidate_word, similarity))

                # 去重并保留最高相似度
                candidate_dict = {}
                for candidate_word, sim in candidates:
                    if candidate_word not in candidate_dict or sim > candidate_dict[candidate_word]:
                        candidate_dict[candidate_word] = sim

                sorted_candidates = sorted(
                    candidate_dict.items(),
                    key=lambda x: (-x[1], -len(x[0]), x[0])
                )

                if sorted_candidates:
                    segmentation_suggestions[combo] = [
                        (w, round(sim, 2)) for w, sim in sorted_candidates
                    ]

    return segmentation_suggestions

from collections import defaultdict
from neo4j import GraphDatabase
from pypinyin import lazy_pinyin, Style


def resolve_tokens(tokens_info):
    """
    迭代执行唯一性规则：
    - 如果一个未确定分词的候选集合只有一个，则确定其句法成分；
    - 如果某个候选标签在所有未确定分词中只出现一次，也确定对应分词的句法成分；
    每次确定后从其他分词的候选集合中移除该标签，并打印确定信息。
    """
    changed = True
    while changed:
        changed = False
        # 构建候选标签到对应分词索引的映射
        label_to_indices = defaultdict(list)
        for info in tokens_info:
            if info['determined'] is None:
                for lab in info['candidates']:
                    label_to_indices[lab].append(info['index'])

        # 规则1：候选集合只有一个的分词直接确定
        for info in tokens_info:
            if info['determined'] is None and len(info['candidates']) == 1:
                determined_label = next(iter(info['candidates']))
                info['determined'] = determined_label
                changed = True
                # print(
                #     f"确定分词 '{info['token']}'（位置 {info['index']}）的句法成分为 {determined_label} —— 候选只有这一种")
                # # 从其他未确定分词中移除该标签
                # for other in tokens_info:
                #     if other['determined'] is None and other is not info and determined_label in other['candidates']:
                #         other['candidates'].discard(determined_label)

        # 规则2：如果某个标签在所有未确定分词中只出现一次，则对应分词可确定
        for lab, indices in label_to_indices.items():
            if len(indices) == 1:
                idx = indices[0]
                info = next(x for x in tokens_info if x['index'] == idx)
                if info['determined'] is None:
                    info['determined'] = lab
                    changed = True
                    # print(
                    #     f"确定分词 '{info['token']}'（位置 {info['index']}）的句法成分为 {lab} —— 标签 {lab}在本句中唯一")
                    # for other in tokens_info:
                    #     if other['determined'] is None and lab in other['candidates']:
                    #         other['candidates'].discard(lab)
    return tokens_info


def locating_entities(sentence, inspection_area_name, seg_list):
    """
    根据给定句子、InspectionArea名称和分词列表，
    确定每个分词的句法成分。分词可能属于：
    "定语"、"主语"、"谓语"、"补语"、"宾语"或由定语与主语共同构成的"定中短语"。

    知识图谱中仅存在以下标签：
      Attributive、Subject、Predicate、Complement、Object、AttributiveSubject、InspectionArea
    以及以下定向关系：
      - "定中": 从 Attributive 指向 Subject
      - "构成"、"构成关系": 分别从 Attributive 或 Subject 指向 AttributiveSubject
      - "主谓": 从 AttributiveSubject 指向 Predicate
      - "谓补": 从 Predicate 指向 Complement
      - "谓宾": 从 Predicate 指向 Object
      - "包含": InspectionArea 指向其他实体

    所有查询均限定在与给定 InspectionArea 相关的子图中。

    返回一个字典，其中：
      {
        "determined": {分词: 句法成分},
        "undetermined": {分词: 在 InspectionArea 限定下的 label列表}
      }
    """
    roles = {}  # 存储分词及其确定的句法成分，例如 {word: role}
    reasons = {}  # 存储每个分词确定句法成分的原因说明

    from neo4j import GraphDatabase
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "kuangxi1323"))

    with driver.session() as session:
        # ① 针对每个分词，查询其在 InspectionArea 子图中的实体及标签
        for word in seg_list:
            if word in roles:
                continue  # 若已确定，则跳过
            query = (
                "MATCH (ia:InspectionArea {name: $inspection_area_name})-[:包含*]->(n) "
                "WHERE n.name = $word "
                "RETURN n.name AS name, labels(n) AS labels"
            )
            result = session.run(query, inspection_area_name=inspection_area_name, word=word)
            found = False
            for record in result:
                entity_labels = record["labels"]
                # 若某个实体的标签中包含 AttributiveSubject，则直接确定为定中短语
                if "AttributiveSubject" in entity_labels:
                    roles[word] = "定中短语"
                    reasons[word] = f"在知识图谱中，实体 '{word}' 包含标签 'AttributiveSubject'."
                    found = True
                    break
            if found:
                continue

        # ② 利用分词间实体之间的关系进一步判断句法成分
        # 遍历所有分词对，查询限定在 InspectionArea 子图中的关系
        n = len(seg_list)
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                word1 = seg_list[i]
                word2 = seg_list[j]
                rel_query = (
                    "MATCH (ia:InspectionArea {name: $inspection_area_name})-[:包含*]->(a), "
                    "(ia)-[:包含*]->(b), "
                    "(a)-[r]->(b) "
                    "WHERE a.name = $word1 AND b.name = $word2 AND type(r) IN ['定中', '构成', '构成关系', '主谓', '谓补', '谓宾'] "
                    "RETURN a.name AS a_name, labels(a) AS a_labels, "
                    "b.name AS b_name, labels(b) AS b_labels, type(r) AS rel_type"
                )
                rel_result = session.run(rel_query, inspection_area_name=inspection_area_name, word1=word1, word2=word2)
                for record in rel_result:
                    a_labels = record["a_labels"]
                    b_labels = record["b_labels"]
                    rel_type = record["rel_type"]

                    # 通过不同的关系确定角色，并打印确认原因
                    if rel_type == "定中":
                        # 期望 a 为 Attributive（定语），b 为 Subject（主语）
                        if word1 not in roles:
                            roles[word1] = "定语"
                            reasons[word1] = (f"通过关系 '定中'，实体 '{word1}'（标签 {a_labels}）被确定为定语，"
                                              f"与 '{word2}'（标签 {b_labels}）构成定中短语.")
                        if word2 not in roles:
                            roles[word2] = "主语"
                            reasons[word2] = (f"通过关系 '定中'，实体 '{word2}'（标签 {b_labels}）被确定为主语，"
                                              f"与 '{word1}'（标签 {a_labels}）构成定中短语.")
                    elif rel_type in ["构成", "构成关系"]:
                        # 如果 a 为 Attributive 且 b 为 AttributiveSubject，则 a 定为定语
                        if "Attributive" in a_labels and "AttributiveSubject" in b_labels:
                            if word1 not in roles:
                                roles[word1] = "定语"
                                reasons[word1] = (f"通过关系 '{rel_type}'，实体 '{word1}'（标签 {a_labels}）被确定为定语，"
                                                  f"参与构成 AttributiveSubject '{word2}'（标签 {b_labels}）.")
                        # 如果 a 为 Subject 且 b 为 AttributiveSubject，则 a 定为主语
                        if "Subject" in a_labels and "AttributiveSubject" in b_labels:
                            if word1 not in roles:
                                roles[word1] = "主语"
                                reasons[word1] = (f"通过关系 '{rel_type}'，实体 '{word1}'（标签 {a_labels}）被确定为主语，"
                                                  f"参与构成 AttributiveSubject '{word2}'（标签 {b_labels}）.")
                    elif rel_type == "主谓":
                        # 从 AttributiveSubject 到 Predicate，确定 AttributiveSubject 为定中短语，Predicate 为谓语
                        if "AttributiveSubject" in a_labels and "Predicate" in b_labels:
                            if word1 not in roles:
                                roles[word1] = "定中短语"
                                reasons[word1] = (f"通过关系 '主谓'，实体 '{word1}'（标签 {a_labels}）被确定为定中短语，"
                                                  f"与谓语 '{word2}'（标签 {b_labels}）相关联.")
                            if word2 not in roles:
                                roles[word2] = "谓语"
                                reasons[word2] = (f"通过关系 '主谓'，实体 '{word2}'（标签 {b_labels}）被确定为谓语，"
                                                  f"与定中短语 '{word1}'（标签 {a_labels}）相关联.")
                    elif rel_type == "谓补":
                        # 从 Predicate 到 Complement，确定 Predicate 为谓语，Complement 为补语
                        if "Predicate" in a_labels and "Complement" in b_labels:
                            if word1 not in roles:
                                roles[word1] = "谓语"
                                reasons[word1] = (f"通过关系 '谓补'，实体 '{word1}'（标签 {a_labels}）被确定为谓语，"
                                                  f"与补语 '{word2}'（标签 {b_labels}）相关联.")
                            if word2 not in roles:
                                roles[word2] = "补语"
                                reasons[word2] = (f"通过关系 '谓补'，实体 '{word2}'（标签 {b_labels}）被确定为补语，"
                                                  f"与谓语 '{word1}'（标签 {a_labels}）相关联.")
                    elif rel_type == "谓宾":
                        # 从 Predicate 到 Object，确定 Predicate 为谓语，Object 为宾语
                        if "Predicate" in a_labels and "Object" in b_labels:
                            if word1 not in roles:
                                roles[word1] = "谓语"
                                reasons[word1] = (f"通过关系 '谓宾'，实体 '{word1}'（标签 {a_labels}）被确定为谓语，"
                                                  f"与宾语 '{word2}'（标签 {b_labels}）相关联.")
                            if word2 not in roles:
                                roles[word2] = "宾语"
                                reasons[word2] = (f"通过关系 '谓宾'，实体 '{word2}'（标签 {b_labels}）被确定为宾语，"
                                                  f"与谓语 '{word1}'（标签 {a_labels}）相关联.")

        # ③ 对于未能确定句法成分的分词，查询其在 InspectionArea 子图下的所有 label
        undetermined = {}
        # 为避免重复查询，对 seg_list 中未确定的分词取唯一集合
        for word in set(seg_list):
            if word in roles:
                continue
            und_query = (
                "MATCH (ia:InspectionArea {name: $inspection_area_name})-[:包含*]->(n) "
                "WHERE n.name = $word "
                "RETURN DISTINCT labels(n) AS labels"
            )
            und_result = session.run(und_query, inspection_area_name=inspection_area_name, word=word)
            label_set = set()
            for record in und_result:
                for lab in record["labels"]:
                    label_set.add(lab)
            undetermined[word] = list(label_set)

        # 最后打印每个分词的最终句法成分确定情况
        # print("最终句法成分确定结果：")
        # for word in seg_list:
        #     if word in roles:
        #         print(f"分词 '{word}' 被确定为：{roles[word]}。原因：{reasons[word]}")
        #     else:
        #         print(f"分词 '{word}' 未能确定句法成分。标签：{undetermined.get(word, [])}")

    driver.close()
    return {"determined": roles, "undetermined": undetermined}


def select_undetermined(entity_label):
    """
    处理 entity_label 中 undetermined 部分，删除无用的分词：

    1. 保留 undetermined 中最大的分词：若存在两个分词，其中一个是另一个的连续子串，
       则删除较短的子串。
    2. 去除 undetermined 中在 determined 中出现过的子集：如果 determined 中的某个分词包含
       undetermined 中的分词（连续匹配），则删除 undetermined 中的该分词。

    参数:
      entity_label: dict，包含两个键：
          "determined": {分词: 句法成分}
          "undetermined": {分词: [在 InspectionArea 限定下的 label 列表]}

    返回:
      处理后的 entity_label，undetermined 中删除了无用分词。
    """
    determined = entity_label.get("determined", {})
    undetermined = entity_label.get("undetermined", {})

    # 第一步：过滤掉 undetermined 中为其他分词连续子串的项
    und_tokens = list(undetermined.keys())
    tokens_to_remove = set()
    for token in und_tokens:
        for other_token in und_tokens:
            if token == other_token:
                continue
            # 如果 token 是 other_token 的连续子串，则标记 token 删除
            if token in other_token:
                tokens_to_remove.add(token)
                break

    for token in tokens_to_remove:
        if token in undetermined:
            # print(f"删除 undetermined 中的子集 '{token}'，因其是其它更长分词的子串。")
            del undetermined[token]

    # 第二步：去除 undetermined 中在 determined 中出现过的子集
    determined_tokens = list(determined.keys())
    tokens_to_remove_determined = set()
    for token in list(undetermined.keys()):
        for det_token in determined_tokens:
            # 如果 undetermined 中的 token 是 determined 中某个分词的连续子串，则删除
            if token in det_token:
                tokens_to_remove_determined.add(token)
                break

    for token in tokens_to_remove_determined:
        if token in undetermined:
            # print(f"删除 undetermined 中的子集 '{token}'，因其在 determined 中 '{det_token}' 已出现。")
            del undetermined[token]

    # 更新 entity_label 中 undetermined 部分，并返回
    entity_label["undetermined"] = undetermined
    return entity_label


def find_top_related_entities(entity_label, inspection_area_name, top_n=5):
    """
    从 entity_label 中（包含 determined 与 undetermined 两部分），
    寻找与这两部分实体节点最相关的前 top_n 个实体节点，并返回它们的名称、label 以及相关性分数。

    思路：
      1. 提取 determined 与 undetermined 两部分的分词名称集合，记为 candidate_names。
      2. 在 InspectionArea 子图中，以 candidate_names 为锚点，
         查询所有与候选节点有直接关系的其它节点，并统计其与候选节点间的连接数作为相关性分数。
      3. 返回相关性分数最高的前 top_n 个候选节点及其 label 信息。
    """
    determined = entity_label.get("determined", {})
    undetermined = entity_label.get("undetermined", {})

    # 候选实体名称集合：两部分节点名称的并集
    candidate_names = set(determined.keys()).union(set(undetermined.keys()))
    if not candidate_names:
        # print("候选名称集合为空。")
        return []

    from neo4j import GraphDatabase
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "kuangxi1323"))
    top_entities = []
    with driver.session() as session:
        # 查询在指定 InspectionArea 子图中，与 candidate_names 中节点存在直接关系的所有候选节点，
        # 并统计每个候选节点与 candidate_names 集合中节点之间的连接数作为相关性分数，
        # 同时返回候选节点的名称和 label。
        query = (
            "MATCH (ia:InspectionArea {name: $inspection_area_name})-[:包含*]->(anchor) "
            "WHERE anchor.name IN $candidate_names "
            "WITH collect(distinct anchor) as anchors "
            "MATCH (ia:InspectionArea {name: $inspection_area_name})-[:包含*]->(m) "
            "MATCH (m)-[r]-(a) "
            "WHERE a IN anchors "
            "RETURN m.name as candidate, labels(m) as candidate_labels, count(r) as rel_count "
            "ORDER BY rel_count DESC LIMIT $top_n"
        )
        result = session.run(query,
                             inspection_area_name=inspection_area_name,
                             candidate_names=list(candidate_names),
                             top_n=top_n)
        for record in result:
            top_entities.append({
                "name": record["candidate"],
                "labels": record["candidate_labels"],
                "rel_count": record["rel_count"]
            })

    driver.close()

    # print("最相关的前 {} 个实体节点：".format(top_n))

    # for entity in top_entities:
    #     print(f"实体: {entity['name']}，标签: {entity['labels']}，相关性分数: {entity['rel_count']}")
    return top_entities

from config import API_KEY, BASE_URL, MODEL_NAME
from utils.clients import Client
def main_desc(body_part, description):

    pinyin_index, length_index = build_pinyin_index()  # 构建拼音-词汇倒排索引

    inspectionArea = body_part
    text = description
    sentences = split_medical_text(text)
    # print(sentences)
    corrected_text = ""
    for sentence in sentences:
        # print("---------------------------------------------------------------------------------------------------------\n")
        SYSTEM_PROMPT =(
            "你是一个医学影像学的纠错专家。下面我会给你提供可能出错的影像描述，同时提供给你该影像描述中可能出错的部分，以及其候选替换词。\n"
            "你要根据我给你提供的信息以及自己的理解，去对提供给你的影响描述纠错，注意：我提供给你的提示，有些可能不属于影像学词汇，我要求你只给我返回纠错结果，不要返回任何的别的文字。\n"
            "以下是可能出错的句子和候选替换词:\n"
        )
        input_text = SYSTEM_PROMPT+"\n" + "可能出错的影像描述:" + sentence + "\n"
        seg_list = participle(sentence)  # jieba 加载医学影像学词典后进行 全模式 分词
        do_not_exit_words = query_engine(seg_list, pinyin_index)  # 筛选不存在与词典的分词

        typo_results = keyword_typo(do_not_exit_words, pinyin_index)  # 因编辑时键盘误触导致的错词
        pron_results = not_familiar(do_not_exit_words, pinyin_index)  # 因拼音不熟悉导致的错误
        tones_results = different_tones(do_not_exit_words, pinyin_index)  # 拼音相同但音调不同
        similar_results = similar_pinyin(
            do_not_exit_words,
            pinyin_index,
            length_index,
            similarity_threshold=0.8  # 可调节阈值
        )
        repeat_results = repeat_words(sentence)
        missing_results = missing_words(seg_list, do_not_exit_words, pinyin_index, length_index)
        segmentation_results = wrong_segmentation(seg_list, do_not_exit_words, pinyin_index, length_index)

        # 合并前四个结果
        merged_results = {}
        merged_results.update(typo_results)
        merged_results.update(pron_results)
        merged_results.update(tones_results)
        merged_results.update(similar_results)

        # 添加missing和segmentation中的新键值对
        merged_results.update(missing_results)
        merged_results.update(segmentation_results)
        #
        # print("最终合并结果：")
        # print(merged_results)
        input_text += "候选替换词（仅供参考）：" + str(merged_results) + "\n"

        # print("去重：")
        # print(repeat_results)

        entity_label = locating_entities(sentence, inspectionArea, seg_list)

        selected_undetermined = select_undetermined(entity_label)

        most_entity = find_top_related_entities(entity_label, inspectionArea)
        input_text += "和这句影像描述最可能相关的实体：" + str(most_entity) + "\n"
        # print(input_text)
        # local_client = LocalClient(model_name="test", API_KEY="0", base_url="http://192.168.1.136:8000/v1")
        client = Client(model_name=MODEL_NAME, API_KEY=API_KEY,base_url=BASE_URL)
        corrected_sentence = client.generate(input_text)
        # print(corrected_sentence)
        corrected_text += corrected_sentence
        # print("---------------------------------------------------------------------------------------------------------\n")
    return corrected_text
