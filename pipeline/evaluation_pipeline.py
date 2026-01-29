"""
Chart QA Evaluation Pipeline
=============================

A two-node pipeline for evaluating VLM (Vision-Language Model) performance
on chart comprehension tasks.

Architecture:
    Node A: VLM Answer Generator - Send chart image + question to VLM
    Node B: Answer Evaluator - Compare VLM answer with ground truth

Author: ChartAgentVAGEN Team
Version: 1.0.0
"""

import json
import base64
import time
from typing import TypedDict, Optional, Literal, Union
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from difflib import SequenceMatcher


# =============================================================================
# SECTION 1: STATE DEFINITIONS
# =============================================================================

class EvaluationState(TypedDict):
    """Evaluation pipeline 状态对象"""
    # 输入数据
    qa_id: str
    question: str
    ground_truth_answer: str
    img_path: str
    chart_type: str
    category: str
    qa_type: str
    curriculum_level: str
    
    # Node A 输出
    vlm_answer: str
    vlm_raw_response: str
    
    # Node B 输出
    is_correct: bool
    match_type: str  # "exact", "numeric_close", "partial", "incorrect"
    similarity_score: float
    evaluation_details: dict
    
    # 元数据
    timestamp: str
    model_name: str
    latency_ms: float


# =============================================================================
# SECTION 2: SYSTEM PROMPTS
# =============================================================================

PROMPT_NODE_A_VLM_QA = PROMPT_NODE_A_VLM_QA = """You are a chart comprehension expert. Analyze the provided chart image and answer the question accurately.

## Instructions
1. Carefully examine the chart image
2. Read and understand the question
3. Extract relevant information from the chart
4. Provide a precise, concise answer

## Answer Format Rules
- For numeric answers: Provide the exact number with appropriate decimal places (e.g., "42.50" or "287.60")
- For multiple values: Use comma-separated format with spaces (e.g., "18.4, 35.2, 20.1")
- For counts: Provide integer only (e.g., "3" or "0")
- Do NOT include units, explanations, or any other text
- Do NOT add percentage signs (%) or currency symbols

## Examples
- Question: "What is the highest value?" → Answer: "42.50"
- Question: "What is the sum of all values?" → Answer: "287.60"
- Question: "How many items are above 30?" → Answer: "5"
- Question: "What are all the values?" → Answer: "18.4, 35.2, 20.1, 42.5"

Respond with ONLY the answer value, nothing else."""

# """Answer this question about the chart in one short phrase."""

# =============================================================================
# SECTION 3: NODE IMPLEMENTATIONS
# =============================================================================

