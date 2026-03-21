from .chart_generator_template import ChartGeneratorTemplate
from view_extractor import ViewData
import matplotlib.pyplot as plt
import seaborn as sns

class StackedBarChartGenerator(ChartGeneratorTemplate):
    @property
    def chart_type(self) -> str:
        return "stacked_bar_chart"

    def generate_chart(self):
        fig, ax = plt.subplots(figsize=self.config["figsize"], dpi=self.config["dpi"])
        
        x_col = self.view_spec.binding.get("cat1")
        stack_col = self.view_spec.binding.get("cat2")
        y_col = self.view_spec.binding.get("measure")
        
        if not x_col or not stack_col or not y_col:
            raise ValueError("Stacked bar chart requires 'cat1', 'cat2', and 'measure' bindings.")

        # Pivot to make stacking easier with pandas plot
        pivot_df = self.extracted_view.pivot(index=x_col, columns=stack_col, values=y_col).fillna(0)
        
        pivot_df.plot(
            kind='bar', 
            stacked=True, 
            ax=ax, 
            colormap=self.config["color_palette"] if self.config["color_palette"] in plt.colormaps() else "Set2"
        )
        
        ax.set_title(f"{y_col} by {x_col} and {stack_col}", fontsize=self.config["title_fontsize"])
        ax.set_xlabel(x_col, fontsize=self.config["label_fontsize"])
        ax.set_ylabel(y_col, fontsize=self.config["label_fontsize"])
        ax.tick_params(axis='both', which='major', labelsize=self.config["tick_fontsize"])
        
        if self.config.get("show_legend"):
            ax.legend(title=stack_col, bbox_to_anchor=(1.05, 1), loc='upper left')
        else:
            try:
                ax.get_legend().remove()
            except AttributeError:
                pass
            
        self._apply_layout_adjustments(fig, ax)
        
        return fig, ax
