from .chart_generator_template import ChartGeneratorTemplate
from view_extractor import ViewData
import matplotlib.pyplot as plt
import seaborn as sns

class HistogramGenerator(ChartGeneratorTemplate):
    @property
    def chart_type(self) -> str:
        return "histogram"

    def generate_chart(self):
        fig, ax = plt.subplots(figsize=self.config["figsize"], dpi=self.config["dpi"])
        
        x_col = self.view_spec.binding.get("measure")
        
        if not x_col:
            raise ValueError("Histogram requires 'measure' binding.")

        # Handle 'bins' config if provided, else let seaborn decide
        bins = self.config.get("bins", 'auto')

        sns.histplot(
            data=self.extracted_view, 
            x=x_col, 
            bins=bins,
            ax=ax, 
            kde=self.config.get("show_kde", False)
        )
        
        ax.set_title(f"Distribution of {x_col}", fontsize=self.config["title_fontsize"])
        ax.set_xlabel(x_col, fontsize=self.config["label_fontsize"])
        ax.set_ylabel("Frequency", fontsize=self.config["label_fontsize"])
        ax.tick_params(axis='both', which='major', labelsize=self.config["tick_fontsize"])
        
        self._apply_layout_adjustments(fig, ax)
        
        return fig, ax
