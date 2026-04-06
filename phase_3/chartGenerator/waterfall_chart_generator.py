from .chart_generator_template import ChartGeneratorTemplate
from view_extractor import ViewData
import matplotlib.pyplot as plt
import numpy as np

class WaterfallChartGenerator(ChartGeneratorTemplate):
    @property
    def chart_type(self) -> str:
        return "waterfall_chart"

    def generate_chart(self):
        fig, ax = plt.subplots(figsize=self.config["figsize"], dpi=self.config["dpi"])
        
        stage_col = self.view_spec.binding.get("stage")
        val_col = self.view_spec.binding.get("measure")
        
        if not stage_col or not val_col:
            raise ValueError("Waterfall chart requires 'stage' and 'measure' bindings.")

        data = self.extracted_view
        
        stages = data[stage_col].astype(str).tolist()
        values = data[val_col].tolist()
        
        cumulative = np.cumsum(values)
        starts = np.pad(cumulative[:-1], (1, 0), constant_values=0)
        
        colors = ['red' if v < 0 else 'green' for v in values]
        
        ax.bar(stages, values, bottom=starts, color=colors, edgecolor='black', zorder=3)
        
        if self.config.get("waterfall_add_total", False):
            ax.bar(['Total'], [cumulative[-1]], bottom=0, color='blue', edgecolor='black', zorder=3)
            stages.append('Total')
        
        ax.set_title(f"Waterfall of {val_col} across {stage_col}", fontsize=self.config["title_fontsize"])
        ax.set_xlabel(stage_col, fontsize=self.config["label_fontsize"])
        ax.set_ylabel(val_col, fontsize=self.config["label_fontsize"])
        ax.tick_params(axis='both', which='major', labelsize=self.config["tick_fontsize"])
        
        # Connectors
        for i in range(len(values) - 1):
            ax.plot([i, i+1], [cumulative[i], cumulative[i]], color='gray', linestyle='--')
            
        self._apply_layout_adjustments(fig, ax)
        
        return fig, ax
