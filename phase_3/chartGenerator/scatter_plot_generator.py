from .chart_generator_template import ChartGeneratorTemplate
from view_extractor import ViewData
import matplotlib.pyplot as plt
import seaborn as sns

class ScatterPlotGenerator(ChartGeneratorTemplate):
    @property
    def chart_type(self) -> str:
        return "scatter_plot"

    def generate_chart(self):
        fig, ax = plt.subplots(figsize=self.config["figsize"], dpi=self.config["dpi"])
        
        x_col = self.view_spec.binding.get("m1")
        y_col = self.view_spec.binding.get("m2")
        color_col = self.view_spec.binding.get("color")
        
        if not x_col or not y_col:
            raise ValueError("Scatter plot requires 'm1' and 'm2' bindings.")

        sns.scatterplot(
            data=self.extracted_view, 
            x=x_col, 
            y=y_col, 
            hue=color_col if color_col else None,
            ax=ax, 
            palette=self.config["color_palette"] if color_col else None,
            alpha=0.7
        )
        
        title_suffix = f" colored by {color_col}" if color_col else ""
        ax.set_title(f"{y_col} vs {x_col}{title_suffix}", fontsize=self.config["title_fontsize"])
        ax.set_xlabel(x_col, fontsize=self.config["label_fontsize"])
        ax.set_ylabel(y_col, fontsize=self.config["label_fontsize"])
        ax.tick_params(axis='both', which='major', labelsize=self.config["tick_fontsize"])
        
        if color_col and self.config.get("show_legend"):
            ax.legend(title=color_col, bbox_to_anchor=(1.05, 1), loc='upper left')
        elif color_col:
            try:
                ax.get_legend().remove()
            except AttributeError:
                pass
            
        self._apply_layout_adjustments(fig, ax)
        
        return fig, ax
