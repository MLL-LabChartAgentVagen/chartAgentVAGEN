from .chart_generator_template import ChartGeneratorTemplate
from view_extractor import ViewData
import matplotlib.pyplot as plt
import seaborn as sns

class GroupedBarChartGenerator(ChartGeneratorTemplate):
    @property
    def chart_type(self) -> str:
        return "grouped_bar_chart"

    def generate_chart(self):
        fig, ax = plt.subplots(figsize=self.config["figsize"], dpi=self.config["dpi"])
        
        x_col = self.view_spec.binding.get("cat1")
        hue_col = self.view_spec.binding.get("cat2")
        y_col = self.view_spec.binding.get("measure")
        
        if not x_col or not hue_col or not y_col:
            raise ValueError("Grouped bar chart requires 'cat1', 'cat2', and 'measure' bindings.")

        sns.barplot(
            data=self.extracted_view, 
            x=x_col, 
            y=y_col, 
            hue=hue_col,
            ax=ax, 
            palette=self.config["color_palette"]
        )
        
        ax.set_title(f"{y_col} by {x_col} and {hue_col}", fontsize=self.config["title_fontsize"])
        ax.set_xlabel(x_col, fontsize=self.config["label_fontsize"])
        ax.set_ylabel(y_col, fontsize=self.config["label_fontsize"])
        ax.tick_params(axis='both', which='major', labelsize=self.config["tick_fontsize"])
        
        if self.config.get("show_legend"):
            ax.legend(title=hue_col, bbox_to_anchor=(1.05, 1), loc='upper left')
        else:
            ax.get_legend().remove()
            
        self._apply_layout_adjustments(fig, ax)
        
        return fig, ax
