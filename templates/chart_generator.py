import copy
from typing import List, Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod
import random

from templates.parser import OperationSettings

class ChartGenerator(ABC):
    """Abstract base class for generators."""
    @abstractmethod
    def generate_random_qa_data(self, chart_metadata: Dict, random_seed: int, num_questions: int = 20) -> List[Dict]:
        pass
    
    @abstractmethod
    def chart_qa_generator(self, chart_metadata: Dict, random_seed: int = 42, num_questions: int = 20) -> List[Dict]:
        pass
    @abstractmethod
    def _format_answer(self, answer: Any) -> str:
        pass
    @abstractmethod
    def _create_qa_data(self, qa_type: str, question: str, reasoning: List[str], answer: Any, mask_indices: List[int], constraint: str = None, curriculum_level: int = 1) -> Dict:
        pass
    @abstractmethod
    def _generate_random_configs(self, chart_metadata: Dict) -> Dict:
        pass
    @abstractmethod
    def _generate_random_operator_composition(self, chart_metadata: Dict, complexity_level: int = 1) -> Tuple[OperationSettings, str, int]:
        pass
    @abstractmethod
    def _extract_constraint_from_settings(self, settings: OperationSettings) -> Optional[str]:
        pass
    @abstractmethod
    def _create_qa_data(self, qa_type: str, question: str, reasoning: List[str], answer: Any, mask_indices: List[int], constraint: str = None, curriculum_level: int = 1) -> Dict:
        pass
    # @abstractmethod
    # def _generate_random_qa_data(self, chart_metadata: Dict, random_seed: int, num_questions: int = 20) -> List[Dict]:
    #     pass
    @abstractmethod
    def _extract_constraint_from_settings(self, settings: OperationSettings) -> Optional[str]:
        pass
    @abstractmethod
    def _create_qa_data(self, qa_type: str, question: str, reasoning: List[str], answer: Any, mask_indices: List[int], constraint: str = None, curriculum_level: int = 1) -> Dict:
        pass
