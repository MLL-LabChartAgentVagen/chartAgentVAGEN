"""
End-to-end workflow for line chart image, QA and mask generation.
"""

from __future__ import annotations

import copy
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Union

import matplotlib.pyplot as plt

project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from metadata.metadata import METADATA_LINE
from chartGenerators.line.line_chart_generator import LineChartGenerator
from utils.logger import logger
from utils.json_util import read_from_json
from utils.masks.mask_generator import mask_generation
from templates.run_draw import RunDraw


# ---------------------------------------------------------------------------
# Drawing utilities
# ---------------------------------------------------------------------------
def draw__4_line__func_1(
    args,
    line_data: List[List[float]],
    line_labels: List[str],
    line_colors: List[str],
    x_labels: List[Union[int, float, str]],
    x_label: str,
    y_label: str,
    img_title: str,
    horizontal: bool = False,
    line_styles: List[str] = None,
    line_widths: List[float] = None,
    marker_styles: List[str] = None,
    show_markers: bool = False,
    show_text_label: bool = False,
    show_legend: bool = True,
    change_x_axis_pos: bool = False,
    change_y_axis_pos: bool = False,
    img_save_name: str = None,
):
    """Render a configurable line chart."""
    if line_styles is None:
        line_styles = ["-"] * len(line_data)
    if line_widths is None:
        line_widths = [3.0] * len(line_data)
    if marker_styles is None:
        marker_styles = ["o"] * len(line_data)

    num_lines = len(line_data)
    line_styles = (line_styles * num_lines)[:num_lines]
    line_widths = (line_widths * num_lines)[:num_lines]
    marker_styles = (marker_styles * num_lines)[:num_lines]
    line_colors = (line_colors * num_lines)[:num_lines]

    fig, ax = plt.subplots(figsize=args.global_figsize)

    lines = []
    for y_data, label, color, style, width, marker in zip(
        line_data, line_labels, line_colors, line_styles, line_widths, marker_styles
    ):
        if horizontal:
            plot_kwargs = dict(
                color=color, linestyle=style, linewidth=width, label=label
            )
            if show_markers:
                plot_kwargs.update({"marker": marker, "markersize": 6})
            line = ax.plot(y_data, x_labels, **plot_kwargs)[0]
        else:
            plot_kwargs = dict(
                color=color, linestyle=style, linewidth=width, label=label
            )
            if show_markers:
                plot_kwargs.update({"marker": marker, "markersize": 6})
            line = ax.plot(x_labels, y_data, **plot_kwargs)[0]
        lines.append(line)

    if show_text_label:
        for y_data in line_data:
            if horizontal:
                for x_val, y_val in zip(x_labels, y_data):
                    ax.text(y_val * 1.02, x_val, f"{y_val:.1f}", ha="left", va="center", fontsize=8)
            else:
                for x_val, y_val in zip(x_labels, y_data):
                    ax.text(x_val, y_val * 1.02, f"{y_val:.1f}", ha="center", va="bottom", fontsize=8)

    if change_x_axis_pos:
        ax.xaxis.set_ticks_position("top")
        ax.xaxis.set_label_position("top")
    if change_y_axis_pos:
        ax.yaxis.set_ticks_position("right")
        ax.yaxis.set_label_position("right")

    if horizontal:
        ax.set_xlabel(y_label, fontsize=13)
        ax.set_ylabel(x_label, fontsize=13)
        ax.set_yticks(x_labels)
    else:
        ax.set_xlabel(x_label, fontsize=13)
        ax.set_ylabel(y_label, fontsize=13)
        ax.set_xticks(x_labels)

    ax.set_title(img_title, fontsize=16)

    if show_legend:
        ax.legend(loc="best")

    ax.grid(True, alpha=0.3)

    ax.spines["top"].set_visible(change_x_axis_pos)
    ax.spines["bottom"].set_visible(not change_x_axis_pos)
    ax.spines["right"].set_visible(change_y_axis_pos)
    ax.spines["left"].set_visible(not change_y_axis_pos)

    plt.tight_layout()

    if img_save_name:
        plt.savefig(img_save_name, dpi=300, bbox_inches="tight")

    return fig


