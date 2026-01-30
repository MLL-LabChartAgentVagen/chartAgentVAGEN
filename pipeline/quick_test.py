"""快速测试答案提取功能"""

# 直接测试提取逻辑
import re

def extract_answer_from_text(text: str) -> tuple[str, str]:
    """从包含思维链的文本中智能提取最终数字答案"""
    
    if not text or not text.strip():
        return "", "no_extraction"
    
    # 策略1: 提取最后一行的纯数字/数字列表
    lines = text.strip().split('\n')
    for i in range(len(lines) - 1, max(-1, len(lines) - 6), -1):
        line = lines[i].strip()
        if re.match(r'^[\d\s\.,]+$', line) and line:
            if re.search(r'\d', line):
                return line, "strategy_1_last_line"
    
    # 策略2: 查找 "Answer:" 标记
    answer_patterns = [
        r'(?:answer|result|solution):\s*([\d\s\.,]+)',
        r'(?:answer|result|solution)\s*=\s*([\d\s\.,]+)',
    ]
    for pattern in answer_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip(), "strategy_2_answer_keyword"
    
    # 策略3: Markdown 粗体
    tail_text = text[-200:] if len(text) > 200 else text
    bold_matches = re.findall(r'\*\*([\d\s\.,]+)\*\*', tail_text)
    if bold_matches:
        return bold_matches[-1].strip(), "strategy_3_markdown_bold"
    
    # 策略4: 等号后的数字
    last_lines = '\n'.join(lines[-10:])
    equals_matches = re.findall(r'=\s*([\d\s\.,]+)', last_lines)
    if equals_matches:
        return equals_matches[-1].strip(), "strategy_4_equals_sign"
    
    # 策略5: fallback
    number_list_pattern = r'\b\d+(?:\.\d+)?(?:\s*,\s*\d+(?:\.\d+)?)+\b'
    number_lists = re.findall(number_list_pattern, text)
    if number_lists:
        return number_lists[-1].strip(), "strategy_5_fallback_list"
    
    single_numbers = re.findall(r'\b\d+\.?\d*\b', text)
    if single_numbers:
        return single_numbers[-1].strip(), "strategy_5_fallback_single"
    
    return text, "no_extraction"


# 测试用例
test_cases = [
    ("Based on calculation:\n**Sum = 503.47**\n\n503.47", "503.47", "思维链-最后一行"),
    ("10", "10", "直接数字"),
    ("Values:\n389.4, 352.7, 319.5", "389.4, 352.7, 319.5", "数字列表"),
    ("Answer: 32.5", "32.5", "Answer标记"),
    ("The count is **2**.", "2", "Markdown粗体"),
    ("Result = 370", "370", "等号"),
]

print("快速测试答案提取功能")
print("=" * 60)

passed = 0
failed = 0

for input_text, expected, desc in test_cases:
    extracted, strategy = extract_answer_from_text(input_text)
    success = extracted.strip() == expected.strip()
    
    status = "✓" if success else "✗"
    print(f"{status} {desc}: {strategy}")
    if not success:
        print(f"  期望: '{expected}', 得到: '{extracted}'")
        failed += 1
    else:
        passed += 1

print("=" * 60)
print(f"结果: {passed} 通过, {failed} 失败")