class NodeA_VLMAnswerGenerator:
    """
    Node A: VLM 答案生成器
    
    职责:
    - 将图表图像和问题发送给 VLM
    - 解析 VLM 的回答
    - 提取结构化答案
    """
    
    def __init__(self, llm_client, data_dir: str = "."):
        """
        Args:
            llm_client: LLMClient 实例 (需支持多模态)
            data_dir: 数据根目录，用于解析相对路径
        """
        self.llm = llm_client
        self.data_dir = Path(data_dir)
    
    def load_image_base64(self, img_path: str) -> str:
        """
        加载图像并转换为 base64
        
        Args:
            img_path: 图像路径 (支持相对路径如 "./data/imgs/...")
        
        Returns:
            Base64 编码的图像字符串
        """
        # 处理相对路径
        if img_path.startswith("./"):
            full_path = self.data_dir / img_path[2:]
        else:
            full_path = Path(img_path)
        
        if not full_path.exists():
            raise FileNotFoundError(f"Image not found: {full_path}")
        
        with open(full_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    
    def validate_output(self, response: str) -> tuple[bool, list[str]]:
        """验证 VLM 输出"""
        errors = []
        if not response or not response.strip():
            errors.append("Empty response from VLM")
        return len(errors) == 0, errors
    
    def __call__(self, state: EvaluationState) -> EvaluationState:
        """
        执行 Node A: 调用 VLM 获取答案
        
        Args:
            state: 当前 pipeline 状态
        
        Returns:
            更新后的状态
        """
        start_time = time.time()
        
        # 加载图像
        try:
            image_base64 = self.load_image_base64(state["img_path"])
        except FileNotFoundError as e:
            state["vlm_answer"] = ""
            state["vlm_raw_response"] = f"Error: {e}"
            state["latency_ms"] = 0
            return state
        
        # 调用 VLM API (支持多模态)
        try:
            response = self.llm.generate_with_image(
                system=PROMPT_NODE_A_VLM_QA,
                user=state["question"],
                image_base64=image_base64,
                temperature=0.1,  # 低温度以获得更确定的答案
                # max_tokens=256
                max_tokens=8000
            )
        except Exception as e:
            # 打印详细的异常信息
            import traceback
            print(f"\n{'!'*80}")
            print(f"[ERROR] API 调用失败!")
            print(f"[ERROR] 异常类型: {type(e).__name__}")
            print(f"[ERROR] 异常信息: {e}")
            print(f"[ERROR] 完整堆栈跟踪:")
            traceback.print_exc()
            print(f"{'!'*80}\n")
            
            state["vlm_answer"] = ""
            state["vlm_raw_response"] = f"API Error: {e}"
            state["latency_ms"] = (time.time() - start_time) * 1000
            return state
        
        latency = (time.time() - start_time) * 1000
        
        # 清理答案
        vlm_answer = response.strip() if response else ""
        
        # 验证输出
        is_valid, errors = self.validate_output(vlm_answer)
        if not is_valid:
            print(f"Warning: VLM output validation failed: {errors}")
        
        # 更新状态
        state["vlm_answer"] = vlm_answer
        state["vlm_raw_response"] = response or ""
        state["latency_ms"] = latency
        state["model_name"] = getattr(self.llm, 'model', 'unknown')
        
        return state


class NodeB_AnswerEvaluator:
    """
    Node B: 答案评估器
    
    职责:
    - 比对 VLM 答案和 ground truth
    - 支持多种匹配模式 (精确匹配、数值近似、部分匹配)
    - 计算评估指标
    """
    
    def __init__(self, tolerance: float = 0.01):
        """
        Args:
            tolerance: 数值比较的相对容差 (默认 1%)
        """
        self.tolerance = tolerance
    
    def normalize_answer(self, answer: str) -> str:
        """
        标准化答案格式
        
        - 去除首尾空格
        - 转小写
        - 去除常见单位符号
        """
        if not answer:
            return ""
        normalized = answer.strip().lower()
        # 去除单位符号
        for char in ["%", "$", "€", "£", "¥"]:
            normalized = normalized.replace(char, "")
        return normalized.strip()
    
    def parse_numeric(self, value: str) -> Optional[float]:
        """
        尝试将字符串解析为数值
        
        Returns:
            解析后的浮点数，或 None 如果无法解析
        """
        try:
            # 处理可能的千分位分隔符
            cleaned = value.replace(",", "").replace(" ", "")
            return float(cleaned)
        except (ValueError, AttributeError):
            return None
    
    def parse_numeric_list(self, value: str) -> Optional[list[float]]:
        """
        尝试将字符串解析为数值列表
        
        支持格式: "1.2, 3.4, 5.6" 或 "1.2,3.4,5.6"
        
        Returns:
            浮点数列表，或 None 如果无法解析
        """
        try:
            # 按逗号分割
            parts = [p.strip() for p in value.split(",")]
            if len(parts) <= 1:
                return None
            return [float(p.replace(" ", "")) for p in parts]
        except (ValueError, AttributeError):
            return None
    
    def compare_numeric(self, pred: float, truth: float) -> bool:
        """
        数值比较 (考虑相对容差)
        
        Args:
            pred: 预测值
            truth: 真实值
        
        Returns:
            是否在容差范围内
        """
        if truth == 0:
            return abs(pred) < self.tolerance
        relative_error = abs(pred - truth) / abs(truth)
        return relative_error <= self.tolerance
    
    def compare_numeric_lists(
        self, 
        pred: list[float], 
        truth: list[float]
    ) -> tuple[bool, float]:
        """
        比较数值列表
        
        Args:
            pred: 预测的数值列表
            truth: 真实的数值列表
        
        Returns:
            (是否完全匹配, 元素级准确率)
        """
        if len(pred) != len(truth):
            # 长度不匹配，尝试找最大重叠
            matches = 0
            for p in pred:
                for t in truth:
                    if self.compare_numeric(p, t):
                        matches += 1
                        break
            accuracy = matches / max(len(truth), 1)
            return False, accuracy
        
        # 长度匹配，逐元素比较
        matches = sum(1 for p, t in zip(pred, truth) if self.compare_numeric(p, t))
        accuracy = matches / len(truth)
        return accuracy == 1.0, accuracy
    
    def evaluate(self, vlm_answer: str, ground_truth: str) -> dict:
        """
        评估单个答案
        
        Args:
            vlm_answer: VLM 生成的答案
            ground_truth: 标准答案
        
        Returns:
            评估结果字典:
            - is_correct: bool
            - match_type: str
            - similarity_score: float
            - details: dict
        """
        pred_norm = self.normalize_answer(vlm_answer)
        truth_norm = self.normalize_answer(ground_truth)
        
        # 处理空答案
        if not pred_norm:
            return {
                "is_correct": False,
                "match_type": "empty_response",
                "similarity_score": 0.0,
                "details": {"method": "empty_check", "error": "VLM returned empty answer"}
            }
        
        # 1. 精确字符串匹配
        if pred_norm == truth_norm:
            return {
                "is_correct": True,
                "match_type": "exact",
                "similarity_score": 1.0,
                "details": {"method": "exact_string_match"}
            }
        
        # 2. 尝试数值列表比较 (优先，因为更复杂)
        pred_list = self.parse_numeric_list(pred_norm)
        truth_list = self.parse_numeric_list(truth_norm)
        
        if pred_list is not None and truth_list is not None:
            is_match, accuracy = self.compare_numeric_lists(pred_list, truth_list)
            return {
                "is_correct": is_match,
                "match_type": "list_match" if is_match else "list_partial",
                "similarity_score": accuracy,
                "details": {
                    "method": "list_comparison",
                    "predicted_values": pred_list,
                    "ground_truth_values": truth_list,
                    "predicted_count": len(pred_list),
                    "ground_truth_count": len(truth_list),
                    "element_accuracy": accuracy
                }
            }
        
        # 3. 单数值比较
        pred_num = self.parse_numeric(pred_norm)
        truth_num = self.parse_numeric(truth_norm)
        
        if pred_num is not None and truth_num is not None:
            is_close = self.compare_numeric(pred_num, truth_num)
            if truth_num != 0:
                relative_error = abs(pred_num - truth_num) / abs(truth_num)
            else:
                relative_error = abs(pred_num)
            
            return {
                "is_correct": is_close,
                "match_type": "numeric_close" if is_close else "numeric_mismatch",
                "similarity_score": max(0, 1 - relative_error),
                "details": {
                    "method": "numeric_comparison",
                    "predicted": pred_num,
                    "ground_truth": truth_num,
                    "relative_error": relative_error,
                    "tolerance": self.tolerance
                }
            }
        
        # 4. 字符串相似度 (fallback)
        similarity = SequenceMatcher(None, pred_norm, truth_norm).ratio()
        
        # 高相似度可能表示格式问题
        is_highly_similar = similarity > 0.9
        
        return {
            "is_correct": False,
            "match_type": "string_similar" if is_highly_similar else "string_mismatch",
            "similarity_score": similarity,
            "details": {
                "method": "string_similarity",
                "similarity_ratio": similarity,
                "predicted_normalized": pred_norm[:100],  # 截断防止过长
                "ground_truth_normalized": truth_norm[:100]
            }
        }
    
    def __call__(self, state: EvaluationState) -> EvaluationState:
        """
        执行 Node B: 评估答案
        
        Args:
            state: 当前 pipeline 状态
        
        Returns:
            更新后的状态
        """
        result = self.evaluate(state["vlm_answer"], state["ground_truth_answer"])
        
        state["is_correct"] = result["is_correct"]
        state["match_type"] = result["match_type"]
        state["similarity_score"] = result["similarity_score"]
        state["evaluation_details"] = result["details"]
        
        return state


# =============================================================================
# SECTION 4: PIPELINE ORCHESTRATOR
# =============================================================================

class ChartQAEvaluationPipeline:
    """
    Chart QA 评估 Pipeline
    
    两节点工作流:
    Node A: VLM Answer Generation (图像 + 问题 → VLM 答案)
      ↓
    Node B: Answer Evaluation (VLM 答案 vs Ground Truth)
    
    Usage:
        from pipeline_architecture import LLMClient
        
        llm = LLMClient(api_key="...", model="gemini-2.0-flash", provider="gemini-native")
        pipeline = ChartQAEvaluationPipeline(llm)
        
        result = pipeline.run_single(qa_entry)
        metrics = pipeline.compute_metrics(results)
    """
    
    def __init__(self, llm_client, config: Optional[dict] = None):
        """
        初始化 Pipeline
        
        Args:
            llm_client: LLMClient 实例 (需要支持 generate_with_image 方法)
            config: 可选配置
                - data_dir: 数据目录 (默认 ".")
                - tolerance: 数值比较容差 (默认 0.01)
        """
        self.config = config or {}
        self.llm = llm_client
        
        # 初始化 Nodes
        self.node_a = NodeA_VLMAnswerGenerator(
            llm_client, 
            data_dir=self.config.get("data_dir", ".")
        )
        self.node_b = NodeB_AnswerEvaluator(
            tolerance=self.config.get("tolerance", 0.01)
        )
    
    def create_initial_state(self, qa_entry: dict) -> EvaluationState:
        """
        从 QA 条目创建初始状态
        
        Args:
            qa_entry: 来自 evaluation_data.json 的单个条目
        
        Returns:
            初始化的 EvaluationState
        """
        return EvaluationState(
            # 输入数据
            qa_id=qa_entry.get("qa_id", ""),
            question=qa_entry.get("question", ""),
            ground_truth_answer=str(qa_entry.get("answer", "")),
            img_path=qa_entry.get("img_path", ""),
            chart_type=qa_entry.get("chart_type", "bar"),
            category=qa_entry.get("category", ""),
            qa_type=qa_entry.get("qa_type", ""),
            curriculum_level=str(qa_entry.get("curriculum_level", "1")),
            # Node A 输出 (待填充)
            vlm_answer="",
            vlm_raw_response="",
            # Node B 输出 (待填充)
            is_correct=False,
            match_type="",
            similarity_score=0.0,
            evaluation_details={},
            # 元数据
            timestamp=datetime.now().isoformat(),
            model_name=getattr(self.llm, 'model', 'unknown'),
            latency_ms=0.0
        )
    
    def run_single(self, qa_entry: dict) -> EvaluationState:
        """
        运行单个 QA 评估
        
        Args:
            qa_entry: 来自 evaluation_data.json 的单个条目
        
        Returns:
            完成评估的 EvaluationState
        """
        # 创建初始状态
        state = self.create_initial_state(qa_entry)
        
        # Node A: 生成 VLM 答案
        state = self.node_a(state)
        
        # Node B: 评估答案
        state = self.node_b(state)
        
        return state
    
    def run_batch(
        self, 
        qa_entries: list[dict],
        progress_callback: Optional[callable] = None
    ) -> list[EvaluationState]:
        """
        批量运行评估
        
        Args:
            qa_entries: QA 条目列表
            progress_callback: 可选的进度回调函数 (current, total, state)
        
        Returns:
            EvaluationState 列表
        """
        results = []
        total = len(qa_entries)
        
        for i, entry in enumerate(qa_entries):
            try:
                result = self.run_single(entry)
                results.append(result)
                
                if progress_callback:
                    progress_callback(i + 1, total, result)
                    
            except Exception as e:
                print(f"Error evaluating {entry.get('qa_id', 'unknown')}: {e}")
                # 创建一个失败的结果
                failed_state = self.create_initial_state(entry)
                failed_state["vlm_answer"] = ""
                failed_state["vlm_raw_response"] = f"Pipeline Error: {e}"
                failed_state["match_type"] = "error"
                failed_state["evaluation_details"] = {"error": str(e)}
                results.append(failed_state)
                
        return results
    
    def compute_metrics(self, results: list[EvaluationState]) -> dict:
        """
        计算汇总指标
        
        Args:
            results: EvaluationState 列表
        
        Returns:
            指标字典:
            - overall_accuracy: 总体准确率
            - total_questions: 问题总数
            - correct_answers: 正确数
            - accuracy_by_qa_type: 按问题类型的准确率
            - accuracy_by_level: 按难度级别的准确率
            - match_type_distribution: 匹配类型分布
        """
        total = len(results)
        if total == 0:
            return {"error": "No results to compute metrics"}
        
        correct = sum(1 for r in results if r["is_correct"])
        
        # 按问题类型分组
        by_qa_type: dict[str, dict] = {}
        for r in results:
            qa_type = r["qa_type"] or "unknown"
            if qa_type not in by_qa_type:
                by_qa_type[qa_type] = {"total": 0, "correct": 0}
            by_qa_type[qa_type]["total"] += 1
            if r["is_correct"]:
                by_qa_type[qa_type]["correct"] += 1
        
        # 按难度级别分组
        by_level: dict[str, dict] = {}
        for r in results:
            level = str(r["curriculum_level"]) or "unknown"
            if level not in by_level:
                by_level[level] = {"total": 0, "correct": 0}
            by_level[level]["total"] += 1
            if r["is_correct"]:
                by_level[level]["correct"] += 1
        
        # 匹配类型分布
        match_types: dict[str, int] = {}
        for r in results:
            mt = r["match_type"] or "unknown"
            match_types[mt] = match_types.get(mt, 0) + 1
        
        # 计算平均延迟 (排除错误情况)
        valid_latencies = [r["latency_ms"] for r in results if r["latency_ms"] > 0]
        avg_latency = sum(valid_latencies) / len(valid_latencies) if valid_latencies else 0
        
        # 计算平均相似度
        avg_similarity = sum(r["similarity_score"] for r in results) / total
        
        return {
            "overall_accuracy": correct / total,
            "total_questions": total,
            "correct_answers": correct,
            "incorrect_answers": total - correct,
            "average_similarity_score": avg_similarity,
            "average_latency_ms": avg_latency,
            "accuracy_by_qa_type": {
                k: v["correct"] / v["total"] if v["total"] > 0 else 0
                for k, v in by_qa_type.items()
            },
            "count_by_qa_type": {
                k: v["total"] for k, v in by_qa_type.items()
            },
            "accuracy_by_level": {
                k: v["correct"] / v["total"] if v["total"] > 0 else 0
                for k, v in by_level.items()
            },
            "count_by_level": {
                k: v["total"] for k, v in by_level.items()
            },
            "match_type_distribution": match_types
        }


# =============================================================================
# SECTION 5: LLM CLIENT EXTENSION (Multimodal Support)
# =============================================================================

def extend_llm_client_with_vision(llm_client):
    """
    为 LLMClient 添加多模态支持
    
    如果 LLMClient 没有 generate_with_image 方法，则动态添加
    
    Args:
        llm_client: 原始 LLMClient 实例
    
    Returns:
        扩展后的 LLMClient
    """
    if hasattr(llm_client, 'generate_with_image'):
        return llm_client
    
    def generate_with_image(
        self,
        system: str,
        user: str,
        image_base64: str,
        temperature: float = 0.3,
        max_tokens: int = 5000 # FIXME： originally 1024
    ) -> str:
        """
        带图像的多模态生成
        
        Args:
            system: System prompt
            user: User question
            image_base64: Base64 encoded image
            temperature: 采样温度
            max_tokens: 最大输出长度
        
        Returns:
            生成的文本响应
        """
        self._ensure_client()
        
        if self.provider == "gemini-native":
            # Gemini native SDK 多模态调用
            from google.genai import types
            
            # 构建带图像的内容
            image_part = types.Part.from_bytes(
                data=base64.b64decode(image_base64),
                mime_type="image/png"
            )
            
            full_prompt = f"{system}\n\nQuestion: {user}"
            
            # 准备生成配置
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens
            }
            
            # 添加安全设置（设置为最宽松，用于调试和避免误拦截）
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
            
            print(f"\n{'='*80}")
            print(f"[DEBUG] 调用 Gemini API")
            print(f"[DEBUG] Model: {self.model}")
            print(f"[DEBUG] Temperature: {temperature}")
            print(f"[DEBUG] Max tokens: {max_tokens}")
            print(f"[DEBUG] Question: {user[:100]}...")
            
            # 构建 API 参数
            api_kwargs = {
                "model": self.model,
                "contents": [image_part, full_prompt],
                "config": generation_config
            }
            
            # 只有非 Gemini-3 模型才支持 safety_settings
            if not self.model.startswith("gemini-3"):
                api_kwargs["safety_settings"] = safety_settings
                print(f"[DEBUG] 使用 safety_settings (Gemini 2.x)")
            else:
                print(f"[DEBUG] 跳过 safety_settings (Gemini 3.x 不支持)")
            
            try:
                response = self._native_client.models.generate_content(**api_kwargs)
                print(f"[DEBUG] API 调用成功!")
            except Exception as api_error:
                print(f"[ERROR] API 调用失败!")
                print(f"[ERROR] 异常类型: {type(api_error).__name__}")
                print(f"[ERROR] 异常信息: {api_error}")
                import traceback
                traceback.print_exc()
                raise
            
            # 详细的响应检查和调试日志
            print(f"[DEBUG] Response type: {type(response)}")
            print(f"[DEBUG] Response object: {response}")
            print(f"[DEBUG] Has candidates: {hasattr(response, 'candidates')}")
            
            if hasattr(response, 'candidates'):
                print(f"[DEBUG] Candidates count: {len(response.candidates) if response.candidates else 0}")
                
                if not response.candidates:
                    print(f"[ERROR] Gemini 返回空 candidates!")
                    print(f"[ERROR] 完整响应: {response}")
                    raise ValueError(f"Gemini returned no candidates. Response: {response}")
                
                candidate = response.candidates[0]
                print(f"[DEBUG] Candidate type: {type(candidate)}")
                print(f"[DEBUG] Finish reason: {candidate.finish_reason}")
                print(f"[DEBUG] Has content: {hasattr(candidate, 'content')}")
                
                if candidate.finish_reason.name != "STOP":
                    print(f"[WARNING] Finish reason 不是 STOP: {candidate.finish_reason.name}")
                    # 对于新模型，某些 finish_reason 可能仍有内容，所以只警告不抛出异常
                
                if hasattr(candidate, 'content') and candidate.content:
                    print(f"[DEBUG] Content type: {type(candidate.content)}")
                    print(f"[DEBUG] Has parts: {hasattr(candidate.content, 'parts')}")
                    
                    if candidate.content.parts:
                        print(f"[DEBUG] Parts count: {len(candidate.content.parts)}")
                        first_part = candidate.content.parts[0]
                        print(f"[DEBUG] First part type: {type(first_part)}")
                        print(f"[DEBUG] First part has 'text': {hasattr(first_part, 'text')}")
                        
                        try:
                            text_content = first_part.text
                            print(f"[DEBUG] 成功获取 text 属性")
                        except Exception as text_error:
                            print(f"[ERROR] 获取 text 属性失败: {text_error}")
                            print(f"[DEBUG] First part 内容: {first_part}")
                            raise
                        
                        print(f"[DEBUG] Text content length: {len(text_content) if text_content else 0}")
                        print(f"[DEBUG] Text content preview: {text_content[:200] if text_content else '(empty)'}")
                        print(f"{'='*80}\n")
                        
                        if not text_content or not text_content.strip():
                            print(f"[ERROR] Gemini 返回的文本为空!")
                            raise ValueError("Gemini returned empty text content")
                        
                        return text_content
                    else:
                        print(f"[ERROR] Content.parts 为空!")
                        raise ValueError(f"Gemini returned empty content.parts. Response: {response}")
                else:
                    print(f"[ERROR] Candidate 没有 content!")
                    raise ValueError(f"Gemini candidate has no content. Response: {response}")
            else:
                print(f"[ERROR] Response 没有 candidates 属性!")
                # 尝试直接访问 .text 属性
                if hasattr(response, 'text'):
                    text = response.text
                    print(f"[DEBUG] 找到 response.text: {text[:200] if text else '(empty)'}")
                    if text and text.strip():
                        print(f"{'='*80}\n")
                        return text
                
                raise ValueError(f"Gemini response has no candidates attribute. Response: {response}")
        
        else:
            # OpenAI 兼容 API 多模态调用
            messages = [
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        },
                        {"type": "text", "text": user}
                    ]
                }
            ]
            
            kwargs = {
                "model": self.model,
                "messages": messages,
            }
            
            # 根据模型选择正确的 token 参数
            # GPT-5+, o1, o3 系列使用 max_completion_tokens
            if self.model.startswith("gpt-5") or self.model.startswith("o1") or self.model.startswith("o3"):
                kwargs["max_completion_tokens"] = max_tokens
                token_param_name = "max_completion_tokens"
            else:
                kwargs["max_tokens"] = max_tokens
                token_param_name = "max_tokens"
            
            # 添加温度参数 (如果支持)
            if self.adapter.capabilities.supports_temperature:
                kwargs["temperature"] = temperature
            
            print(f"\n{'='*80}")
            print(f"[DEBUG] 调用 OpenAI API")
            print(f"[DEBUG] Model: {self.model}")
            print(f"[DEBUG] Temperature: {kwargs.get('temperature', 'N/A')}")
            print(f"[DEBUG] Max tokens: {max_tokens} (使用参数: {token_param_name})")
            print(f"[DEBUG] Question: {user[:100]}...")
            
            try:
                response = self._client.chat.completions.create(**kwargs)
                print(f"[DEBUG] API 调用成功!")
            except Exception as api_error:
                print(f"[ERROR] API 调用失败!")
                print(f"[ERROR] 异常类型: {type(api_error).__name__}")
                print(f"[ERROR] 异常信息: {api_error}")
                import traceback
                traceback.print_exc()
                raise
            
            # 调试日志
            print(f"[DEBUG] Response type: {type(response)}")
            print(f"[DEBUG] Has choices: {hasattr(response, 'choices')}")
            
            if hasattr(response, 'choices') and response.choices:
                print(f"[DEBUG] Choices count: {len(response.choices)}")
                choice = response.choices[0]
                print(f"[DEBUG] Finish reason: {choice.finish_reason}")
                print(f"[DEBUG] Has message: {hasattr(choice, 'message')}")
                
                if hasattr(choice, 'message') and choice.message:
                    content = choice.message.content
                    print(f"[DEBUG] Content length: {len(content) if content else 0}")
                    print(f"[DEBUG] Content preview: {content[:200] if content else '(empty)'}")
                    print(f"{'='*80}\n")
                    
                    if not content or not content.strip():
                        print(f"[ERROR] OpenAI 返回的内容为空!")
                        print(f"[ERROR] 完整响应: {response}")
                        raise ValueError("OpenAI returned empty content")
                    
                    return content
                else:
                    print(f"[ERROR] Choice 没有 message!")
                    raise ValueError(f"OpenAI choice has no message. Response: {response}")
            else:
                print(f"[ERROR] Response 没有 choices!")
                raise ValueError(f"OpenAI response has no choices. Response: {response}")
            
            print(f"{'='*80}\n")
    
    # 动态绑定方法
    import types as py_types
    llm_client.generate_with_image = py_types.MethodType(generate_with_image, llm_client)
    
    return llm_client


