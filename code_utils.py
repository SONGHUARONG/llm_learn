import re

def extract_codes(text):
    result = {}

    # 定义正则表达式
    # 合同号或产品编码：000开头，14位数字字母
    contract_product_pattern = r'(?:合同号|产品编码)?\s*:\s*(000[A-Za-z0-9]{11})\b|(?:^|\b)(000[A-Za-z0-9]{11})\b(?![A-Za-z0-9])'
    # 更鲁棒地匹配：允许“合同号”等前缀，也可以无前缀独立出现
    contract_full_pattern = r'(?:合同号|产品编码)[：: ]*\s*(000[A-Za-z0-9]{11})\b|(?<!\w)(000[A-Za-z0-9]{11})(?!\w)'

    # 项目编码：5开头，7位
    project_pattern = r'(?<!\w)(5[A-Za-z0-9]{6})(?!\w)'
    # 子项目编码：6开头，7位
    subproject_pattern = r'(?<!\w)(6[A-Za-z0-9]{6})(?!\w)'

    # 提取合同号/产品编码
    matches = re.findall(contract_full_pattern, text)
    for match in matches:
        code = match[0] if match[0] else match[1]
        if code and len(code) == 14 and code.startswith('000'):
            # 优先保留第一个有效值
            if '合同号' not in result:
                result['合同号'] = code
            if '产品编码' not in result:
                result['产品编码'] = code

    # 提取项目编码
    project_codes = re.findall(project_pattern, text)
    for code in project_codes:
        # 排除可能是时间部分的情况（如后面紧接“月”字）
        match_iter = re.finditer(project_pattern, text)
        for m in match_iter:
            if m.group(1) == code:
                # 检查后一个字符是否为“月”或其他可能构成时间的部分
                end_pos = m.end()
                if end_pos < len(text) and text[end_pos] == '月':
                    continue  # 跳过，是时间的一部分
                result['项目编码'] = code
                break
        if '项目编码' in result:
            break

    # 提取子项目编码
    subproject_codes = re.findall(subproject_pattern, text)
    for code in subproject_codes:
        match_iter = re.finditer(subproject_pattern, text)
        found_valid = False
        for m in match_iter:
            if m.group(1) == code:
                end_pos = m.end()
                if end_pos < len(text) and text[end_pos] == '月':
                    continue  # 跳过时间干扰
                result['子项目编码'] = code
                found_valid = True
                break
        if found_valid:
            break

    return result
