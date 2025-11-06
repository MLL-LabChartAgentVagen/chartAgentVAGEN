"""
Run Draw
"""

import os
import json
from typing import List, Dict
from abc import ABC, abstractmethod
from typing import Callable

class RunDraw(ABC):

    @abstractmethod
    def _init_plot_functions(self) -> Dict[str, Dict[str, Callable]]:
        pass

    @abstractmethod
    def _save_chart_qa_data_to_json(self, chart_qa_data: Dict) -> None:
        pass
