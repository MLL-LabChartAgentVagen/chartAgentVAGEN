"""
Pie chart
"""

import os
import json
import copy
import numpy as np
import pandas as pd
from typing import List, Dict
import seaborn as sns
import matplotlib.pyplot as plt

from abc import ABC, abstractmethod
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
from templates.run_draw import RunDraw

from metadata.metadata import METADATA_PIE
from utils.masks.mask_generator import mask_generation
from chartGenerators.pie_chart.pie_chart_generator import PieChartGenerator
from utils.logger import logger
from utils.json_util import read_from_json


# ============================================================
#                        Function 1
# Draw a pie chart with customizable colors, labels, and positioning.
# ============================================================
def draw__8_pie__func_1(
        args,
        pie_data: List,
        pie_labels: List,
        pie_colors: List,
        img_title: str,
        show_percentages: bool = False,
        show_values: bool = False,
        show_legend: bool = True,
        explode_slices: List = None,
        startangle: float = 90,
        autopct_format: str = '%1.1f%%',
        img_save_name: str = None,
    ):
    """
    Draw a pie chart with customizable colors, labels, and positioning.
    
    This function creates a pie chart with specified data values, labels, and colors.
    It allows for customization of slice explosion, percentage display, legend, and saving the resulting chart.
    
    Args:
        args: Configuration object containing global figure settings
        pie_data (List): A list of numerical values for the pie slice sizes
        pie_labels (List): A list of strings for the pie slice labels
        pie_colors (List): A list of hex color codes for the pie slices
        img_title (str): The title of the chart
        show_percentages (bool, optional): If True, displays percentages on pie slices. Default is False.
        show_values (bool, optional): If True, displays actual values on pie slices. Default is False.
        show_legend (bool, optional): If True, show the legend; if False, hide the legend. Default is True.
        explode_slices (List, optional): List of explosion distances for each slice. If None, no explosion. Default is None.
        startangle (float, optional): Angle to start the first slice. Default is 90.
        autopct_format (str, optional): Format string for percentage display. Default is '%1.1f%%'.
        img_save_name (str, optional): Filepath to save the image. If None, image is not saved. Default is None.
    
    Returns:
        matplotlib.figure.Figure: The figure object containing the pie chart
    """
    # Create figure
    fig, ax = plt.subplots(figsize=args.global_figsize)
    
    # Prepare autopct parameter
    autopct = None
    if show_percentages and show_values:
        # Custom function to show both percentages and values
        def make_autopct(values):
            def my_autopct(pct):
                total = sum(values)
                val = int(round(pct*total/100.0))
                return f'{pct:.1f}%\n({val})'
            return my_autopct
        autopct = make_autopct(pie_data)
    elif show_percentages:
        autopct = autopct_format
    elif show_values:
        # Custom function to show only values
        def make_autopct_values(values):
            def my_autopct(pct):
                total = sum(values)
                val = int(round(pct*total/100.0))
                return f'{val}'
            return my_autopct
        autopct = make_autopct_values(pie_data)
    
    # Create the pie chart
    wedges, texts, autotexts = ax.pie(
        pie_data,
        labels=pie_labels,
        colors=pie_colors,
        autopct=autopct,
        startangle=startangle,
        explode=explode_slices,
        textprops={'fontsize': 12}
    )
    
    # Set title
    ax.set_title(img_title, fontsize=16, pad=20)
    
    # Add legend
    if show_legend:
        ax.legend(wedges, pie_labels, title="Categories", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    
    # Ensure the pie chart is circular
    ax.axis('equal')
    
    # Adjust layout to make sure everything fits
    plt.tight_layout()
    
    # Save the image if a save path is provided
    if img_save_name:
        plt.savefig(img_save_name, dpi=300, bbox_inches='tight')
    
    return fig


def draw__8_pie__func_1__mask(
        args,
        pie_data: List,
        pie_labels: List,
        pie_colors: List,
        img_title: str,
        show_percentages: bool = False,
        show_values: bool = False,
        show_legend: bool = True,
        explode_slices: List = None,
        startangle: float = 90,
        autopct_format: str = '%1.1f%%',
        img_save_name: str = None,
        mask_color: str = None,
        mask_idx: List[int] = None,
    ):
    """
    Draw a pie chart with customizable colors, labels, and positioning, with masking capability.
    
    This function creates a pie chart with specified data values, labels, and colors,
    and applies masking to specified slices.
    
    Args:
        args: Configuration object containing global figure settings
        pie_data (List): A list of numerical values for the pie slice sizes
        pie_labels (List): A list of strings for the pie slice labels
        pie_colors (List): A list of hex color codes for the pie slices
        img_title (str): The title of the chart
        show_percentages (bool, optional): If True, displays percentages on pie slices. Default is False.
        show_values (bool, optional): If True, displays actual values on pie slices. Default is False.
        show_legend (bool, optional): If True, show the legend; if False, hide the legend. Default is True.
        explode_slices (List, optional): List of explosion distances for each slice. If None, no explosion. Default is None.
        startangle (float, optional): Angle to start the first slice. Default is 90.
        autopct_format (str, optional): Format string for percentage display. Default is '%1.1f%%'.
        img_save_name (str, optional): Filepath to save the image. If None, image is not saved. Default is None.
        mask_color (str, optional): Color to use for masking. If None, uses args.gray_mask. Default is None.
        mask_idx (List[int], optional): List of slice indices to mask. If None, no masking is applied. Default is None.
    
    Returns:
        matplotlib.figure.Figure: The figure object containing the masked pie chart
    """
    if mask_color is None:
        mask_color = args.gray_mask
    
    # Validate mask_idx
    if mask_idx is None:
        mask_idx = []
    
    # Create figure
    fig, ax = plt.subplots(figsize=args.global_figsize)
    
    # Prepare autopct parameter
    autopct = None
    if show_percentages and show_values:
        # Custom function to show both percentages and values
        def make_autopct(values):
            def my_autopct(pct):
                total = sum(values)
                val = int(round(pct*total/100.0))
                return f'{pct:.1f}%\n({val})'
            return my_autopct
        autopct = make_autopct(pie_data)
    elif show_percentages:
        autopct = autopct_format
    elif show_values:
        # Custom function to show only values
        def make_autopct_values(values):
            def my_autopct(pct):
                total = sum(values)
                val = int(round(pct*total/100.0))
                return f'{val}'
            return my_autopct
        autopct = make_autopct_values(pie_data)
    
    # Create the pie chart with original colors (we'll mask with rectangles later)
    wedges, texts, autotexts = ax.pie(
        pie_data,
        labels=pie_labels,
        colors=pie_colors,
        autopct=autopct,
        startangle=startangle,
        explode=explode_slices,
        textprops={'fontsize': 12}
    )
    
    # Set title
    ax.set_title(img_title, fontsize=16, pad=20)
    
    # Add legend
    legend = None
    if show_legend:
        legend = ax.legend(wedges, pie_labels, title="Categories", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    
    # Ensure the pie chart is circular
    ax.axis('equal')
    
    # Adjust layout to make sure everything fits
    plt.tight_layout()
    
    # Apply masking if mask_idx is provided
    if mask_idx:
        # Draw the canvas to get proper coordinates
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        
        # 1. Mask the pie slices with tight bounding boxes (no padding beyond max points)
        for idx in mask_idx:
            if 0 <= idx < len(wedges):
                wedge = wedges[idx]
                # Get the wedge's path and vertices
                path = wedge.get_path()
                vertices = path.vertices
                
                # Calculate tight bounding box of the wedge
                x_coords = vertices[:, 0]
                y_coords = vertices[:, 1]
                
                x_min, x_max = np.min(x_coords), np.max(x_coords)
                y_min, y_max = np.min(y_coords), np.max(y_coords)
                
                # Create rectangle with exact bounding box (no padding)
                width = x_max - x_min
                height = y_max - y_min
                
                rect = plt.Rectangle(
                    (x_min, y_min),
                    width, height,
                    transform=ax.transData,
                    color=mask_color,
                    zorder=10  # Place above the pie slices
                )
                ax.add_patch(rect)
        
        # 2. Mask the slice labels (outside the pie)
        for idx in mask_idx:
            if 0 <= idx < len(texts):
                text = texts[idx]
                bbox = text.get_window_extent(renderer=renderer)
                bbox_fig = bbox.transformed(fig.transFigure.inverted())
                
                rect = plt.Rectangle(
                    (bbox_fig.x0 - 0.01, bbox_fig.y0 - 0.005),
                    bbox_fig.width + 0.02, bbox_fig.height + 0.01,
                    transform=fig.transFigure,
                    color=mask_color,
                    zorder=100
                )
                fig.patches.append(rect)
        
        # 3. Mask the autopct text (percentages/values inside slices)
        if autotexts:
            for idx in mask_idx:
                if 0 <= idx < len(autotexts):
                    text = autotexts[idx]
                    bbox = text.get_window_extent(renderer=renderer)
                    bbox_fig = bbox.transformed(fig.transFigure.inverted())
                    
                    rect = plt.Rectangle(
                        (bbox_fig.x0 - 0.005, bbox_fig.y0 - 0.005),
                        bbox_fig.width + 0.01, bbox_fig.height + 0.01,
                        transform=fig.transFigure,
                        color=mask_color,
                        zorder=100
                    )
                    fig.patches.append(rect)
        
        # 4. Mask the legend if present
        if show_legend and legend:
            legend_texts = legend.get_texts()
            legend_handles = legend.legend_handles
            
            for idx in mask_idx:
                if 0 <= idx < len(legend_texts):
                    # Mask legend text
                    text = legend_texts[idx]
                    bbox = text.get_window_extent(renderer=renderer)
                    bbox_fig = bbox.transformed(fig.transFigure.inverted())
                    
                    rect = plt.Rectangle(
                        (bbox_fig.x0 - 0.005, bbox_fig.y0 - 0.005),
                        bbox_fig.width + 0.01, bbox_fig.height + 0.01,
                        transform=fig.transFigure,
                        color=mask_color,
                        zorder=100
                    )
                    fig.patches.append(rect)
                    
                    # Mask legend handle (the colored patch)
                    if 0 <= idx < len(legend_handles):
                        handle = legend_handles[idx]
                        bbox = handle.get_window_extent(renderer=renderer)
                        bbox_fig = bbox.transformed(fig.transFigure.inverted())
                        
                        rect = plt.Rectangle(
                            (bbox_fig.x0 - 0.005, bbox_fig.y0 - 0.005),
                            bbox_fig.width + 0.01, bbox_fig.height + 0.01,
                            transform=fig.transFigure,
                            color=mask_color,
                            zorder=100
                        )
                        fig.patches.append(rect)
    
    # Save the image if a filename is provided
    if img_save_name:
        plt.savefig(img_save_name, dpi=300, bbox_inches='tight')
    
    return fig


class PieChartRunDraw(RunDraw):
    def __init__(self, args):
        self.args = args
        self.function_dict = self._init_plot_functions()
        self.draw_chart_function = None
        self.total_img_num = 0
        self.root_path = f"{args.data_path}/imgs/{args.chart_type}/{args.chart_mode}"
        self.generated_vqa_data_save_path = f"{args.data_path}/{args.chart_type}__meta_qa_data.json"
        self.generated_vqa_data = {}
        self._init_generated_chart_qa_data()

    def _init_plot_functions(self):
        function_dict = {
            "draw__8_pie__func_1": {
                "original_img": draw__8_pie__func_1,
                "masked_img": draw__8_pie__func_1__mask,
            },
        }
        return function_dict

    def _init_dir(self, dir_path):
        os.makedirs(dir_path, exist_ok=True)

    def _init_generated_chart_qa_data(self):
        if os.path.exists(self.generated_vqa_data_save_path):
            self.generated_vqa_data = read_from_json(self.generated_vqa_data_save_path)
        else:
            self.generated_vqa_data = {}

    def _check_if_skip_existing_data(self, vqa_id: str):
        if vqa_id in self.generated_vqa_data.keys():
            print(f"VQA data `{vqa_id}` already exists, skipping current construction entry...")
            return True
        else:
            return False

    def _save_chart_qa_data_to_json(self):
        """
        Save the generated VQA data dictionary to a JSON file.
        
        The function saves self.generated_vqa_data to the file path 
        specified by self.generated_vqa_data_save_path.
        """        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.generated_vqa_data_save_path), exist_ok=True)
        
        # Write the JSON data to file with pretty formatting
        with open(self.generated_vqa_data_save_path, 'w', encoding='utf-8') as f:
            json.dump(self.generated_vqa_data, f, indent=4, ensure_ascii=False)
            
        logger.info(f"Chart QA data successfully saved to: {self.generated_vqa_data_save_path}")

    def _plot_masked_chart(
            self,
            mask_idx_list: List,
            chart_entry: Dict,
            show_percentages: str,
            show_values: str,
            show_legend: str,
            explode_slices: str,
            chart_id: str,
            mask_id: str,
        ):
        # Subtask 0: Generate image with masked color (0_auto_maskcolor)
        if '0' in self.args.construction_subtask:
            self.draw_masked_chart_function(
                args=self.args, 
                pie_data=chart_entry["pie_data"], 
                pie_labels=chart_entry["pie_labels"], 
                pie_colors=chart_entry["pie_colors"],
                img_title=chart_entry["img_title"],
                show_percentages=show_percentages=="w_percent",
                show_values=show_values=="w_value",
                show_legend=show_legend=="w_legend",
                explode_slices=explode_slices,
                img_save_name=f"{self.root_path}/{mask_id}__gray_mask.png",
                mask_color=self.args.gray_mask,
                mask_idx=mask_idx_list,
            )
        
        # Subtask 2-3: Generate mask
        if ('2' in self.args.construction_subtask) or ('3' in self.args.construction_subtask):
            mask_generation(self.args, self.root_path, chart_id, f"{mask_id}")

    def run_draw_single_figure(self):
        """Pie chart generation"""
        # Single chart generation
        self._init_dir(self.root_path)
        self.total_img_num = 0
        self.total_vqa_num = 0
        chart_idx = 0  # track image num
        entry_idx = -1

        for func_id in METADATA_PIE.keys():
            self.draw_chart_function = self.function_dict[func_id]["original_img"]
            self.draw_masked_chart_function = self.function_dict[func_id]["masked_img"]

            for category_id in METADATA_PIE[func_id].keys():
                # List of entries
                chart_metadata = METADATA_PIE[func_id][category_id]

                for chart_entry in chart_metadata:
                    entry_idx += 1

                    for show_percentages in ["w_percent"]:  # currently all showing percentages for strict eval, or set to ["w_percent", "wo_percent"] when with LLM-as-a-judge
                        for show_values in ["w_value"]:  # currently all labeled for strict eval, or set to ["w_value", "wo_value"] when with LLM-as-a-judge
                            for show_legend in ["w_legend"]:  # currently all with legend for strict eval, or set to ["w_legend", "wo_legend"] when with LLM-as-a-judge
                                for explode_slice_dix in range(5):  # fixed number of segments: 5
                                    for startangle in [0, 30, 45, 60, 90]:
                                        chart_idx += 1
                                        chart_id = f"{self.args.chart_type}__img_{chart_idx}__category{category_id.split(' ')[0]}__{show_percentages}__{show_values}__{show_legend}__segment{explode_slice_dix}__angle{startangle}"
                                        chart_entry["chart_direction"] = "circular"  # Pie charts are always circular
                                        logger.info(
                                            f"{'=' * 100}"
                                            f"\n{' ' * 10} Image Index: {chart_idx}"
                                            f"\n{' ' * 10} Chart ID: {chart_id}"
                                            f"\n{'=' * 100}"
                                        )
                                        assert len(chart_entry["pie_data"]) == 5
                                        explode_slices = [0 for _ in range(5)]
                                        explode_slices[explode_slice_dix] = 0.1

                                        # Subtask 1: Original chart
                                        if '1' in self.args.construction_subtask:
                                            self.draw_chart_function(
                                                args=self.args, 
                                                pie_data=chart_entry["pie_data"], 
                                                pie_labels=chart_entry["pie_labels"], 
                                                pie_colors=chart_entry["pie_colors"],
                                                img_title=chart_entry["img_title"],
                                                show_percentages=show_percentages=="w_percent",
                                                show_values=show_values=="w_value",
                                                show_legend=show_legend=="w_legend",
                                                explode_slices=explode_slices,
                                                img_save_name=f"{self.root_path}/{chart_id}.png",
                                            )

                                        # Init chart QA data generator
                                        self.vqa_generator = PieChartGenerator(self.args, chart_id)                                            

                                        # Chart QA data generation & mask chart
                                        qa_data_condidates = self.vqa_generator.chart_qa_generator(chart_entry)

                                        for new_qa_data in qa_data_condidates:
                                            new_qa_id = new_qa_data["qa_id"]

                                            if self._check_if_skip_existing_data(new_qa_id):
                                                continue

                                            # Mask paths
                                            new_mask_path = {}
                                            for step_key in new_qa_data["mask"]:
                                                new_mask_path[step_key] = f"./data/imgs/{self.args.chart_type}/{self.args.chart_mode}/{new_qa_id}__mask_{step_key}.png"

                                            # Save to self.generated_vqa_data
                                            self.total_vqa_num += 1
                                            self.generated_vqa_data[new_qa_id] = {
                                                "qa_id": new_qa_id,
                                                "qa_type": new_qa_data["qa_type"],
                                                "chart_type": self.args.chart_mode,
                                                "category": category_id,
                                                "curriculum_level": new_qa_data["curriculum_level"],
                                                "constraint": new_qa_data["constraint"],
                                                "eval_mode": show_percentages,
                                                "img_path": f"./data/imgs/{self.args.chart_type}/{self.args.chart_mode}/{chart_id}.png",
                                                "mask_path": new_mask_path,
                                                "mask_indices": new_qa_data["mask"],
                                                "question": new_qa_data["question"],
                                                "reasoning": new_qa_data["reasoning"],
                                                "answer": new_qa_data["answer"],
                                            }
                                            
                                            # Generate masked chart
                                            for step_key in new_mask_path:
                                                curr_mask_id = new_mask_path[step_key].split("/")[-1].replace(".png", "").strip()
                                                self._plot_masked_chart(
                                                    mask_idx_list=new_qa_data["mask"][step_key],
                                                    chart_entry=chart_entry,
                                                    show_percentages=show_percentages,
                                                    show_values=show_values,
                                                    show_legend=show_legend,
                                                    explode_slices=explode_slices,
                                                    chart_id=chart_id,
                                                    mask_id=curr_mask_id,
                                                )

                                            # Save
                                            self._save_chart_qa_data_to_json()

                                            # Progress
                                            self.total_img_num = chart_idx
                                            logger.info(
                                                f"\n{'=' * 100}"
                                                f"\n{' ' * 8} Total number of source images:  {self.total_img_num}"
                                                f"\n{' ' * 8} Total number of chart QA data:  {self.total_vqa_num}"
                                                f"\n{'=' * 100}\n"
                                            )
                                            
        # Final save
        self._save_chart_qa_data_to_json()
        logger.info(
            f"\n{'=' * 100}"
            f"\n{' ' * 8} Total number of source images:  {self.total_img_num}"
            f"\n{' ' * 8} Total number of chart QA data:  {self.total_vqa_num}"
            f"\n{'=' * 100}\n"
        )

