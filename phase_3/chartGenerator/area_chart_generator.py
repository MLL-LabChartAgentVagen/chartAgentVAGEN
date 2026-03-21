from .chart_generator_template import ChartGeneratorTemplate
from view_extractor import ViewData
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

class AreaChartGenerator(ChartGeneratorTemplate):
    @property
    def chart_type(self) -> str:
        return "area_chart"

    def generate_chart(self):
        fig, ax = plt.subplots(figsize=self.config["figsize"], dpi=self.config["dpi"])
        
        x_col = self.view_spec.binding.get("time")
        stack_col = self.view_spec.binding.get("stack")
        y_col = self.view_spec.binding.get("measure")
        
        if not x_col or not stack_col or not y_col:
            raise ValueError("Area chart requires 'time', 'stack', and 'measure' bindings.")

        # Pivot the data to create a wide format for stacked area plotting
        data = self.extracted_view.pivot(index=x_col, columns=stack_col, values=y_col).fillna(0)
        
        # Plot stacked area
        x_vals = data.index
        y_vals = [data[col] for col in data.columns]
        labels = data.columns
        
        # Get colors
        cmap = plt.get_cmap(self.config["color_palette"] if self.config["color_palette"] in plt.colormaps() else "Set2")
        colors = [cmap(i) for i in np.linspace(0, 1, len(y_vals))]
        
        ax.stackplot(x_vals, y_vals, labels=labels, colors=colors, alpha=0.8)
        
        ax.set_title(f"Stacked {y_col} over {x_col} by {stack_col}", fontsize=self.config["title_fontsize"])
        ax.set_xlabel(x_col, fontsize=self.config["label_fontsize"])
        ax.set_ylabel(y_col, fontsize=self.config["label_fontsize"])
        ax.tick_params(axis='both', which='major', labelsize=self.config["tick_fontsize"])
        
        if self.config.get("show_legend"):
            ax.legend(title=stack_col, bbox_to_anchor=(1.05, 1), loc='upper left')
            
        self._apply_layout_adjustments(fig, ax)
        
        return fig, ax
