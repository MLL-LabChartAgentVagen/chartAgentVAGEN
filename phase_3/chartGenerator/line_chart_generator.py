from .chart_generator_template import ChartGeneratorTemplate
from view_extractor import ViewData
import matplotlib.pyplot as plt
import seaborn as sns

class LineChartGenerator(ChartGeneratorTemplate):
    @property
    def chart_type(self) -> str:
        return "line_chart"

    def generate_chart(self):
        fig, ax = plt.subplots(figsize=self.config["figsize"], dpi=self.config["dpi"])
        
        x_col = self.view_spec.binding.get("time")
        series_col = self.view_spec.binding.get("series")
        y_col = self.view_spec.binding.get("measure")
        
        if not x_col or not y_col:
            raise ValueError("Line chart requires 'time' and 'measure' bindings.")

        # Sort data by time to ensure line connects properly
        data = self.extracted_view.sort_values(by=x_col)

        sns.lineplot(
            data=data, 
            x=x_col, 
            y=y_col, 
            hue=series_col if series_col else None,
            marker='o',
            ax=ax, 
            palette=self.config["color_palette"] if series_col else None
        )
        
        title_suffix = f" grouped by {series_col}" if series_col else ""
        ax.set_title(f"{y_col} over {x_col}{title_suffix}", fontsize=self.config["title_fontsize"])
        ax.set_xlabel(x_col, fontsize=self.config["label_fontsize"])
        ax.set_ylabel(y_col, fontsize=self.config["label_fontsize"])
        ax.tick_params(axis='both', which='major', labelsize=self.config["tick_fontsize"])
        
        if series_col and self.config.get("show_legend"):
            ax.legend(title=series_col, bbox_to_anchor=(1.05, 1), loc='upper left')
        elif series_col and not self.config.get("show_legend"):
            ax.get_legend().remove()
            
        self._apply_layout_adjustments(fig, ax)
        
        return fig, ax
