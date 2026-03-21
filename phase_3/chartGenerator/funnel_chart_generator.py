from .chart_generator_template import ChartGeneratorTemplate
from view_extractor import ViewData
import matplotlib.pyplot as plt
import numpy as np

class FunnelChartGenerator(ChartGeneratorTemplate):
    @property
    def chart_type(self) -> str:
        return "funnel_chart"

    def generate_chart(self):
        fig, ax = plt.subplots(figsize=self.config["figsize"], dpi=self.config["dpi"])
        
        stage_col = self.view_spec.binding.get("stage")
        val_col = self.view_spec.binding.get("measure")
        
        if not stage_col or not val_col:
            val_col = self.extracted_view.columns[-1]

        data = self.extracted_view
        
        stages = data[stage_col].astype(str).tolist()
        values = data[val_col].tolist()
        
        max_val = max(values)
        y_pos = np.arange(len(stages))
        
        widths = np.array(values)
        lefts = -widths / 2
        
        cmap = plt.get_cmap(self.config["color_palette"] if self.config["color_palette"] in plt.colormaps() else "Set2")
        colors = [cmap(i/max(1, len(stages)-1)) for i in range(len(stages))]
        
        ax.barh(y_pos, widths, left=lefts, height=0.6, align='center', color=colors, alpha=0.8)
        
        for i, val in enumerate(values):
            ax.text(0, y_pos[i], f"{val}", ha='center', va='center', color='black', fontsize=self.config["tick_fontsize"], fontweight='bold')
            ax.text(max_val/2 * 1.05, y_pos[i], stages[i], ha='left', va='center', fontsize=self.config["tick_fontsize"])

        ax.set_yticks([]) 
        ax.set_xticks([]) 
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        
        ax.invert_yaxis()
        
        ax.set_title(f"Funnel Chart", fontsize=self.config["title_fontsize"])
        
        self.config["show_grid"] = False
        self._apply_layout_adjustments(fig, ax)
        
        return fig, ax
