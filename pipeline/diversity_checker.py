"""
Diversity Checker for Generated Metadata

Usage:
    python diversity_checker.py --input generated_metadata.json --report diversity_report.txt
"""

import json
import argparse
from collections import Counter
from typing import Dict, List, Any


def check_topic_diversity(results: List[Dict]) -> Dict[str, Any]:
    """检查主题多样性"""
    concepts = [r.get('semantic_concept', '') for r in results]
    unique_concepts = len(set(concepts))
    
    # 检查是否有完全重复的概念
    concept_counts = Counter(concepts)
    duplicates = {k: v for k, v in concept_counts.items() if v > 1}
    
    return {
        "total_samples": len(results),
        "unique_concepts": unique_concepts,
        "diversity_ratio": unique_concepts / len(results) if results else 0,
        "duplicates": duplicates,
        "status": "✅ GOOD" if unique_concepts / len(results) > 0.95 else "⚠️ LOW DIVERSITY"
    }


def check_distribution_diversity(results: List[Dict]) -> Dict[str, Any]:
    """检查统计分布多样性"""
    distributions = []
    for r in results:
        dist_type = r.get('master_data', {}).get('statistical_properties', {}).get('distribution_type', 'unknown')
        distributions.append(dist_type)
    
    dist_counts = Counter(distributions)
    unique_dists = len(set(distributions))
    
    # 理想情况：5种分布类型均匀分布
    expected_types = ['normal', 'power_law', 'bimodal', 'uniform', 'exponential']
    coverage = sum(1 for dt in expected_types if dt in dist_counts) / len(expected_types)
    
    return {
        "distribution_counts": dict(dist_counts),
        "unique_distributions": unique_dists,
        "type_coverage": coverage,
        "status": "✅ GOOD" if coverage >= 0.6 else "⚠️ LIMITED VARIETY"
    }


def check_entity_count_diversity(results: List[Dict]) -> Dict[str, Any]:
    """检查实体数量多样性"""
    entity_counts = []
    for r in results:
        count = len(r.get('master_data', {}).get('entities', []))
        entity_counts.append(count)
    
    count_distribution = Counter(entity_counts)
    unique_counts = len(set(entity_counts))
    
    return {
        "count_distribution": dict(count_distribution),
        "unique_counts": unique_counts,
        "status": "✅ GOOD" if unique_counts >= 3 else "⚠️ LOW VARIETY"
    }


def check_value_range_diversity(results: List[Dict]) -> Dict[str, Any]:
    """检查数值范围多样性"""
    scales = []
    for r in results:
        primary_values = r.get('master_data', {}).get('primary_values', [])
        if primary_values:
            max_val = max(primary_values)
            # 判断数量级
            if max_val < 100:
                scales.append("small")
            elif max_val < 10000:
                scales.append("medium")
            else:
                scales.append("large")
    
    scale_counts = Counter(scales)
    
    return {
        "scale_distribution": dict(scale_counts),
        "status": "✅ GOOD" if len(scale_counts) >= 2 else "⚠️ SINGLE SCALE"
    }


def generate_report(results: List[Dict]) -> str:
    """生成多样性报告"""
    report = []
    report.append("=" * 60)
    report.append("DIVERSITY ANALYSIS REPORT")
    report.append("=" * 60)
    report.append("")
    
    # 主题多样性
    topic_div = check_topic_diversity(results)
    report.append(f"## Topic Diversity {topic_div['status']}")
    report.append(f"   Total samples: {topic_div['total_samples']}")
    report.append(f"   Unique concepts: {topic_div['unique_concepts']}")
    report.append(f"   Diversity ratio: {topic_div['diversity_ratio']:.2%}")
    if topic_div['duplicates']:
        report.append(f"   ⚠️ Duplicates found: {len(topic_div['duplicates'])}")
        for concept, count in list(topic_div['duplicates'].items())[:5]:
            report.append(f"      - '{concept}': {count} times")
    report.append("")
    
    # 分布多样性
    dist_div = check_distribution_diversity(results)
    report.append(f"## Distribution Type Diversity {dist_div['status']}")
    report.append(f"   Unique distributions: {dist_div['unique_distributions']}")
    report.append(f"   Type coverage: {dist_div['type_coverage']:.2%}")
    report.append("   Distribution counts:")
    for dist_type, count in dist_div['distribution_counts'].items():
        report.append(f"      - {dist_type}: {count}")
    report.append("")
    
    # 实体数量多样性
    entity_div = check_entity_count_diversity(results)
    report.append(f"## Entity Count Diversity {entity_div['status']}")
    report.append(f"   Unique entity counts: {entity_div['unique_counts']}")
    report.append("   Count distribution:")
    for count, freq in sorted(entity_div['count_distribution'].items()):
        report.append(f"      - {count} entities: {freq} samples")
    report.append("")
    
    # 数值范围多样性
    value_div = check_value_range_diversity(results)
    report.append(f"## Value Range Diversity {value_div['status']}")
    report.append("   Scale distribution:")
    for scale, count in value_div['scale_distribution'].items():
        report.append(f"      - {scale}: {count} samples")
    report.append("")
    
    # 总体评估
    report.append("=" * 60)
    report.append("OVERALL ASSESSMENT")
    report.append("=" * 60)
    
    all_good = all([
        topic_div['diversity_ratio'] > 0.95,
        dist_div['type_coverage'] >= 0.6,
        entity_div['unique_counts'] >= 3
    ])
    
    if all_good:
        report.append("✅ Diversity levels are GOOD - low risk of model collapse")
    else:
        report.append("⚠️ Diversity could be improved:")
        if topic_div['diversity_ratio'] <= 0.95:
            report.append("   - Consider increasing temperature for Node A")
        if dist_div['type_coverage'] < 0.6:
            report.append("   - Enhance Node B prompt to encourage distribution variety")
        if entity_div['unique_counts'] < 3:
            report.append("   - Add entity count variation to Node B prompt")
    
    return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description="Check diversity of generated metadata")
    parser.add_argument("--input", "-i", required=True, help="Input JSON file")
    parser.add_argument("--report", "-r", help="Output report file (optional, prints to stdout if not specified)")
    
    args = parser.parse_args()
    
    # 加载数据
    with open(args.input, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    # 生成报告
    report_text = generate_report(results)
    
    # 输出
    if args.report:
        with open(args.report, 'w', encoding='utf-8') as f:
            f.write(report_text)
        print(f"Report saved to: {args.report}")
    else:
        print(report_text)


if __name__ == "__main__":
    main()
