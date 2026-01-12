"""
Workflow for heatmap chart rendering, QA generation, and mask creation.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np

project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from metadata.metadata import METADATA_HEATMAP
from chartGenerators.heatmap.heatmap_chart_generator import HeatmapChartGenerator
from utils.logger import logger
from utils.json_util import read_from_json
from utils.masks.mask_generator import mask_generation
from templates.run_draw import RunDraw


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------
def draw__7_heatmap__func_1(
    args,
    heatmap_data: Union[List[List[float]], np.ndarray],
    x_labels: List[str],
    y_labels: List[str],
    x_label: str,
    y_label: str,
    img_title: str,
    colormap: str = "Set3",
    show_values: bool = False,
    show_colorbar: bool = True,
    change_x_axis_pos: bool = False,
    change_y_axis_pos: bool = False,
    img_save_name: str = None,
):
    """Render a heatmap."""
    heatmap_data = np.array(heatmap_data)
    fig, ax = plt.subplots(figsize=args.global_figsize)

    im = ax.imshow(heatmap_data, cmap=colormap, aspect="auto")

    ax.set_xticks(np.arange(len(x_labels)))
    ax.set_yticks(np.arange(len(y_labels)))
    ax.set_xticklabels(x_labels)
    ax.set_yticklabels(y_labels)

    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    if change_x_axis_pos:
        ax.xaxis.tick_top()
        ax.xaxis.set_label_position("top")
        plt.setp(ax.get_xticklabels(), rotation=45, ha="left", rotation_mode="anchor")

    if change_y_axis_pos:
        ax.yaxis.tick_right()
        ax.yaxis.set_label_position("right")

    ax.set_xlabel(x_label, fontsize=13)
    ax.set_ylabel(y_label, fontsize=13)
    ax.set_title(img_title, fontsize=16)

    if show_values:
        for i in range(len(y_labels)):
            for j in range(len(x_labels)):
                ax.text(j, i, f"{heatmap_data[i, j]:.2f}", ha="center", va="center", color="black")

    if show_colorbar:
        plt.colorbar(im, ax=ax)

    plt.tight_layout()

    if img_save_name:
        plt.savefig(img_save_name, dpi=300, bbox_inches="tight")

    return fig


def draw__7_heatmap__func_1__mask(
    args,
    heatmap_data: Union[List[List[float]], np.ndarray],
    x_labels: List[str],
    y_labels: List[str],
    x_label: str,
    y_label: str,
    img_title: str,
    colormap: str = "Set3",
    show_values: bool = False,
    show_colorbar: bool = True,
    change_x_axis_pos: bool = False,
    change_y_axis_pos: bool = False,
    img_save_name: str = None,
    mask_color: str = None,
    mask_cells: List[Tuple[int, int]] = None,
    mask_rows: List[int] = None,
    mask_cols: List[int] = None,
):
    """Render a masked heatmap by overlaying rectangles over target cells."""
    if mask_color is None:
        mask_color = args.gray_mask
    if mask_cells is None:
        mask_cells = []
    if mask_rows is None:
        mask_rows = []
    if mask_cols is None:
        mask_cols = []

    heatmap_data = np.array(heatmap_data)
    fig, ax = plt.subplots(figsize=args.global_figsize)

    im = ax.imshow(heatmap_data, cmap=colormap, aspect="auto")
    ax.set_xticks(np.arange(len(x_labels)))
    ax.set_yticks(np.arange(len(y_labels)))
    ax.set_xticklabels(x_labels)
    ax.set_yticklabels(y_labels)

    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    if change_x_axis_pos:
        ax.xaxis.tick_top()
        ax.xaxis.set_label_position("top")
        plt.setp(ax.get_xticklabels(), rotation=45, ha="left", rotation_mode="anchor")

    if change_y_axis_pos:
        ax.yaxis.tick_right()
        ax.yaxis.set_label_position("right")

    ax.set_xlabel(x_label, fontsize=13)
    ax.set_ylabel(y_label, fontsize=13)
    ax.set_title(img_title, fontsize=16)

    if show_values:
        for i in range(len(y_labels)):
            for j in range(len(x_labels)):
                ax.text(j, i, f"{heatmap_data[i, j]:.2f}", ha="center", va="center", color="black")

    if show_colorbar:
        plt.colorbar(im, ax=ax)

    # Mask specific cells
    for row, col in mask_cells:
        rect = plt.Rectangle(
            (col - 0.5, row - 0.5),
            1,
            1,
            linewidth=0,
            edgecolor=mask_color,
            facecolor=mask_color,
            alpha=1.0,
            zorder=100,
        )
        ax.add_patch(rect)

    # Mask entire rows
    for row in mask_rows:
        rect = plt.Rectangle(
            (-0.5, row - 0.5),
            len(x_labels),
            1,
            linewidth=0,
            edgecolor=mask_color,
            facecolor=mask_color,
            alpha=1.0,
            zorder=90,
        )
        ax.add_patch(rect)

    # Mask entire columns
    for col in mask_cols:
        rect = plt.Rectangle(
            (col - 0.5, -0.5),
            1,
            len(y_labels),
            linewidth=0,
            edgecolor=mask_color,
            facecolor=mask_color,
            alpha=1.0,
            zorder=90,
        )
        ax.add_patch(rect)

    plt.tight_layout()

    if img_save_name:
        plt.savefig(img_save_name, dpi=300, bbox_inches="tight")

    return fig


# ---------------------------------------------------------------------------
# RunDraw implementation
# ---------------------------------------------------------------------------
class HeatmapChartRunDraw(RunDraw):
    """Concrete workflow runner for heatmap charts."""

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
            "draw__7_heatmap__func_1": {
                "original_img": draw__7_heatmap__func_1,
                "masked_img": draw__7_heatmap__func_1__mask,
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

    def _index_to_cell(self, idx: int, num_cols: int) -> Tuple[int, int]:
        if num_cols == 0:
            return 0, 0
        return idx // num_cols, idx % num_cols

    def _plot_masked_chart(
        self,
        mask_idx_list: List[int],
        chart_entry: Dict,
        chart_id: str,
        mask_id: str,
    ):
        num_rows = len(chart_entry["heatmap_data"])
        num_cols = len(chart_entry["heatmap_data"][0]) if num_rows else 0
        mask_cells = [self._index_to_cell(idx, num_cols) for idx in mask_idx_list]

        if "0" in self.args.construction_subtask:
            self.draw_masked_chart_function(
                args=self.args,
                heatmap_data=chart_entry["heatmap_data"],
                x_labels=chart_entry["x_labels"],
                y_labels=chart_entry["y_labels"],
                x_label=chart_entry["x_label"],
                y_label=chart_entry["y_label"],
                img_title=chart_entry["img_title"],
                colormap="Set3",
                show_values=False,
                show_colorbar=True,
                change_x_axis_pos=False,
                change_y_axis_pos=False,
                img_save_name=f"{self.root_path}/{mask_id}__gray_mask.png",
                mask_color=self.args.gray_mask,
                mask_cells=mask_cells,
                mask_rows=[],
                mask_cols=[],
            )

        if "2" in self.args.construction_subtask or "3" in self.args.construction_subtask:
            mask_generation(self.args, self.root_path, chart_id, mask_id)

    def run_draw_single_figure(self):
        self._init_dir(self.root_path)
        self.total_img_num = 0
        self.total_vqa_num = 0
        chart_idx = 0

        for func_id, categories in METADATA_HEATMAP.items():
            self.draw_chart_function = self.function_dict[func_id]["original_img"]
            self.draw_masked_chart_function = self.function_dict[func_id]["masked_img"]

            for category_id, chart_entries in categories.items():
                for chart_entry in chart_entries:
                    chart_idx += 1
                    chart_id = f"{self.args.chart_type}__img_{chart_idx}__category{category_id.split(' ')[0]}"

                    if "1" in self.args.construction_subtask:
                        self.draw_chart_function(
                            args=self.args,
                            heatmap_data=chart_entry["heatmap_data"],
                            x_labels=chart_entry["x_labels"],
                            y_labels=chart_entry["y_labels"],
                            x_label=chart_entry["x_label"],
                            y_label=chart_entry["y_label"],
                            img_title=chart_entry["img_title"],
                            colormap="Set3",
                            show_values=False,
                            show_colorbar=True,
                            change_x_axis_pos=False,
                            change_y_axis_pos=False,
                            img_save_name=f"{self.root_path}/{chart_id}.png",
                        )

                    self.vqa_generator = HeatmapChartGenerator(self.args, chart_id)
                    qa_candidates = self.vqa_generator.chart_qa_generator(
                        chart_metadata=chart_entry, random_seed=42, num_questions=20
                    )

                    for qa_data in qa_candidates:
                        qa_id = qa_data["qa_id"]
                        if self._check_if_skip_existing_data(qa_id):
                            continue

                        mask_paths = {}
                        for step_key in qa_data["mask"]:
                            mask_paths[
                                step_key
                            ] = f"./data/imgs/{self.args.chart_type}/{self.args.chart_mode}/{qa_id}__mask_{step_key}.png"

                        self.total_vqa_num += 1
                        self.generated_vqa_data[qa_id] = {
                            "qa_id": qa_id,
                            "qa_type": qa_data["qa_type"],
                            "chart_type": self.args.chart_mode,
                            "category": category_id,
                            "curriculum_level": qa_data["curriculum_level"],
                            "constraint": qa_data["constraint"],
                            "eval_mode": "labeled",
                            "img_path": f"./data/imgs/{self.args.chart_type}/{self.args.chart_mode}/{chart_id}.png",
                            "mask_path": mask_paths,
                            "mask_indices": qa_data["mask"],
                            "question": qa_data["question"],
                            "reasoning": qa_data["reasoning"],
                            "answer": qa_data["answer"],
                        }

                        for step_key, mask_idx_list in qa_data["mask"].items():
                            mask_id = (
                                mask_paths[step_key].split("/")[-1].replace(".png", "").strip()
                            )
                            self._plot_masked_chart(
                                mask_idx_list=mask_idx_list,
                                chart_entry=chart_entry,
                                chart_id=chart_id,
                                mask_id=mask_id,
                            )

                        self._save_chart_qa_data_to_json()
                        self.total_img_num = chart_idx

        self._save_chart_qa_data_to_json()
        logger.info(
            f"Heatmap generation complete. Images: {self.total_img_num} | "
            f"QA examples: {self.total_vqa_num}"
        )


__all__ = ["HeatmapChartRunDraw", "draw__7_heatmap__func_1", "draw__7_heatmap__func_1__mask"]

