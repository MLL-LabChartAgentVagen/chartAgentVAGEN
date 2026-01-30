"""
Chart QA Evaluation Runner
==========================

Command-line interface for running chart QA evaluations on VLMs.

Setup:
    1. Install dependencies: pip install -r requirements.txt
    2. Configure API key in .env file:
       GEMINI_API_KEY=your-gemini-key-here
       # or
       OPENAI_API_KEY=your-openai-key-here

Usage:
    # Run full evaluation with Gemini
    python evaluation_runner.py --provider gemini-native
    
    # Run with specific model
    python evaluation_runner.py --provider openai --model gpt-4o
    
    # Limit number of evaluations
    python evaluation_runner.py --count 10
    
    # Filter by difficulty level
    python evaluation_runner.py --level 1
    
    # Filter by QA type
    python evaluation_runner.py --qa-type simple_min
    
    # Specify custom data and output paths
    python evaluation_runner.py --data ./data/evaluation_data.json --output ./results/my_results.json

Author: ChartAgentVAGEN Team
Version: 1.0.0
"""

import json
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Install with: pip install python-dotenv")
    print("Falling back to system environment variables...")


# =============================================================================
# LLM CONFIGURATION (Reuse from example_runner.py)
# =============================================================================

# Provider configuration mapping
PROVIDER_CONFIGS = {
    "openai": {
        "env_model_key": "OPENAI_MODEL",
        "default_model": "gpt-4o",
        "env_api_key": "OPENAI_API_KEY",
        "model_patterns": ["gpt", "o1"],
    },
    "gemini": {
        "env_model_key": "GEMINI_MODEL",
        "default_model": "gemini-2.0-flash",
        "env_api_key": "GEMINI_API_KEY",
        "model_patterns": ["gemini"],
    },
    "gemini-native": {
        "env_model_key": "GEMINI_MODEL",
        "default_model": "gemini-2.0-flash",
        "env_api_key": "GEMINI_API_KEY",
        "model_patterns": ["gemini"],
    },
    "azure": {
        "env_model_key": "AZURE_OPENAI_MODEL",
        "default_model": "gpt-4o",
        "env_api_key": "AZURE_OPENAI_API_KEY",
        "model_patterns": ["gpt"],
    },
}

DEFAULT_PROVIDER = "gemini-native"


def infer_provider_from_model(model_name: str) -> str:
    """Infer provider from model name"""
    model_lower = model_name.lower()
    
    for provider, config in PROVIDER_CONFIGS.items():
        for pattern in config["model_patterns"]:
            if pattern in model_lower:
                return provider
    
    return DEFAULT_PROVIDER


def resolve_llm_config(args) -> tuple:
    """
    Unified LLM configuration resolver. Returns (provider, model, api_key)
    """
    # Step 1: Determine provider
    if args.provider and args.provider != "auto":
        provider = args.provider
    elif args.model:
        provider = infer_provider_from_model(args.model)
    else:
        provider = DEFAULT_PROVIDER
    
    # Validate provider support
    if provider not in PROVIDER_CONFIGS:
        raise ValueError(
            f"Unsupported provider: {provider}\n"
            f"Supported options: {', '.join(PROVIDER_CONFIGS.keys())}"
        )
    
    # Get provider configuration
    config = PROVIDER_CONFIGS[provider]
    
    # Step 2: Determine model
    if args.model:
        model = args.model
    else:
        model = os.environ.get(config["env_model_key"], config["default_model"])
    
    # Step 3: Determine api_key
    if args.api_key:
        api_key = args.api_key
    else:
        api_key = os.environ.get(config["env_api_key"])
    
    return provider, model, api_key


# =============================================================================
# EVALUATION RUNNER
# =============================================================================