# =============================================================================
# SECTION 6: UTILITY FUNCTIONS
# =============================================================================

def load_evaluation_data(data_path: str) -> list[dict]:
    """
    加载评估数据
    
    Args:
        data_path: JSON 文件路径
    
    Returns:
        QA 条目列表
    """
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # JSON 可能是 dict 格式 (key: qa_id)，转换为 list
    if isinstance(data, dict):
        return list(data.values())
    return data


def save_results(results: list[dict], output_path: str, metrics: dict = None):
    """
    保存评估结果
    
    Args:
        results: 结果列表
        output_path: 输出路径
        metrics: 可选的指标字典
    """
    output = {
        "timestamp": datetime.now().isoformat(),
        "total_results": len(results),
        "results": results
    }
    
    if metrics:
        output["metrics"] = metrics
    
    # 确保目录存在
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)


# =============================================================================
# SECTION 7: MAIN (for testing)
# =============================================================================

if __name__ == "__main__":
    print("Chart QA Evaluation Pipeline")
    print("=" * 50)
    print("This module provides:")
    print("- NodeA_VLMAnswerGenerator: Sends image + question to VLM")
    print("- NodeB_AnswerEvaluator: Compares VLM answer with ground truth")
    print("- ChartQAEvaluationPipeline: Orchestrates the evaluation")
    print("")
    print("Usage:")
    print("  from evaluation_pipeline import ChartQAEvaluationPipeline")
    print("  from pipeline_architecture import LLMClient")
    print("")
    print("  llm = LLMClient(api_key='...', model='gemini-2.0-flash')")
    print("  pipeline = ChartQAEvaluationPipeline(llm)")
    print("  result = pipeline.run_single(qa_entry)")
