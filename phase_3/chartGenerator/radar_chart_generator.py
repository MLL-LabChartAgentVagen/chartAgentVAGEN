from .chart_generator_template import ChartGeneratorTemplate
from view_extractor import ViewData
import matplotlib.pyplot as plt
import numpy as np

class RadarChartGenerator(ChartGeneratorTemplate):
    @property
    def chart_type(self) -> str:
        return "radar_chart"

    def generate_chart(self):
        fig = plt.figure(figsize=self.config["figsize"], dpi=self.config["dpi"])
        ax = fig.add_subplot(111, polar=True)
        
        cat_col = self.view_spec.binding.get("cat")
        
        if not cat_col:
            raise ValueError("Radar chart requires 'cat' binding.")

        measures = [col for col in self.extracted_view.columns if col != cat_col]
        num_vars = len(measures)
        
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1]
        
        cmap = plt.get_cmap(self.config["color_palette"] if self.config["color_palette"] in plt.colormaps() else "Set2")
        colors = [cmap(i) for i in range(len(self.extracted_view))]

        for idx, row in self.extracted_view.iterrows():
            if len(measures) == 0:
                continue
                
            values = row[measures].fillna(0).values.flatten().tolist()
            if not values:
                continue
                
            values += values[:1] 
            entity = row[cat_col]
            
            # Ensure no NaNs are plotted
            values = [0 if np.isnan(v) else v for v in values]
            
            ax.plot(angles, values, linewidth=2, label=str(entity), color=colors[idx % len(colors)])
            ax.fill(angles, values, color=colors[idx % len(colors)], alpha=0.25)

        if len(measures) > 0:
            ax.set_theta_offset(np.pi / 2)
            ax.set_theta_direction(-1)
            ax.set_thetagrids(np.degrees(angles[:-1]), measures, fontsize=self.config["tick_fontsize"])
        
        ax.set_title(f"Radar Chart by {cat_col}", fontsize=self.config["title_fontsize"], pad=20)
        
        if self.config.get("show_legend"):
            ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

        self._apply_layout_adjustments(fig, ax)
        
        return fig, ax
