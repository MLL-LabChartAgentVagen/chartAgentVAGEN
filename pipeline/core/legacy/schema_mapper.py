import json
import logging
import numpy as np
from typing import Dict, Any

from .master_table import MasterTable
from .basic_operators import Chain, GroupBy, Sort, Limit, Project

logger = logging.getLogger(__name__)

# Legacy Prompts (moved here for encapsulation)
PROMPT_NODE_C_SCHEMA_MAPPER = """
You are an expert Data Visualizer. Your task is to map relational Master Data into schemas 
for 6 chart types: BAR, SCATTER, PIE, HISTOGRAM, LINE, and HEATMAP.

Return a JSON with keys for each chart type containing the necessary structural arrays.

Master Data Input:
{master_data_json}
"""

PROMPT_NODE_D_RL_CAPTIONER = """
You are an expert Data Analyst. Your task is to write a single descriptive caption 
for a {chart_type} chart based on its structural metadata. 

Return JSON: {{"ground_truth_caption": "Your text here..."}}

Metadata:
{chart_metadata_json}
"""

class SchemaMapper:
    """
    Extracted from generation_pipeline.py NodeC_SchemaMapper.
    Constructs chart plotting instructions and captions from a MasterTable.
    """
    
    DEFAULT_COLORS = [
        "#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8",
        "#82CA9D", "#FFC658", "#FF6B9D", "#4ECDC4", "#45B7D1",
        "#96CEB4", "#FFEAA7", "#DDA0DD", "#98D8C8", "#F7DC6F"
    ]
    
    def __init__(self, llm_client, use_relational_adapter: bool = True):
        self.llm = llm_client
        self.use_relational_adapter = use_relational_adapter

    def _pick_columns(self, mt: MasterTable):
        """Heuristically pick categorical and numeric columns from the MasterTable."""
        df = mt.df
        cat_cols = df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
        num_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        non_date_cats = [
            c for c in cat_cols
            if not any(kw in c.lower() for kw in ('date', 'time', 'period', 'year', 'month', 'quarter'))
        ]
        entity_col = non_date_cats[0] if non_date_cats else (cat_cols[0] if cat_cols else None)
        primary_metric = num_cols[0] if len(num_cols) >= 1 else None
        secondary_metric = num_cols[1] if len(num_cols) >= 2 else None
        tertiary_metric = num_cols[2] if len(num_cols) >= 3 else None
        
        return entity_col, primary_metric, secondary_metric, tertiary_metric
    
    def _adapter_bar(self, mt: MasterTable) -> dict:
        entity_col, primary_metric, _, _ = self._pick_columns(mt)
        if not entity_col or not primary_metric:
            raise ValueError("Cannot derive bar chart: missing entity or primary metric column")
        
        chain = Chain([
            GroupBy(by=[entity_col], agg={primary_metric: 'sum'}),
            Sort(column=primary_metric, ascending=False),
            Limit(10),
        ])
        result_df = chain.apply(mt.df)
        n = len(result_df)
        colors = self.DEFAULT_COLORS[:n] if n <= len(self.DEFAULT_COLORS) else (self.DEFAULT_COLORS * ((n // len(self.DEFAULT_COLORS)) + 1))[:n]
        
        return {
            "bar_data": result_df[primary_metric].tolist(),
            "bar_labels": result_df[entity_col].astype(str).tolist(),
            "bar_colors": colors,
            "x_label": entity_col,
            "y_label": primary_metric,
            "img_title": f"{primary_metric} by {entity_col}",
        }
    
    def _adapter_scatter(self, mt: MasterTable) -> dict:
        entity_col, primary_metric, secondary_metric, tertiary_metric = self._pick_columns(mt)
        if not primary_metric or not secondary_metric:
            raise ValueError("Cannot derive scatter chart: need 2+ numeric columns")
        
        cols_to_project = [c for c in [entity_col, primary_metric, secondary_metric, tertiary_metric] if c]
        chain = Chain([Project(cols_to_project)])
        result_df = chain.apply(mt.df).dropna(subset=[primary_metric, secondary_metric])
        n = len(result_df)
        colors = self.DEFAULT_COLORS[:n] if n <= len(self.DEFAULT_COLORS) else (self.DEFAULT_COLORS * ((n // len(self.DEFAULT_COLORS)) + 1))[:n]
        
        if tertiary_metric and tertiary_metric in result_df.columns:
            tertiary_vals = result_df[tertiary_metric].tolist()
            max_t = max(tertiary_vals) if tertiary_vals else 1
            scale = 60 if max_t < 10 else (20 if max_t < 100 else 5)
            sizes = [v * scale for v in tertiary_vals]
        else:
            sizes = [50] * n
        
        return {
            "scatter_x_data": result_df[secondary_metric].tolist(),
            "scatter_y_data": result_df[primary_metric].tolist(),
            "scatter_labels": result_df[entity_col].astype(str).tolist() if entity_col else [str(i) for i in range(n)],
            "scatter_colors": colors,
            "scatter_sizes": sizes,
            "x_label": secondary_metric,
            "y_label": primary_metric,
            "img_title": f"{primary_metric} vs {secondary_metric}",
        }
    
    def _adapter_pie(self, mt: MasterTable) -> dict:
        entity_col, primary_metric, _, _ = self._pick_columns(mt)
        if not entity_col or not primary_metric:
            raise ValueError("Cannot derive pie chart: missing entity or primary metric column")
        
        chain = Chain([
            GroupBy(by=[entity_col], agg={primary_metric: 'sum'}),
            Sort(column=primary_metric, ascending=False),
            Limit(8),
        ])
        result_df = chain.apply(mt.df)
        n = len(result_df)
        colors = self.DEFAULT_COLORS[:n] if n <= len(self.DEFAULT_COLORS) else (self.DEFAULT_COLORS * ((n // len(self.DEFAULT_COLORS)) + 1))[:n]
        
        return {
            "pie_data": result_df[primary_metric].tolist(),
            "pie_labels": result_df[entity_col].astype(str).tolist(),
            "pie_colors": colors,
            "pie_data_category": {
                "singular": entity_col,
                "plural": entity_col
            },
            "pie_label_category": {
                "singular": entity_col,
                "plural": entity_col
            },
            "img_title": f"Distribution of {primary_metric} by {entity_col}",
        }
    
    def _adapter_histogram(self, mt: MasterTable) -> dict:
        _, primary_metric, _, _ = self._pick_columns(mt)
        if not primary_metric:
            raise ValueError("Cannot derive histogram: missing numeric column")
        
        values = mt.df[primary_metric].dropna().tolist()
        counts, edges = np.histogram(values, bins='auto')
        
        return {
            "histogram_data": values,
            "bin_edges": edges.tolist(),
            "x_label": primary_metric,
            "y_label": "Frequency",
            "img_title": f"Distribution of {primary_metric}",
            "chart_color": self.DEFAULT_COLORS[0],
            "tick_step": max(1, len(edges) // 6),
        }
    
    def _adapter_line(self, mt: MasterTable) -> dict:
        df = mt.df
        entity_col, primary_metric, _, _ = self._pick_columns(mt)
        if not entity_col or not primary_metric:
            raise ValueError("Cannot derive line chart: missing entity or metric column")
        
        temporal_col = None
        for col in df.columns:
            if any(kw in col.lower() for kw in ('date', 'time', 'period', 'year', 'month', 'quarter')):
                temporal_col = col
                break
        
        if temporal_col:
            pivot = df.pivot_table(
                index=temporal_col, columns=entity_col,
                values=primary_metric, aggfunc='sum'
            ).fillna(0)
            x_labels = [str(x) for x in pivot.index.tolist()]
            line_labels = [str(c) for c in pivot.columns.tolist()]
            line_data = [pivot[col].tolist() for col in pivot.columns]
        else:
            grouped = df.groupby(entity_col, as_index=False)[primary_metric].sum()
            x_labels = grouped[entity_col].astype(str).tolist()
            line_labels = [primary_metric]
            line_data = [grouped[primary_metric].tolist()]
        
        n_series = len(line_labels)
        colors = self.DEFAULT_COLORS[:n_series] if n_series <= len(self.DEFAULT_COLORS) else (
            self.DEFAULT_COLORS * ((n_series // len(self.DEFAULT_COLORS)) + 1))[:n_series]
        
        return {
            "line_data": line_data,
            "line_labels": line_labels,
            "line_category": {
                "singular": entity_col,
                "plural": entity_col
            },
            "line_colors": colors,
            "x_labels": x_labels,
            "x_label": temporal_col or entity_col,
            "y_label": primary_metric,
            "img_title": f"{primary_metric} Trend by {entity_col}",
        }
    
    def _adapter_heatmap(self, mt: MasterTable) -> dict:
        df = mt.df
        entity_col, primary_metric, _, _ = self._pick_columns(mt)
        if not entity_col or not primary_metric:
            raise ValueError("Cannot derive heatmap: missing entity or metric column")
        
        second_dim = None
        for col in df.columns:
            if col == entity_col:
                continue
            if any(kw in col.lower() for kw in ('date', 'time', 'period', 'year', 'month', 'quarter')):
                second_dim = col
                break
        
        if not second_dim:
            cat_cols = df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
            others = [c for c in cat_cols if c != entity_col]
            if others:
                second_dim = others[0]
        
        if not second_dim:
            raise ValueError("Cannot derive heatmap: need 2 categorical dimensions")
        
        pivot = df.pivot_table(
            index=second_dim, columns=entity_col,
            values=primary_metric, aggfunc='sum'
        ).fillna(0)
        
        x_labels = [str(c) for c in pivot.columns.tolist()]
        y_labels = [str(r) for r in pivot.index.tolist()]
        heatmap_data = pivot.values.tolist()
        
        return {
            "heatmap_data": heatmap_data,
            "heatmap_category": {
                "singular": primary_metric,
                "plural": primary_metric
            },
            "x_labels": x_labels,
            "y_labels": y_labels,
            "x_label": entity_col,
            "y_label": second_dim,
            "img_title": f"{primary_metric} by {entity_col} and {second_dim}",
        }

    def validate_caption_output(self, data: dict) -> tuple[bool, list[str]]:
        errors = []
        if "ground_truth_caption" not in data:
            errors.append("Missing ground_truth_caption")
        elif not isinstance(data["ground_truth_caption"], str):
            errors.append("ground_truth_caption must be a string")
        elif len(data["ground_truth_caption"].strip()) == 0:
            errors.append("ground_truth_caption cannot be empty")
        return len(errors) == 0, errors

    def __call__(self, master_data: MasterTable) -> Dict[str, Any]:
        """
        Derive chart schemas and generate captions.
        """
        if not isinstance(master_data, MasterTable):
            raise ValueError("SchemaMapper requires a MasterTable instance.")

        response = {}
        for chart_type, adapter_fn in [
            ("bar", self._adapter_bar),
            ("scatter", self._adapter_scatter),
            ("pie", self._adapter_pie),
            ("histogram", self._adapter_histogram),
            ("line", self._adapter_line),
            ("heatmap", self._adapter_heatmap),
        ]:
            try:
                response[chart_type] = adapter_fn(master_data)
            except Exception as e:
                logger.warning(f"Adapter for {chart_type} failed: {e}. Skipping.")

        # Caption Generation
        captions = {}
        for chart_type, metadata in response.items():
            if not self.llm:
                break
                
            system_prompt = PROMPT_NODE_D_RL_CAPTIONER.format(
                chart_type=chart_type.upper(),
                chart_metadata_json=json.dumps(metadata, indent=2)
            )
            
            try:
                caption_response = self.llm.generate_json(
                    system=system_prompt,
                    user=f"Generate caption for this {chart_type} chart:\n\nMetadata: {json.dumps(metadata, indent=2)}",
                    temperature=1.0
                )
                
                cleaned_response = {
                    "ground_truth_caption": caption_response.get(
                        "ground_truth_caption", 
                        f"Chart showing {metadata.get('img_title', 'data')}"
                    )
                }
                
                is_valid, errors = self.validate_caption_output(cleaned_response)
                if not is_valid:
                    cleaned_response["ground_truth_caption"] = f"Chart showing {metadata.get('img_title', 'data')}"
                
                captions[chart_type] = cleaned_response
            except Exception as e:
                logger.warning(f"Caption generation failed for {chart_type}: {e}")
                captions[chart_type] = {"ground_truth_caption": f"Chart showing {metadata.get('img_title', 'data')}"}

        return {
            "chart_entries": response,
            "captions": captions
        }