def draw__4_line__func_1__mask(
    args,
    line_data: List[List[float]],
    line_labels: List[str],
    line_colors: List[str],
    x_labels: List[Union[int, float, str]],
    x_label: str,
    y_label: str,
    img_title: str,
    horizontal: bool = False,
    line_styles: List[str] = None,
    line_widths: List[float] = None,
    marker_styles: List[str] = None,
    show_markers: bool = False,
    show_text_label: bool = False,
    show_legend: bool = True,
    change_x_axis_pos: bool = False,
    change_y_axis_pos: bool = False,
    img_save_name: str = None,
    mask_color: str = None,
    mask_idx: List[int] = None,
):
    """Render a masked version of the line chart."""
    if mask_color is None:
        mask_color = args.gray_mask
    if mask_idx is None:
        mask_idx = []

    fig = draw__4_line__func_1(
        args=args,
        line_data=line_data,
        line_labels=line_labels,
        line_colors=copy.deepcopy(line_colors),
        x_labels=x_labels,
        x_label=x_label,
        y_label=y_label,
        img_title=img_title,
        horizontal=horizontal,
        line_styles=line_styles,
        line_widths=line_widths,
        marker_styles=marker_styles,
        show_markers=show_markers,
        show_text_label=show_text_label,
        show_legend=show_legend,
        change_x_axis_pos=change_x_axis_pos,
        change_y_axis_pos=change_y_axis_pos,
        img_save_name=None,
    )

    ax = fig.axes[0]
    renderer = fig.canvas.get_renderer()

    # Mask specific lines
    for idx, line in enumerate(ax.lines):
        if idx in mask_idx:
            path = line.get_path()
            verts = path.vertices
            if verts.size == 0:
                continue
            x_min, y_min = verts.min(axis=0)
            x_max, y_max = verts.max(axis=0)
            rect = plt.Rectangle(
                (x_min, y_min),
                x_max - x_min,
                y_max - y_min,
                transform=ax.transData,
                color=mask_color,
                zorder=100,
            )
            ax.add_patch(rect)

    # Mask legend entries if present
    legend = ax.get_legend()
    if show_legend and legend:
        texts = legend.get_texts()
        handles = legend.legend_handles
        for idx in mask_idx:
            if 0 <= idx < len(texts):
                bbox = texts[idx].get_window_extent(renderer=renderer)
                bbox_fig = bbox.transformed(fig.transFigure.inverted())
                rect = plt.Rectangle(
                    (bbox_fig.x0 - 0.005, bbox_fig.y0 - 0.005),
                    bbox_fig.width + 0.01,
                    bbox_fig.height + 0.01,
                    transform=fig.transFigure,
                    color=mask_color,
                    zorder=150,
                )
                fig.patches.append(rect)
            if 0 <= idx < len(handles):
                bbox = handles[idx].get_window_extent(renderer=renderer)
                bbox_fig = bbox.transformed(fig.transFigure.inverted())
                rect = plt.Rectangle(
                    (bbox_fig.x0 - 0.005, bbox_fig.y0 - 0.005),
                    bbox_fig.width + 0.01,
                    bbox_fig.height + 0.01,
                    transform=fig.transFigure,
                    color=mask_color,
                    zorder=150,
                )
                fig.patches.append(rect)

    if img_save_name:
        plt.savefig(img_save_name, dpi=300, bbox_inches="tight")

    return fig


