import random
import pandas as pd
from typing import Dict, Any, Tuple
from view_spec import ViewSpec
from .intra_view_templates import INTRA_VIEW_TEMPLATES

class IntraQAGenerator:
    def __init__(self, templates: Dict[str, Dict[str, Any]] = None):
        if templates is None:
            self.templates = INTRA_VIEW_TEMPLATES
        else:
            self.templates = templates

    def generate_qa(self, view_spec: ViewSpec) -> Tuple[str, str]:
        """
        Generates a random question and answer based on the provided view_spec
        and its extracted_view DataFrame.
        """
        df = view_spec.extracted_view
        if df is None or df.empty:
            return "No data available", "N/A"

        chart_type = view_spec.chart_type
        
        # Filter templates applicable to this chart_type
        applicable_templates = {
            k: v for k, v in self.templates.items() 
            if chart_type in v.get("applicable", [])
        }

        if not applicable_templates:
            return f"No templates available for {chart_type}", "N/A"

        # Select a random template
        template_name = random.choice(list(applicable_templates.keys()))
        t_data = applicable_templates[template_name]
        
        try:
            return self._apply_template(template_name, t_data, view_spec, df)
        except Exception as e:
            return f"Error generating QA for {template_name}: {e}", "N/A"

    def generate_all_qa(self, view_spec: ViewSpec) -> list[dict]:
        """
        Generates one QA pair for each applicable template for the given view_spec.
        """
        df = view_spec.extracted_view
        if df is None or df.empty:
            return []

        chart_type = view_spec.chart_type
        
        applicable_templates = {
            k: v for k, v in self.templates.items() 
            if chart_type in v.get("applicable", [])
        }

        qa_pairs = []
        for template_name, t_data in applicable_templates.items():
            try:
                q, a = self._apply_template(template_name, t_data, view_spec, df)
                qa_pairs.append({
                    "template": template_name,
                    "question": q,
                    "answer": a,
                    "difficulty": t_data.get("difficulty", "unknown")
                })
            except Exception as e:
                # Can silently skip or log
                pass
                
        return qa_pairs

    def _apply_template(self, template_name: str, t_data: dict, view_spec: ViewSpec, df: pd.DataFrame) -> Tuple[str, str]:
        q_template = t_data["template"]
        ans_fn = t_data["answer_fn"]
        
        # Basic variable resolution from view_spec
        measure = view_spec.measure
        if not measure and view_spec.binding.get("m1"):
            measure = view_spec.binding.get("m1") # fallback
            
        cat = view_spec.binding.get("cat") or view_spec.binding.get("cat1") or view_spec.binding.get("row_cat") or view_spec.binding.get("time")

        if template_name == "value_retrieval":
            entity = random.choice(df[cat].unique()) if cat in df.columns else "Unknown"
            agg = random.choice(["mean", "sum", "median"])
            
            # Since view is likely already aggregated, we just describe the aggregation
            # if the user specifically asked for dynamic aggregation simulation:
            if agg == "mean":
                ans = df.loc[df[cat] == entity, measure].mean()
            elif agg == "sum":
                ans = df.loc[df[cat] == entity, measure].sum()
            else: # median
                ans = df.loc[df[cat] == entity, measure].median()

            q = q_template.format(agg=agg, measure=measure, entity=entity)
            return q, str(ans)

        elif template_name == "extremum":
            mode = random.choice(["highest", "lowest"])
            q = q_template.format(cat=cat, mode=mode, measure=measure)
            ans = ans_fn(df, measure, cat, mode)
            return q, str(ans)

        elif template_name == "comparison":
            if cat in df.columns and len(df[cat].unique()) >= 2:
                entities = random.sample(list(df[cat].unique()), 2)
                mode = random.choice(["more", "less"])
                q = q_template.format(mode=mode, entity_a=entities[0], measure=measure, entity_b=entities[1])
                ans = ans_fn(df, entities[0], entities[1], measure, cat)
                return q, str(ans)
            return "Not enough entities for comparison", "N/A"

        elif template_name == "trend":
            if cat in df.columns: # Needs a time/cat column
                start = df[cat].iloc[0]
                end = df[cat].iloc[-1]
                q = q_template.format(measure=measure, start=start, end=end)
                ans = ans_fn(df, measure)
                return q, str(ans)

        elif template_name == "proportion":
            if cat in df.columns:
                entity = random.choice(df[cat].unique())
                q = q_template.format(entity=entity, measure=measure)
                ans = ans_fn(df, entity, measure, cat)
                return q, f"{ans:.2f}%"

        elif template_name == "distribution_shape":
            q = q_template.format(measure=measure)
            ans = ans_fn(df, measure)
            return q, str(ans)

        elif template_name == "correlation_direction":
            m1 = view_spec.binding.get("m1")
            m2 = view_spec.binding.get("m2")
            if m1 and m2:
                q = q_template.format(m1=m1, m2=m2)
                ans = ans_fn(df, m1, m2)
                return q, str(ans)

        return f"Unhandled template parameters for {template_name}", "N/A"
