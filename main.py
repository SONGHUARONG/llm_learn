# import ssl
# # try:
# #     # Try to get the ca certificate
# #     _create_unverified_https_context = ssl._create_unverified_context
# # except AttributeError:
# #     # Legacy Python that doesn't verify HTTPS certificates by default
# #     pass
# # else:
# #     # Handle target environment that doesn't support HTTPS verification
# #     ssl._create_default_https_context = _create_unverified_https_context
#
# import nltk
# # nltk.download('punkt_tab')
# def pos_tag(sentence):
#     words = nltk.word_tokenize(sentence)
#     tagged_words = nltk.pos_tag(words)
#     return tagged_words
#
#
# def is_question(sentence):
#     tagged_words = pos_tag(sentence)
#
#     if tagged_words[0][1] == 'WP' or tagged_words[0][1] == 'WRB':
#         return True
#     else:
#         return False
# sentence1 = "项目56a08x2 收入是多少？"
# print(is_question(sentence1)) # True


import re
from typing import Dict, List, Set

def extract_codes(text: str) -> Dict[str, str]:
    """
    从文本中提取合同号/产品编码、项目编码、子项目编码
    要求：
      - 合同号/产品编码：000开头，14位数字字母
      - 项目编码：5开头，7位数字字母
      - 子项目编码：6开头，7位数字字母
    条件：
      - 不提取时间中的数字（如 '56a08x21月' 中不能把 6a08x21 当作子项目编码）
      - 不提取已匹配长编码中的子串编码
    """

    results = {}

    # 定义正则：单词边界 + 指定模式 + 单词边界
    # 防止匹配到中间部分（如 000... 中间截出 5...）
    patterns = {
        "合同号": r'\b(000[0-9a-zA-Z]{11})\b',  # 000 + 11个字符 = 14位
        "rt合同号": r'\b(000[0-9a-zA-Z]{11})\b',  # 000 + 11个字符 = 14位
        "项目编码": r'\b(5[0-9a-zA-Z]{6})\b',    # 5 + 6个字符 = 7位
        "子项目编码": r'\b(6[0-9a-zA-Z]{6})\b',  # 6 + 6个字符 = 7位
    }

    # 用于记录所有成功匹配的 span（位置区间），用于后续去重和冲突判断
    matches = []

    for key, pattern in patterns.items():
        for match in re.finditer(pattern, text):
            value = match.group(1)
            start, end = match.span()

            # 进一步校验：确保该匹配不是时间的一部分（如 xx月、xx日、xx年）
            after_text = text[end:end+2]
            before_text = text[max(0, start-2):start]
            context = before_text + value + after_text

            # 排除常见时间格式干扰，比如 "56a08x21月" → 末尾是 "1月"，说明可能是时间
            # 我们要避免把 "6a08x21" 从 "56a08x21月" 中提取出来
            if re.search(r'\d+月|\d+日|\d+年|\d+时', context):
                continue  # 跳过疑似时间的部分

            # 特别处理：如果这个匹配是某个更长的合法编码的一部分，跳过
            is_subpart = False
            for other_key, other_value, other_start, other_end in matches:
                if other_start < start and end <= other_end:
                    # 当前匹配被包含在另一个已匹配项中（如 5453012 是 000... 的一部分）
                    is_subpart = True
                    break
            if is_subpart:
                continue

            # 添加当前匹配
            matches.append((key, value, start, end))
            # 如果已有同类编码，保留第一个（可选：也可保留多个，这里先保留一个）
            if key not in results:
                results[key] = value

    return results


# === 测试用例 ===
if __name__ == "__main__":
    test_cases = [
        "合同号00012349999999项目编码56a08x2子项目编码6a08x21",
        "错误示例：56a08x21月不应提取子项目编码",
        "混合内容：00023545301234 和 5abc123 和 6xyz789",
        "嵌套测试：00023545301234 中不要提取 5453012",
        "时间干扰：项目编码5abc123于2024年6月完成，子项目编码6xyz789启动",
        "边界测试：a00012345678901b 应该能提取 00012345678901",
        "无效测试：00123456789012 不以000开头，不应提取",
        "模糊测试：56a08x21月 中只提取 56a08x2，不提取 6a08x21",
    ]

    for i, text in enumerate(test_cases):
        print(f"测试 {i+1}: {text}")
        result = extract_codes(text)
        print("→ 提取结果:", result)
        print()

