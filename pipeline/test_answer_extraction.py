"""
测试答案提取功能
==================

测试 NodeB_AnswerEvaluator 的智能答案提取功能，验证能否正确从思维链中提取最终答案。
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.evaluation_pipeline import NodeB_AnswerEvaluator


def test_answer_extraction():
    """测试各种答案提取场景"""
    
    evaluator = NodeB_AnswerEvaluator(tolerance=0.01)
    
    # 测试用例
    test_cases = [
        # (输入文本, 期望提取的答案, 测试描述)
        
        # 1. 思维链案例（策略1：最后一行）
        (
            "Based on the chart provided, here is the step-by-step calculation:\n\n"
            "1. Identify the 2nd lowest country:\n"
            "   * Australia: 81.32 (2nd Lowest)\n\n"
            "2. Calculate the sum:\n"
            "   * Sum = 81.32 + 422.15\n"
            "   * **Sum = 503.47**\n\n"
            "503.47",
            "503.47",
            "策略1: 思维链 - 最后一行纯数字"
        ),
        
        # 2. 直接数字答案（策略1：最后一行）
        (
            "10",
            "10",
            "策略1: 直接数字答案"
        ),
        
        # 3. 数字列表（策略1：最后一行）
        (
            "Looking at the chart, the values are:\n"
            "389.4, 352.7, 319.5, 284.8, 250.1",
            "389.4, 352.7, 319.5, 284.8, 250.1",
            "策略1: 数字列表在最后一行"
        ),
        
        # 4. Answer: 标记（策略2）
        (
            "To find the mean, we calculate:\n"
            "Mean = (27.6 + 37.4) / 2 = 65.0 / 2\n"
            "Answer: 32.5",
            "32.5",
            "策略2: Answer: 标记"
        ),
        
        # 5. Markdown 粗体（策略3）
        (
            "Based on the chart, the countries are Canada and South Korea.\n"
            "The count is **2**.\n"
            "This represents the bottom 2 countries in GDP.",
            "2",
            "策略3: Markdown 粗体数字"
        ),
        
        # 6. 等号后数字（策略4）
        (
            "Looking at the lowest values:\n"
            "Child Protection NGOs: 360 (Lowest)\n"
            "Homeless Aid: 380 (Second Lowest)\n"
            "Middle value = (360 + 380) / 2 = 370",
            "370",
            "策略4: 等号后的数字"
        ),
        
        # 7. 空响应
        (
            "",
            "",
            "边界情况: 空响应"
        ),
        
        # 8. 只有文字没有数字
        (
            "Based on the chart, the value appears to be unclear.",
            "Based on the chart, the value appears to be unclear.",
            "边界情况: 无数字内容"
        ),
        
        # 9. 多个数字，取最后一个（策略5）
        (
            "The first value is 100, the second is 200, and the final answer is 42.27",
            "42.27",
            "策略5: 多个数字取最后一个"
        ),
        
        # 10. 带小数的数字列表
        (
            "The values are 178.5, 165.2, 153.9, 142.7, 131.4",
            "178.5, 165.2, 153.9, 142.7, 131.4",
            "策略5: 带小数的数字列表（fallback）"
        ),
    ]
    
    print("=" * 80)
    print("答案提取功能测试")
    print("=" * 80)
    print()
    
    passed = 0
    failed = 0
    
    for i, (input_text, expected, description) in enumerate(test_cases, 1):
        extracted, strategy = evaluator.extract_answer_from_text(input_text)
        
        # 标准化比较
        extracted_norm = extracted.strip()
        expected_norm = expected.strip()
        
        success = extracted_norm == expected_norm
        
        if success:
            passed += 1
            status = "✓ 通过"
        else:
            failed += 1
            status = "✗ 失败"
        
        print(f"[测试 {i:2d}] {status} - {description}")
        print(f"  策略: {strategy}")
        print(f"  输入: {input_text[:80]}{'...' if len(input_text) > 80 else ''}")
        print(f"  期望: '{expected_norm}'")
        print(f"  提取: '{extracted_norm}'")
        
        if not success:
            print(f"  ❌ 不匹配!")
        
        print()
    
    print("=" * 80)
    print(f"测试结果: {passed} 通过, {failed} 失败 (总计 {passed + failed})")
    print("=" * 80)
    
    return failed == 0


def test_evaluation_with_extraction():
    """测试完整的评估流程（包含答案提取）"""
    
    evaluator = NodeB_AnswerEvaluator(tolerance=0.01)
    
    print("\n" + "=" * 80)
    print("完整评估流程测试（含答案提取）")
    print("=" * 80)
    print()
    
    test_cases = [
        # (VLM输出, Ground Truth, 期望是否正确, 测试描述)
        
        # 思维链输出 - 应该匹配
        (
            "Based on calculation:\n**Sum = 503.47**\n\n503.47",
            "503.47",
            True,
            "思维链输出，答案正确"
        ),
        
        # 直接数字 - 应该匹配
        (
            "10",
            "10",
            True,
            "直接数字答案"
        ),
        
        # 数字列表 - 应该匹配
        (
            "The values are:\n389.4, 352.7, 319.5, 284.8, 250.1",
            "389.4, 352.7, 319.5, 284.8, 250.1",
            True,
            "数字列表答案"
        ),
        
        # 思维链但答案错误
        (
            "Based on calculation:\nAnswer: 500.00",
            "503.47",
            False,
            "思维链输出，但答案错误"
        ),
    ]
    
    for i, (vlm_answer, ground_truth, expected_correct, description) in enumerate(test_cases, 1):
        result = evaluator.evaluate(vlm_answer, ground_truth)
        
        is_correct = result["is_correct"]
        success = is_correct == expected_correct
        
        print(f"[评估 {i}] {'✓ 通过' if success else '✗ 失败'} - {description}")
        print(f"  VLM: {vlm_answer[:60]}{'...' if len(vlm_answer) > 60 else ''}")
        print(f"  GT:  {ground_truth}")
        print(f"  匹配类型: {result['match_type']}")
        print(f"  相似度: {result['similarity_score']:.4f}")
        print(f"  提取策略: {result['details'].get('extraction_strategy', 'N/A')}")
        print(f"  提取应用: {result['details'].get('extraction_applied', False)}")
        
        if 'extracted_answer' in result['details']:
            print(f"  提取答案: {result['details']['extracted_answer'][:60]}")
        
        print()
    
    print("=" * 80)


if __name__ == "__main__":
    print("开始测试答案提取功能...\n")
    
    # 运行提取功能测试
    extraction_success = test_answer_extraction()
    
    # 运行完整评估测试
    test_evaluation_with_extraction()
    
    print("\n测试完成!")
    
    if extraction_success:
        print("✅ 所有答案提取测试通过!")
        sys.exit(0)
    else:
        print("❌ 部分测试失败，请检查实现")
        sys.exit(1)
