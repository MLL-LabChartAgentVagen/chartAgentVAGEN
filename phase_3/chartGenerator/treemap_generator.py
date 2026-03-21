from .chart_generator_template import ChartGeneratorTemplate
from view_extractor import ViewData
import matplotlib.pyplot as plt
import pandas as pd

class TreemapGenerator(ChartGeneratorTemplate):
    @property
    def chart_type(self) -> str:
        return "treemap"

    def generate_chart(self):
        try:
            import squarify
        except ImportError:
            raise ImportError("Please install 'squarify' package to generate Treemaps (pip install squarify).")

        fig, ax = plt.subplots(figsize=self.config["figsize"], dpi=self.config["dpi"])
        
        hier1 = self.view_spec.binding.get("hier1") or self.view_spec.binding.get("cat") or self.view_spec.binding.get("cat1")
        hier2 = self.view_spec.binding.get("hier2") or self.view_spec.binding.get("cat2")
        measure = self.view_spec.binding.get("measure")
        
        if not hier1 or not measure:
            raise ValueError("Treemap requires at least 'hier1' and 'measure' bindings.")
            
        data = self.extracted_view
        
        if not hier2:
            labels = data[hier1].astype(str).tolist()
        else:
            if hier2 in data.columns:
                labels = [f"{h1}\n{h2}" for h1, h2 in zip(data[hier1], data[hier2])]
            else:
                labels = data[hier1].astype(str).tolist()
        
        # Sort by measure descending to place largest squares correctly
        data = data.sort_values(by=measure, ascending=False)
        sizes = data[measure]
        
        # Labels should be aligned with the sorted data
        if not hier2 or hier2 not in data.columns:
            labels = data[hier1].astype(str).tolist()
        else:
            labels = [f"{h1}\n{h2}" for h1, h2 in zip(data[hier1], data[hier2])]
        
        cmap = plt.get_cmap(self.config["color_palette"] if self.config["color_palette"] in plt.colormaps() else "Set2")
        # generate colors based on sizes
        colors = [cmap(i/max(1, len(sizes)-1)) for i in range(len(sizes))]

        squarify.plot(sizes=sizes, label=labels, alpha=0.8, color=colors, ax=ax, text_kwargs={'fontsize': self.config["tick_fontsize"]})
        
        ax.set_title(f"Treemap of {measure} by {hier1} and {hier2}", fontsize=self.config["title_fontsize"])
        ax.axis('off')
        
        self._apply_layout_adjustments(fig, ax)
        
        return fig, ax
