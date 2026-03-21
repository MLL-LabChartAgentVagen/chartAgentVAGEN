from .chart_generator_template import ChartGeneratorTemplate
from view_extractor import ViewData
import matplotlib.pyplot as plt
import seaborn as sns

class BarChartGenerator(ChartGeneratorTemplate):
    @property
    def chart_type(self) -> str:
        return "bar_chart"

    def generate_chart(self):
        fig, ax = plt.subplots(figsize=self.config["figsize"], dpi=self.config["dpi"])
        
        x_col = self.view_spec.binding.get("cat")
        y_col = self.view_spec.binding.get("measure")
        
        if not x_col or not y_col:
            raise ValueError("Bar chart requires 'cat' and 'measure' bindings.")

        # Sort the values as per the view extraction rules logic implies ORDER BY AGG DESC
        data = self.extracted_view.sort_values(by=y_col, ascending=False)
        
        sns.barplot(
            data=data, 
            x=x_col, 
            y=y_col, 
            hue=x_col,
            ax=ax, 
            palette=self.config["color_palette"],
            legend=False
        )
        
        ax.set_title(f"{y_col} by {x_col}", fontsize=self.config["title_fontsize"])
        ax.set_xlabel(x_col, fontsize=self.config["label_fontsize"])
        ax.set_ylabel(y_col, fontsize=self.config["label_fontsize"])
        ax.tick_params(axis='both', which='major', labelsize=self.config["tick_fontsize"])
        
        self._apply_layout_adjustments(fig, ax)
        
        return fig, ax
