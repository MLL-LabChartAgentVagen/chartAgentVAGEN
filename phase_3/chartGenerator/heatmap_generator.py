from .chart_generator_template import ChartGeneratorTemplate
from view_extractor import ViewData
import matplotlib.pyplot as plt
import seaborn as sns

class HeatmapGenerator(ChartGeneratorTemplate):
    @property
    def chart_type(self) -> str:
        return "heatmap"

    def generate_chart(self):
        fig, ax = plt.subplots(figsize=self.config["figsize"], dpi=self.config["dpi"])
        
        row_col = self.view_spec.binding.get("row_cat")
        col_col = self.view_spec.binding.get("col_cat")
        val_col = self.view_spec.binding.get("measure")
        
        if not row_col or not col_col or not val_col:
            raise ValueError("Heatmap requires 'row_cat', 'col_cat', and 'measure' bindings.")

        # Pivot to matrix format required for standard heatmaps
        pivot_df = self.extracted_view.pivot(index=row_col, columns=col_col, values=val_col).fillna(0)
        
        sns.heatmap(
            data=pivot_df, 
            ax=ax, 
            cmap=self.config.get("heatmap_cmap", "YlGnBu"),
            annot=self.config.get("show_annotations", True),
            fmt=".2f",
            annot_kws={"size": max(6, self.config["tick_fontsize"] - 2)}
        )
        
        ax.set_title(f"Heatmap of {val_col} by {row_col} and {col_col}", fontsize=self.config["title_fontsize"])
        ax.set_xlabel(col_col, fontsize=self.config["label_fontsize"])
        ax.set_ylabel(row_col, fontsize=self.config["label_fontsize"])
        ax.tick_params(axis='both', which='major', labelsize=self.config["tick_fontsize"])
        
        self._apply_layout_adjustments(fig, ax)
        
        return fig, ax
