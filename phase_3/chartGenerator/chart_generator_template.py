from view_extraction_rules import VIEW_EXTRACTION_RULES
from intra_view_qa_template import INTRA_VIEW_TEMPLATES
from view_spec import ViewSpec
from view_extractor import ViewData, ViewExtractor
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from abc import ABC, abstractmethod

class ChartGeneratorTemplate(ABC):
    def __init__(self, view_data: ViewData):
        self.view_data = view_data
        self.view_spec = view_data.view_spec
        self.master_table = view_data.master_table
        self.extracted_view = view_data.extracted_view
        
        # Configuration dictionary with defaults
        self.config = {
            "figsize": (10, 6),
            "color_palette": "Set2",
            "title_fontsize": 14,
            "label_fontsize": 12,
            "tick_fontsize": 10,
            "show_grid": True,
            "show_legend": True,
            "dpi": 100,
            "explode": False  # Specific for pie/donut charts, etc.
        }
        
        if self.view_spec.chart_type != self.chart_type:
            raise ValueError(f"Chart type mismatch: expected {self.chart_type}, got {self.view_spec.chart_type}")

    @property
    @abstractmethod
    def chart_type(self) -> str:
        """String representing the chart type (e.g., 'bar_chart')"""
        pass
        
    def update_config(self, **kwargs):
        """Allows user to safely override chart configurations"""
        for key, value in kwargs.items():
            if key == "figsize" and isinstance(value, tuple) and len(value) == 2:
                # Sanitize figure size
                w, h = value
                w = max(2, min(w, 20))
                h = max(2, min(h, 20))
                self.config["figsize"] = (w, h)
            elif key in ["title_fontsize", "label_fontsize", "tick_fontsize"] and isinstance(value, (int, float)):
                # Sanitize font sizes
                self.config[key] = max(6, min(value, 24))
            elif key in self.config:
                self.config[key] = value
                
    def _apply_layout_adjustments(self, fig, ax):
        """Helper to safely format layout and prevent overlaps"""
        if self.config.get("show_grid"):
            # Some axes like pie charts shouldn't have grid lines, we will let subclasses override or we check axis type
            # but generally we can try/except or just plot grid safely
            try:
                ax.grid(True, linestyle='--', alpha=0.7)
            except AttributeError:
                pass
        
        # Prevent overlapping x-ticks by rotating if there are many
        try:
            if len(ax.get_xticklabels()) > 5:
                for label in ax.get_xticklabels():
                    label.set_rotation(45)
                    label.set_horizontalalignment('right')
        except AttributeError:
            pass
            
        try:
            fig.tight_layout()
        except (ValueError, Exception):
            pass
        
    @abstractmethod
    def generate_chart(self):
        """Core charting method to be implemented by subclasses. Should return (fig, ax)."""
        pass