# ---------------------------------------------------------------------------
# Run-draw orchestration
# ---------------------------------------------------------------------------
class LineChartRunDraw(RunDraw):
    """Concrete workflow for line chart generation."""

    def __init__(self, args):
        self.args = args
        self.function_dict = self._init_plot_functions()
        self.draw_chart_function = None
        self.draw_masked_chart_function = None
        self.total_img_num = 0
        self.total_vqa_num = 0
        self.root_path = f"{args.data_path}/imgs/{args.chart_type}/{args.chart_mode}"
        self.generated_vqa_data_save_path = f"{args.data_path}/{args.chart_type}__meta_qa_data.json"
        self.generated_vqa_data: Dict[str, Dict] = {}
        self._init_generated_chart_qa_data()

    def _init_plot_functions(self):
        return {
            "draw__4_line__func_1": {
                "original_img": draw__4_line__func_1,
                "masked_img": draw__4_line__func_1__mask,
            },
        }

    def _init_dir(self, dir_path):
        os.makedirs(dir_path, exist_ok=True)

    def _init_generated_chart_qa_data(self):
        if os.path.exists(self.generated_vqa_data_save_path):
            self.generated_vqa_data = read_from_json(self.generated_vqa_data_save_path)
        else:
            self.generated_vqa_data = {}

    def _check_if_skip_existing_data(self, vqa_id: str):
        if vqa_id in self.generated_vqa_data:
            logger.info(f"VQA data `{vqa_id}` already exists, skipping.")
            return True
        return False

    def _save_chart_qa_data_to_json(self):
        os.makedirs(os.path.dirname(self.generated_vqa_data_save_path), exist_ok=True)
        with open(self.generated_vqa_data_save_path, "w", encoding="utf-8") as fp:
            json.dump(self.generated_vqa_data, fp, indent=4, ensure_ascii=False)
        logger.info(f"Chart QA data saved to: {self.generated_vqa_data_save_path}")

    def _plot_masked_chart(
        self,
        mask_idx_list: List[int],
        chart_entry: Dict,
        chart_direction: str,
        line_styles: List[str],
        line_widths: List[float],
        marker_styles: List[str],
        show_markers: str,
        show_label: str,
        show_legend: str,
        x_axis_pos: str,
        y_axis_pos: str,
        chart_id: str,
        mask_id: str,
    ):
        if "0" in self.args.construction_subtask:
            self.draw_masked_chart_function(
                args=self.args,
                line_data=chart_entry["line_data"],
                line_labels=chart_entry["line_labels"],
                line_colors=chart_entry["line_colors"],
                x_labels=chart_entry["x_labels"],
                x_label=chart_entry["x_label"],
                y_label=chart_entry["y_label"],
                img_title=chart_entry["img_title"],
                horizontal=chart_direction == "horizontal",
                line_styles=line_styles,
                line_widths=line_widths,
                marker_styles=marker_styles,
                show_markers=show_markers == "w_markers",
                show_text_label=show_label == "labeled",
                show_legend=show_legend == "w_legend",
                change_x_axis_pos=x_axis_pos == "xtop",
                change_y_axis_pos=y_axis_pos == "yright",
                img_save_name=f"{self.root_path}/{mask_id}__gray_mask.png",
                mask_color=self.args.gray_mask,
                mask_idx=mask_idx_list,
            )

        if "2" in self.args.construction_subtask or "3" in self.args.construction_subtask:
            mask_generation(self.args, self.root_path, chart_id, mask_id)

    def run_draw_single_figure(self):
        self._init_dir(self.root_path)
        self.total_img_num = 0
        self.total_vqa_num = 0
        chart_idx = 0

        for func_id, categories in METADATA_LINE.items():
            self.draw_chart_function = self.function_dict[func_id]["original_img"]
            self.draw_masked_chart_function = self.function_dict[func_id]["masked_img"]

            for category_id, chart_entries in categories.items():
                for chart_entry in chart_entries:
                    for chart_direction in ["vertical", "horizontal"]:
                        for show_label in ["labeled"]:
                            for x_axis_pos in ["xtop", "xbottom"]:
                                for y_axis_pos in ["yleft", "yright"]:
                                    for show_markers in ["w_markers"]:
                                        for show_legend in ["w_legend"]:
                                            for line_styles in [["-", ":", "--", "-."]]:
                                                for line_widths in [[3.0, 3.0, 3.0, 3.0]]:
                                                    for marker_styles in [["o", "^", "s", "D"]]:
                                                        chart_idx += 1
                                                        chart_id = (
                                                            f"{self.args.chart_type}__img_{chart_idx}"
                                                            f"__category{category_id.split(' ')[0]}"
                                                            f"__{chart_direction}__{show_markers}"
                                                            f"__{show_label}__{show_legend}"
                                                            f"__{x_axis_pos}__{y_axis_pos}"
                                                        )
                                                        chart_entry["chart_direction"] = chart_direction

                                                        if "1" in self.args.construction_subtask:
                                                            self.draw_chart_function(
                                                                args=self.args,
                                                                line_data=chart_entry["line_data"],
                                                                line_labels=chart_entry["line_labels"],
                                                                line_colors=chart_entry["line_colors"],
                                                                x_labels=chart_entry["x_labels"],
                                                                x_label=chart_entry["x_label"],
                                                                y_label=chart_entry["y_label"],
                                                                img_title=chart_entry["img_title"],
                                                                horizontal=chart_direction == "horizontal",
                                                                line_styles=line_styles,
                                                                line_widths=line_widths,
                                                                marker_styles=marker_styles,
                                                                show_markers=show_markers == "w_markers",
                                                                show_text_label=show_label == "labeled",
                                                                show_legend=show_legend == "w_legend",
                                                                change_x_axis_pos=x_axis_pos == "xtop",
                                                                change_y_axis_pos=y_axis_pos == "yright",
                                                                img_save_name=f"{self.root_path}/{chart_id}.png",
                                                            )

                                                        self.vqa_generator = LineChartGenerator(self.args, chart_id)
                                                        qa_candidates = self.vqa_generator.chart_qa_generator(
                                                            chart_metadata=chart_entry,
                                                            random_seed=42,
                                                            num_questions=20,
                                                        )

                                                        for new_qa_data in qa_candidates:
                                                            new_qa_id = new_qa_data["qa_id"]
                                                            if self._check_if_skip_existing_data(new_qa_id):
                                                                continue

                                                            mask_paths = {}
                                                            for step_key in new_qa_data["mask"]:
                                                                mask_paths[
                                                                    step_key
                                                                ] = f"./data/imgs/{self.args.chart_type}/{self.args.chart_mode}/{new_qa_id}__mask_{step_key}.png"

                                                            self.total_vqa_num += 1
                                                            self.generated_vqa_data[new_qa_id] = {
                                                                "qa_id": new_qa_id,
                                                                "qa_type": new_qa_data["qa_type"],
                                                                "chart_type": self.args.chart_mode,
                                                                "category": category_id,
                                                                "curriculum_level": new_qa_data["curriculum_level"],
                                                                "constraint": new_qa_data["constraint"],
                                                                "eval_mode": show_label,
                                                                "img_path": f"./data/imgs/{self.args.chart_type}/{self.args.chart_mode}/{chart_id}.png",
                                                                "mask_path": mask_paths,
                                                                "mask_indices": new_qa_data["mask"],
                                                                "question": new_qa_data["question"],
                                                                "reasoning": new_qa_data["reasoning"],
                                                                "answer": new_qa_data["answer"],
                                                            }

                                                            for step_key, mask_idx_list in new_qa_data["mask"].items():
                                                                mask_id = (
                                                                    mask_paths[step_key]
                                                                    .split("/")[-1]
                                                                    .replace(".png", "")
                                                                    .strip()
                                                                )
                                                                self._plot_masked_chart(
                                                                    mask_idx_list=mask_idx_list,
                                                                    chart_entry=chart_entry,
                                                                    chart_direction=chart_direction,
                                                                    line_styles=line_styles,
                                                                    line_widths=line_widths,
                                                                    marker_styles=marker_styles,
                                                                    show_markers=show_markers,
                                                                    show_label=show_label,
                                                                    show_legend=show_legend,
                                                                    x_axis_pos=x_axis_pos,
                                                                    y_axis_pos=y_axis_pos,
                                                                    chart_id=chart_id,
                                                                    mask_id=mask_id,
                                                                )

                                                            self._save_chart_qa_data_to_json()
                                                            self.total_img_num = chart_idx

        self._save_chart_qa_data_to_json()
        logger.info(
            f"Line chart generation complete. Images: {self.total_img_num} | "
            f"QA examples: {self.total_vqa_num}"
        )


__all__ = ["LineChartRunDraw", "draw__4_line__func_1", "draw__4_line__func_1__mask"]

