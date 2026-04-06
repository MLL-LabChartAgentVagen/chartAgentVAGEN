from .chart_generator_template import ChartGeneratorTemplate
from view_extractor import ViewData
import matplotlib.pyplot as plt

class PieChartGenerator(ChartGeneratorTemplate):
    @property
    def chart_type(self) -> str:
        return "pie_chart"

    def generate_chart(self):
        fig, ax = plt.subplots(figsize=self.config["figsize"], dpi=self.config["dpi"])
        
        cat_col = self.view_spec.binding.get("cat")
        val_col = self.view_spec.binding.get("measure")
        
        if not cat_col or not val_col:
            raise ValueError("Pie chart requires 'cat' and 'measure' bindings.")

        labels = self.extracted_view[cat_col]
        sizes = self.extracted_view[val_col]
        
        explode = tuple(0.1 if getattr(self.config, "explode_slices", False) else 0 for _ in range(len(sizes)))
        if self.config.get("explode"):
            explode = tuple(0.05 for _ in range(len(sizes)))
        
        cmap = plt.get_cmap(self.config["color_palette"] if self.config["color_palette"] in plt.colormaps() else "Set2")
        colors = cmap(range(len(labels)))
        
        ax.pie(
            sizes, 
            labels=labels, 
            autopct='%1.1f%%', 
            startangle=90, 
            colors=colors,
            explode=explode,
            textprops={'fontsize': self.config["tick_fontsize"]}
        )
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        
        ax.set_title(f"{val_col} Share by {cat_col}", fontsize=self.config["title_fontsize"])
        
        self._apply_layout_adjustments(fig, ax)
        
        return fig, ax