class ChartQAEvaluationRunner:
    """
    评估 Pipeline 运行器
    
    封装了数据加载、pipeline 执行和结果保存的完整流程
    """
    
    def __init__(self, llm_client, verbose: bool = True, log_file: Optional[str] = None, debug: bool = False):
        """
        Args:
            llm_client: LLMClient 实例
            verbose: 是否输出详细日志
            log_file: 日志文件路径（可选）
            debug: 是否启用详细的 API 调试信息
        """
        self.llm = llm_client
        self.verbose = verbose
        self.log_file = log_file
        self.log_file_handle = None
        self.debug = debug
        
        # 打开日志文件
        if self.log_file:
            Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)
            self.log_file_handle = open(self.log_file, 'w', encoding='utf-8')
            self._write_log_header()
        
        # 延迟导入 pipeline
        from evaluation_pipeline import (
            ChartQAEvaluationPipeline, 
            extend_llm_client_with_vision
        )
        
        # 扩展 LLM 客户端以支持多模态
        extended_llm = extend_llm_client_with_vision(llm_client, debug=debug)
        
        self.pipeline = ChartQAEvaluationPipeline(
            extended_llm,
            config={"data_dir": "."}
        )
    
    def _write_log_header(self):
        """写入日志文件头部信息"""
        if self.log_file_handle:
            header = f"""Chart QA Evaluation Log
{'=' * 80}
Model: {getattr(self.llm, 'model', 'unknown')}
Provider: {getattr(self.llm, 'provider', 'unknown')}
Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 80}

"""
            self.log_file_handle.write(header)
            self.log_file_handle.flush()
    
    def log(self, message: str):
        """输出日志到控制台和文件"""
        if self.verbose:
            timestamp = datetime.now().strftime('%H:%M:%S')
            output = f"[{timestamp}] {message}"
            print(output)
            
            # 同时写入日志文件
            if self.log_file_handle:
                self.log_file_handle.write(output + "\n")
                self.log_file_handle.flush()
    
    def print_to_log(self, message: str):
        """直接打印到控制台和日志文件（不带时间戳）"""
        print(message)
        if self.log_file_handle:
            self.log_file_handle.write(message + "\n")
            self.log_file_handle.flush()
    
    def close_log(self):
        """关闭日志文件"""
        if self.log_file_handle:
            # 写入结束信息
            footer = f"""
{'=' * 80}
End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 80}
"""
            self.log_file_handle.write(footer)
            self.log_file_handle.close()
            self.log_file_handle = None
    
    def load_evaluation_data(self, data_path: str) -> list[dict]:
        """
        加载评估数据
        
        Args:
            data_path: JSON 文件路径
        
        Returns:
            QA 条目列表
        """
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # JSON 可能是 dict 格式，转换为 list
        if isinstance(data, dict):
            return list(data.values())
        return data
    
    def filter_data(
        self, 
        data: list[dict], 
        level: Optional[str] = None,
        qa_type: Optional[str] = None,
        chart_type: Optional[str] = None,
        count: Optional[int] = None
    ) -> list[dict]:
        """
        筛选数据
        
        Args:
            data: 原始数据列表
            level: 筛选难度级别 (1, 2, 3)
            qa_type: 筛选问题类型 (部分匹配)
            chart_type: 筛选图表类型 (bar, scatter, pie)
            count: 限制数量
        
        Returns:
            筛选后的数据列表
        """
        filtered = data
        
        if level:
            filtered = [
                d for d in filtered 
                if str(d.get("curriculum_level", "")) == str(level)
            ]
        
        if qa_type:
            filtered = [
                d for d in filtered 
                if qa_type.lower() in d.get("qa_type", "").lower()
            ]
        
        if chart_type:
            filtered = [
                d for d in filtered 
                if d.get("chart_type", "").lower() == chart_type.lower()
            ]
        
        if count and count > 0:
            filtered = filtered[:count]
        
        return filtered
    
    def run(
        self, 
        # data_path: str = "./data/evaluation_data.json",
        # output_path: str = "./results/evaluation_results.json",
        data_path: str = "./data_files/bar__meta_qa_data.json",
        output_path: str = "./results/evaluation_results.json",
        level: Optional[str] = None,
        qa_type: Optional[str] = None,
        chart_type: Optional[str] = None,
        count: Optional[int] = None
    ) -> dict:
        """
        运行评估
        
        Args:
            data_path: 评估数据路径
            output_path: 结果输出路径
            level: 筛选难度级别
            qa_type: 筛选问题类型
            chart_type: 筛选图表类型
            count: 限制评估数量
        
        Returns:
            包含 metadata, metrics, results 的字典
        """
        import time
        
        # 加载数据
        self.log(f"Loading data from {data_path}...")
        data = self.load_evaluation_data(data_path)
        self.log(f"Loaded {len(data)} QA entries")
        
        # 筛选数据
        data = self.filter_data(data, level, qa_type, chart_type, count)
        self.log(f"Evaluating {len(data)} entries after filtering")
        
        if len(data) == 0:
            self.log("No data to evaluate after filtering!")
            return {"error": "No data after filtering"}
        
        # 进度回调
        def progress_callback(current: int, total: int, state: dict):
            status = "✓" if state["is_correct"] else "✗"
            vlm_preview = state["vlm_answer"][:30] if state["vlm_answer"] else "(empty)"
            gt_preview = state["ground_truth_answer"][:30]
            self.log(f"  [{current}/{total}] {status} {state['qa_id']}")
            if self.verbose:
                self.log(f"      VLM: {vlm_preview}... | GT: {gt_preview}...")
        
        # 运行评估
        start_time = time.time()
        self.log("Starting evaluation...")
        self.log("-" * 50)
        
        results = self.pipeline.run_batch(data, progress_callback)
        
        total_time = time.time() - start_time
        self.log("-" * 50)
        self.log(f"Evaluation completed in {total_time:.1f}s")
        
        # 计算指标
        metrics = self.pipeline.compute_metrics(results)
        metrics["total_time_seconds"] = total_time
        
        # 构建输出
        output = {
            "metadata": {
                "model": getattr(self.llm, 'model', 'unknown'),
                "provider": getattr(self.llm, 'provider', 'unknown'),
                "timestamp": datetime.now().isoformat(),
                "data_path": data_path,
                "total_questions": len(data),
                "filters": {
                    "level": level,
                    "qa_type": qa_type,
                    "chart_type": chart_type,
                    "count": count
                }
            },
            "metrics": metrics,
            "results": [dict(r) for r in results]
        }
        
        # 保存结果
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        self.log(f"Results saved to {output_path}")
        
        return output
    
    def print_summary(self, metrics: dict):
        """
        打印评估摘要（同时输出到控制台和日志文件）
        
        Args:
            metrics: 指标字典
        """
        self.print_to_log("\n" + "=" * 60)
        self.print_to_log("                  EVALUATION SUMMARY")
        self.print_to_log("=" * 60)
        
        # 总体指标
        self.print_to_log(f"\n📊 Overall Performance:")
        self.print_to_log(f"   Accuracy:        {metrics.get('overall_accuracy', 0):.2%}")
        self.print_to_log(f"   Total Questions: {metrics.get('total_questions', 0)}")
        self.print_to_log(f"   Correct:         {metrics.get('correct_answers', 0)}")
        self.print_to_log(f"   Incorrect:       {metrics.get('incorrect_answers', 0)}")
        self.print_to_log(f"   Avg Similarity:  {metrics.get('average_similarity_score', 0):.3f}")
        self.print_to_log(f"   Avg Latency:     {metrics.get('average_latency_ms', 0):.0f}ms")
        
        if metrics.get('total_time_seconds'):
            self.print_to_log(f"   Total Time:      {metrics['total_time_seconds']:.1f}s")
        
        # 按难度级别
        accuracy_by_level = metrics.get('accuracy_by_level', {})
        count_by_level = metrics.get('count_by_level', {})
        if accuracy_by_level:
            self.print_to_log(f"\n📈 Accuracy by Difficulty Level:")
            for level in sorted(accuracy_by_level.keys()):
                acc = accuracy_by_level[level]
                cnt = count_by_level.get(level, 0)
                self.print_to_log(f"   Level {level}: {acc:.2%} ({cnt} questions)")
        
        # 按问题类型 (Top 10)
        accuracy_by_type = metrics.get('accuracy_by_qa_type', {})
        count_by_type = metrics.get('count_by_qa_type', {})
        if accuracy_by_type:
            self.print_to_log(f"\n📋 Accuracy by QA Type (Top 10):")
            sorted_types = sorted(
                accuracy_by_type.items(),
                key=lambda x: (-x[1], x[0])  # 按准确率降序，然后按名称
            )[:10]
            for qa_type, acc in sorted_types:
                cnt = count_by_type.get(qa_type, 0)
                # 截断过长的类型名
                display_type = qa_type[:40] + "..." if len(qa_type) > 40 else qa_type
                self.print_to_log(f"   {display_type}: {acc:.2%} ({cnt})")
        
        # 匹配类型分布
        match_dist = metrics.get('match_type_distribution', {})
        if match_dist:
            self.print_to_log(f"\n🔍 Match Type Distribution:")
            for match_type, count in sorted(match_dist.items(), key=lambda x: -x[1]):
                self.print_to_log(f"   {match_type}: {count}")
        
        self.print_to_log("\n" + "=" * 60)


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Chart QA Evaluation Pipeline Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full evaluation with Gemini
  python evaluation_runner.py --provider gemini-native

  # Run with OpenAI GPT-4o
  python evaluation_runner.py --provider openai --model gpt-4o

  # Evaluate only 10 questions
  python evaluation_runner.py --count 10

  # Filter by difficulty level
  python evaluation_runner.py --level 1

  # Filter by QA type (partial match)
  python evaluation_runner.py --qa-type simple_min

  # Combine filters
  python evaluation_runner.py --level 1 --qa-type simple --count 20

  # Custom paths
  python evaluation_runner.py --data ./my_data.json --output ./my_results.json
        """
    )
    
    # LLM 配置参数
    parser.add_argument(
        "--api-key",
        help="API key (or set GEMINI_API_KEY/OPENAI_API_KEY env var)"
    )
    
    parser.add_argument(
        "--model", "-m",
        help="Model name (e.g., gemini-2.0-flash, gpt-4o)"
    )
    
    parser.add_argument(
        "--provider", "-p",
        help="LLM provider",
        choices=["openai", "gemini", "gemini-native", "azure"],
        default="gemini-native"
    )
    
    # 数据参数
    parser.add_argument(
        "--data", "-d",
        # default="./data/evaluation_data.json",
        default= "./data_files/bar__meta_qa_data.json",
        help="Path to evaluation data JSON (default: ./data/evaluation_data.json)"

    )
    
    parser.add_argument(
        "--output", "-o",
        # default="./results/evaluation_results.json",
        default="./results/evaluation_results.json", 
        help="Output path for results (default: ./results/evaluation_results.json)"
    )
    
    # 筛选参数
    parser.add_argument(
        "--count", "-n",
        type=int,
        help="Limit number of evaluations"
    )
    
    parser.add_argument(
        "--level", "-l",
        choices=["1", "2", "3"],
        help="Filter by curriculum level (1=easy, 2=medium, 3=hard)"
    )
    
    parser.add_argument(
        "--qa-type", "-t",
        help="Filter by QA type (partial match, e.g., 'simple_min', 'nested')"
    )
    
    parser.add_argument(
        "--chart-type", "-c",
        choices=["bar", "scatter", "pie"],
        help="Filter by chart type"
    )
    
    # 其他参数
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress verbose output"
    )
    
    parser.add_argument(
        "--no-summary",
        action="store_true",
        help="Don't print summary after evaluation"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable detailed debug logging for API calls"
    )
    
    parser.add_argument(
        "--log-dir",
        default="./results/logs",
        help="Directory to save log files (default: ./results/logs)"
    )
    
    args = parser.parse_args()
    
    # 解析 LLM 配置
    try:
        provider, model, api_key = resolve_llm_config(args)
    except ValueError as e:
        print(f"ERROR: {e}")
        return 1
    
    # 检查 API key
    if not api_key:
        config = PROVIDER_CONFIGS.get(provider, {})
        env_key_name = config.get('env_api_key', 'API_KEY')
        
        print("ERROR: API key not found!")
        print(f"       Provider '{provider}' requires: {env_key_name}")
        print("")
        print("       Set it in one of these ways:")
        print("       1. Use --api-key command line argument")
        print(f"       2. Set {env_key_name} in .env file or environment variable")
        print("")
        print("       Example .env file:")
        print(f"       {env_key_name}=your-key-here")
        return 1
    
    # 检查数据文件是否存在
    if not Path(args.data).exists():
        print(f"ERROR: Data file not found: {args.data}")
        return 1
    
    # 生成日志文件名：模型名_日期时间.txt
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    # 清理模型名中的特殊字符
    clean_model_name = model.replace("/", "_").replace(":", "_").replace("\\", "_")
    log_filename = f"{clean_model_name}_{timestamp}.txt"
    log_path = Path(args.log_dir) / log_filename
    
    # 创建 LLM 客户端
    print(f"Initializing LLM client...")
    print(f"  Provider: {provider}")
    print(f"  Model: {model}")
    print(f"  Log file: {log_path}")
    
    try:
        # 导入 LLMClient
        from generation_pipeline import LLMClient
        
        llm = LLMClient(
            api_key=api_key,
            model=model,
            provider=provider
        )
        print(f"  Detected provider: {llm.provider}")
        print("")
    except ImportError as e:
        print(f"ERROR: Failed to import LLMClient: {e}")
        print("       Make sure generation_pipeline.py is in the same directory")
        return 1
    except Exception as e:
        print(f"ERROR: Failed to create LLM client: {e}")
        return 1
    
    # 运行评估（带日志文件）
    runner = ChartQAEvaluationRunner(
        llm, 
        verbose=not args.quiet,
        log_file=str(log_path),
        debug=args.debug
    )
    
    try:
        output = runner.run(
            data_path=args.data,
            output_path=args.output,
            level=args.level,
            qa_type=args.qa_type,
            chart_type=args.chart_type,
            count=args.count
        )
    except Exception as e:
        print(f"ERROR: Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        runner.close_log()  # 确保关闭日志文件
        return 1
    
    # 打印摘要
    if not args.no_summary and "metrics" in output:
        runner.print_summary(output["metrics"])
    
    # 关闭日志文件
    runner.close_log()
    runner.log(f"\nLog saved to: {log_path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
