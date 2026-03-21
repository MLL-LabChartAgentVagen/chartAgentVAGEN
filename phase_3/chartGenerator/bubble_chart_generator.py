from .chart_generator_template import ChartGeneratorTemplate
from view_extractor import ViewData
import matplotlib.pyplot as plt
import seaborn as sns

class BubbleChartGenerator(ChartGeneratorTemplate):
    @property
    def chart_type(self) -> str:
        return "bubble_chart"

    def generate_chart(self):
        fig, ax = plt.subplots(figsize=self.config["figsize"], dpi=self.config["dpi"])
        
        cat_col = self.view_spec.binding.get("cat")
        x_col = self.view_spec.binding.get("m1")
        y_col = self.view_spec.binding.get("m2")
        size_col = self.view_spec.binding.get("m3")
        
        if not cat_col or not x_col or not y_col or not size_col:
            raise ValueError("Bubble chart requires 'cat', 'm1', 'm2', and 'm3' bindings.")

        sns.scatterplot(
            data=self.extracted_view, 
            x=x_col, 
            y=y_col, 
            size=size_col,
            sizes=(20, 1000), # Minimum and maximum bubble sizes
            hue=cat_col,
            ax=ax, 
            palette=self.config["color_palette"],
            alpha=0.7
        )
        
        ax.set_title(f"Bubble Chart: {y_col} vs {x_col} (Size: {size_col})", fontsize=self.config["title_fontsize"])
        ax.set_xlabel(x_col, fontsize=self.config["label_fontsize"])
        ax.set_ylabel(y_col, fontsize=self.config["label_fontsize"])
        ax.tick_params(axis='both', which='major', labelsize=self.config["tick_fontsize"])
        
        if self.config.get("show_legend"):
            # Move legend outside since sizes + categories can be large
            # Adding tight_layout here strictly before returning prevents matplotlib infinite layout recursion
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
        else:
            try:
                ax.get_legend().remove()
            except AttributeError:
                pass
            
        self._apply_layout_adjustments(fig, ax)
        
        return fig, ax
