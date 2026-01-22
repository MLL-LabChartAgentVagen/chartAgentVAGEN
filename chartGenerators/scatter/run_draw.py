"""
Scatter chart
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

from metadata.metadata import METADATA_SCATTER
from utils.masks.mask_generator import mask_generation
from chartGenerators.scatter.scatter_chart_generator import ScatterChartGenerator
from utils.logger import logger
from utils.json_util import read_from_json


def _place_legend_outside_scatter(ax, scatter_points, scatter_labels, change_x_axis_pos, change_y_axis_pos, scatter_size_in_legend):
    """
    Place legend outside the plot area to prevent overlap with chart content.
    Uses dynamic spacing based on legend size.
    
    Args:
        ax: Matplotlib axes object
        scatter_points: List of scatter plot objects
        scatter_labels: Labels for the legend
        change_x_axis_pos: Whether x-axis is at top
        change_y_axis_pos: Whether y-axis is at right
        scatter_size_in_legend: Size for markers in legend
    
    Returns:
        Legend object
    """
    fig = ax.figure
    
    # First, do a tight layout to fit the plot content
    plt.tight_layout()
    
    # Get initial axes position
    initial_bbox = ax.get_position()
    
    # Determine best side for legend based on axis positions
    if change_y_axis_pos:
        # Y-axis on right, place legend on left side of plot
        bbox_to_anchor = (0.0, 0.5)  # At left edge of axes
        loc = 'center right'
        side = 'left'
    else:
        # Y-axis on left, place legend on right side of plot
        bbox_to_anchor = (1.0, 0.5)  # At right edge of axes
        loc = 'center left'
        side = 'right'
    
    # Create legend outside the plot area (in axes coordinates)
    legend = ax.legend(scatter_points, scatter_labels, loc=loc, bbox_to_anchor=bbox_to_anchor, 
                      frameon=True, fancybox=True, shadow=True, markerscale=0.8)
    
    # Set marker sizes in legend
    for handle in legend.legend_handles:
        handle.set_sizes([scatter_size_in_legend])
    
    # Draw the figure to get accurate measurements
    fig.canvas.draw()
    
    # Get the legend's bounding box in figure coordinates
    legend_bbox_fig = legend.get_window_extent().transformed(fig.transFigure.inverted())
    
    # Get current subplot position in figure coordinates
    bbox = ax.get_position()
    
    # Calculate how much space we need and adjust subplot
    if side == 'right':
        # Legend is on the right side of plot
        # Calculate space needed: legend width + small padding
        legend_width = legend_bbox_fig.width
        padding = 0.015  # 1.5% padding
        total_needed = legend_width + padding
        
        # Calculate new right edge, ensuring we don't shrink too much
        max_right = 0.98
        new_right = min(max_right, bbox.x1 - total_needed)
        
        # Only adjust if we need to make room and won't shrink too much
        min_width = 0.15  # Keep at least 15% of figure width for plot
        if new_right < bbox.x1 and (new_right - bbox.x0) >= min_width:
            ax.set_position([bbox.x0, bbox.y0, new_right - bbox.x0, bbox.height])
            # Update legend position to stay outside
            legend.set_bbox_to_anchor((1.0, 0.5))
    else:
        # Legend is on the left side of plot
        legend_width = legend_bbox_fig.width
        padding = 0.015
        total_needed = legend_width + padding
        
        # Calculate new left edge
        min_left = 0.02
        new_left = max(min_left, bbox.x0 + total_needed)
        
        # Only adjust if we need to make room and won't shrink too much
        min_width = 0.15
        if new_left > bbox.x0 and (bbox.x1 - new_left) >= min_width:
            ax.set_position([new_left, bbox.y0, bbox.x1 - new_left, bbox.height])
            # Update legend position to stay outside
            legend.set_bbox_to_anchor((0.0, 0.5))
            legend.set_loc('center right')
    
    return legend


# ============================================================
#                        Function 1
# Draw a scatter plot with customizable axes, colors, sizes, and positioning.
# ============================================================
def draw__3_scatter__func_1(
        args,
        scatter_x_data: List,
        scatter_y_data: List,
        scatter_labels: List,
        scatter_colors: List,
        scatter_sizes: List,
        x_label: str,
        y_label: str,
        img_title: str,
        horizontal: bool=False,
        show_text_label: bool=False,
        show_legend: bool=False,
        change_x_axis_pos: bool=False,
        change_y_axis_pos: bool=False,
        img_save_name: str=None,
        scatter_size_in_legend: int=100,
    ):
    """
    Draw a scatter plot with customizable axes, colors, sizes, and positioning.
    
    This function creates a scatter plot with specified x and y data values, labels, colors, and sizes.
    It allows for customization of orientation (horizontal or vertical), axis positions, 
    display of data point labels, and saving the resulting chart.
    
    IMPORTANT NOTE ON PARAMETERS:
    - When horizontal=False (default): 
      * Normal scatter plot with x_label on x-axis and y_label on y-axis
      
    - When horizontal=True: 
      * Scatter plot is flipped - x and y data are swapped
      * x_label is used for the y-axis and y_label is used for the x-axis
      * The axis labels are effectively swapped to maintain logical orientation
    
    Args:
        args: Configuration object containing global figure settings
        scatter_x_data (List): A list of numerical values for x-axis positions (or y-axis if horizontal=True)
        scatter_y_data (List): A list of numerical values for y-axis positions (or x-axis if horizontal=True)
        scatter_labels (List): A list of strings for the scatter point labels
        scatter_colors (List): A list of hex color codes for the scatter points
        scatter_sizes (List): A list of numerical values for the scatter point sizes
        x_label (str): The label for categories axis (x-axis in vertical mode, y-axis in horizontal mode)
        y_label (str): The label for values axis (y-axis in vertical mode, x-axis in horizontal mode)
        img_title (str): The title of the chart
        horizontal (bool, optional): If True, scatter plot is flipped; if False, normal orientation. Default is False.
        show_text_label (bool, optional): If True, displays labels next to each scatter point. Default is False.
        show_legend (bool, optional): If True, show the legend; if False, hide the legend. Default is False.
        change_x_axis_pos (bool, optional): If True, X axis is at the top; if False, at the bottom. Default is False.
        change_y_axis_pos (bool, optional): If True, Y axis is at the right; if False, at the left. Default is False.
        img_save_name (str, optional): Filepath to save the image. If None, image is not saved. Default is None.
    
    Returns:
        matplotlib.figure.Figure: The figure object containing the scatter plot
    """
    # Create figure
    fig, ax = plt.subplots(figsize=args.global_figsize)
    
    # Create scatter plot based on orientation
    scatter_points = []
    if horizontal:
        # Swap x and y data for horizontal orientation
        for i in range(len(scatter_x_data)):
            scatter = ax.scatter(
                scatter_y_data[i],  # y_data becomes x-axis
                scatter_x_data[i],  # x_data becomes y-axis
                c=scatter_colors[i], 
                s=scatter_sizes[i],
                label=scatter_labels[i] if show_legend else None,
                alpha=0.7
            )
            scatter_points.append(scatter)
    else:
        # Normal orientation
        for i in range(len(scatter_x_data)):
            scatter = ax.scatter(
                scatter_x_data[i], 
                scatter_y_data[i], 
                c=scatter_colors[i], 
                s=scatter_sizes[i],
                label=scatter_labels[i] if show_legend else None,
                alpha=0.7
            )
            scatter_points.append(scatter)
    
    # Add text labels next to scatter points
    if show_text_label:
        if change_y_axis_pos:
            ha_align = 'right'
        else:
            ha_align = 'left'

        for i in range(len(scatter_x_data)):
            if horizontal:
                # For horizontal orientation, swap coordinates
                ax.annotate(
                    scatter_labels[i], 
                    (scatter_y_data[i], scatter_x_data[i]),
                    xytext=(10, 10), 
                    textcoords='offset points',
                    fontsize=10,
                    ha=ha_align
                )
            else:
                # Normal orientation
                ax.annotate(
                    scatter_labels[i], 
                    (scatter_x_data[i], scatter_y_data[i]),
                    xytext=(10, 10), 
                    textcoords='offset points',
                    fontsize=10,
                    ha=ha_align
                )
    
    # Set the position of the axes
    if change_x_axis_pos:
        ax.xaxis.set_ticks_position('top')
        ax.xaxis.set_label_position('top')
    
    if change_y_axis_pos:
        ax.yaxis.set_ticks_position('right')
        ax.yaxis.set_label_position('right')
    
    # Set labels and title
    # When horizontal=True, we need to swap the axis labels
    if horizontal:
        ax.set_xlabel(y_label, fontsize=13)  # X-axis gets the original y_label
        ax.set_ylabel(x_label, fontsize=13)  # Y-axis gets the original x_label
    else:
        ax.set_xlabel(x_label, fontsize=13)
        ax.set_ylabel(y_label, fontsize=13)
    ax.set_title(img_title, fontsize=16)
    
    # Add legend outside plot area to prevent overlap
    legend = None
    if show_legend:
        legend = _place_legend_outside_scatter(ax, scatter_points, scatter_labels, 
                                               change_x_axis_pos, change_y_axis_pos, 
                                               scatter_size_in_legend)
    else:
        # Adjust layout only if no legend
        plt.tight_layout()
    
    # Add grid for better readability
    ax.grid(True, alpha=0.3)
    
    # Hide non-axis spines based on axis positions
    if change_x_axis_pos:
        # X-axis is at top, hide bottom spine
        ax.spines['bottom'].set_visible(False)
    else:
        # X-axis is at bottom, hide top spine
        ax.spines['top'].set_visible(False)
    
    if change_y_axis_pos:
        # Y-axis is at right, hide left spine
        ax.spines['left'].set_visible(False)
    else:
        # Y-axis is at left, hide right spine
        ax.spines['right'].set_visible(False)
    
    # Adjust layout to make sure everything fits
    plt.tight_layout()
    
    # Save the image if a save path is provided
    if img_save_name:
        plt.savefig(img_save_name, dpi=300)
    
    return fig


def draw__3_scatter__func_1__mask(
        args,
        scatter_x_data: List,
        scatter_y_data: List,
        scatter_labels: List,
        scatter_colors: List,
        scatter_sizes: List,
        x_label: str,
        y_label: str,
        img_title: str,
        horizontal: bool=False,
        show_text_label: bool=False,
        show_legend: bool=False,
        change_x_axis_pos: bool=False,
        change_y_axis_pos: bool=False,
        img_save_name: str=None,
        mask_color: str=None,
        mask_idx: list=None,
        scatter_size_in_legend: int=100,
    ):
    """
    Draw a scatter plot with customizable colors, labels, and positioning, with masking capability.
    
    This function creates a scatter plot with specified data values, labels, and colors,
    and applies masking to specified scatter points.
    
    Args:
        args: Configuration object containing global figure settings
        scatter_x_data (List): A list of numerical values for x-axis positions
        scatter_y_data (List): A list of numerical values for y-axis positions
        scatter_labels (List): A list of strings for the scatter point labels
        scatter_colors (List): A list of hex color codes for the scatter points
        scatter_sizes (List): A list of numerical values for the scatter point sizes
        x_label (str): The label for x-axis
        y_label (str): The label for y-axis
        img_title (str): The title of the chart
        horizontal (bool, optional): If True, scatter plot is flipped; if False, normal orientation. Default is False.
        show_text_label (bool, optional): If True, displays labels next to each scatter point. Default is False.
        show_legend (bool, optional): If True, show the legend; if False, hide the legend. Default is False.
        change_x_axis_pos (bool, optional): If True, X axis is at the top; if False, at the bottom. Default is False.
        change_y_axis_pos (bool, optional): If True, Y axis is at the right; if False, at the left. Default is False.
        img_save_name (str, optional): Filepath to save the image. If None, image is not saved. Default is None.
        mask_color (str, optional): Color to use for masking. If None, uses args.gray_mask. Default is None.
        mask_idx (List[int], optional): List of scatter point indices to mask. If None, no masking is applied. Default is None.
    
    Returns:
        matplotlib.figure.Figure: The figure object containing the masked scatter plot
    """
    if mask_color is None:
        mask_color = args.gray_mask
    
    # Validate mask_idx
    if mask_idx is None:
        mask_idx = []
    
    # Create figure
    fig, ax = plt.subplots(figsize=args.global_figsize)
    
    # Create scatter plot based on orientation
    scatter_points = []
    if horizontal:
        # Swap x and y data for horizontal orientation
        for i in range(len(scatter_x_data)):
            scatter = ax.scatter(
                scatter_y_data[i],  # y_data becomes x-axis
                scatter_x_data[i],  # x_data becomes y-axis
                c=scatter_colors[i], 
                s=scatter_sizes[i],
                label=scatter_labels[i] if show_legend else None,
                alpha=0.7
            )
            scatter_points.append(scatter)
    else:
        # Normal orientation
        for i in range(len(scatter_x_data)):
            scatter = ax.scatter(
                scatter_x_data[i], 
                scatter_y_data[i], 
                c=scatter_colors[i], 
                s=scatter_sizes[i],
                label=scatter_labels[i] if show_legend else None,
                alpha=0.7
            )
            scatter_points.append(scatter)
    
    # Add text labels next to scatter points
    if show_text_label:
        if change_y_axis_pos:
            ha_align = 'right'
        else:
            ha_align = 'left'

        for i in range(len(scatter_x_data)):
            if horizontal:
                # For horizontal orientation, swap coordinates
                ax.annotate(
                    scatter_labels[i], 
                    (scatter_y_data[i], scatter_x_data[i]),
                    xytext=(10, 10), 
                    textcoords='offset points',
                    fontsize=10,
                    ha=ha_align
                )
            else:
                # Normal orientation
                ax.annotate(
                    scatter_labels[i], 
                    (scatter_x_data[i], scatter_y_data[i]),
                    xytext=(10, 10), 
                    textcoords='offset points',
                    fontsize=10,
                    ha=ha_align
                )
    
    # Set the position of the axes
    if change_x_axis_pos:
        ax.xaxis.set_ticks_position('top')
        ax.xaxis.set_label_position('top')
    
    if change_y_axis_pos:
        ax.yaxis.set_ticks_position('right')
        ax.yaxis.set_label_position('right')
    
    # Set labels and title
    # When horizontal=True, we need to swap the axis labels
    if horizontal:
        ax.set_xlabel(y_label, fontsize=13)  # X-axis gets the original y_label
        ax.set_ylabel(x_label, fontsize=13)  # Y-axis gets the original x_label
    else:
        ax.set_xlabel(x_label, fontsize=13)
        ax.set_ylabel(y_label, fontsize=13)
    ax.set_title(img_title, fontsize=16)
    
    # Add legend outside plot area to prevent overlap
    legend = None
    if show_legend:
        legend = _place_legend_outside_scatter(ax, scatter_points, scatter_labels, 
                                               change_x_axis_pos, change_y_axis_pos, 
                                               scatter_size_in_legend)
    else:
        # Adjust layout only if no legend
        plt.tight_layout()
    
    # Add grid for better readability
    ax.grid(True, alpha=0.3)
    
    # Hide non-axis spines based on axis positions
    if change_x_axis_pos:
        # X-axis is at top, hide bottom spine
        ax.spines['bottom'].set_visible(False)
    else:
        # X-axis is at bottom, hide top spine
        ax.spines['top'].set_visible(False)
    
    if change_y_axis_pos:
        # Y-axis is at right, hide left spine
        ax.spines['left'].set_visible(False)
    else:
        # Y-axis is at left, hide right spine
        ax.spines['right'].set_visible(False)
    
    # Adjust layout to make sure everything fits
    plt.tight_layout()
    
    # Apply masking if mask_idx is provided
    if mask_idx:
        # Draw the canvas to get proper coordinates
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        
        # Mask scatter points
        for idx in mask_idx:
            if 0 <= idx < len(scatter_points):
                scatter = scatter_points[idx]
                # Get the scatter point's position
                if horizontal:
                    x_pos = scatter_y_data[idx]
                    y_pos = scatter_x_data[idx]
                else:
                    x_pos = scatter_x_data[idx]
                    y_pos = scatter_y_data[idx]
                
                # Get the size of the scatter point
                size = scatter_sizes[idx]
                # Approximate radius (scatter size is in points^2, so we need to convert)
                radius = np.sqrt(size / np.pi) * 0.01  # Rough conversion
                
                # Create a circle to mask the scatter point
                circle = plt.Circle(
                    (x_pos, y_pos),
                    radius,
                    transform=ax.transData,
                    color=mask_color,
                    zorder=10
                )
                ax.add_patch(circle)
        
        # Mask text labels if shown
        if show_text_label:
            for idx in mask_idx:
                if 0 <= idx < len(scatter_labels):
                    # Find the annotation text
                    for text in ax.texts:
                        if text.get_text() == scatter_labels[idx]:
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
        
        # Mask legend entries if present
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
                    
                    # Mask legend handle (the colored marker)
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
        plt.savefig(img_save_name, dpi=300)
    
    return fig


class ScatterChartRunDraw(RunDraw):
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
            "draw__3_scatter__func_1": {
                "original_img": draw__3_scatter__func_1,
                "masked_img": draw__3_scatter__func_1__mask,
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
            horizontal: str,
            show_text_label: str,
            show_legend: str,
            change_x_axis_pos: str,
            change_y_axis_pos: str,
            chart_id: str,
            mask_id: str,
        ):
        # Subtask 0: Generate image with masked color (0_auto_maskcolor)
        if '0' in self.args.construction_subtask:
            self.draw_masked_chart_function(
                args=self.args, 
                scatter_x_data=chart_entry["scatter_x_data"], 
                scatter_y_data=chart_entry["scatter_y_data"], 
                scatter_labels=chart_entry["scatter_labels"], 
                scatter_colors=chart_entry["scatter_colors"],
                scatter_sizes=chart_entry["scatter_sizes"],
                x_label=chart_entry["x_label"],
                y_label=chart_entry["y_label"],
                img_title=chart_entry["img_title"],
                horizontal=horizontal=="horizontal",
                show_text_label=show_text_label=="labeled",
                show_legend=show_legend=="w_legend",
                change_x_axis_pos=change_x_axis_pos=="xtop",
                change_y_axis_pos=change_y_axis_pos=="yright",
                img_save_name=f"{self.root_path}/{mask_id}__gray_mask.png",
                mask_color=self.args.gray_mask,
                mask_idx=mask_idx_list,
            )
        
        # Subtask 2-3: Generate mask
        if ('2' in self.args.construction_subtask) or ('3' in self.args.construction_subtask):
            mask_generation(self.args, self.root_path, chart_id, f"{mask_id}")

    def run_draw_single_figure(self):
        """Scatter chart generation"""
        # Single chart generation
        self._init_dir(self.root_path)
        self.total_img_num = 0
        self.total_vqa_num = 0
        chart_idx = 0  # track image num
        entry_idx = -1

        for func_id in METADATA_SCATTER.keys():
            self.draw_chart_function = self.function_dict[func_id]["original_img"]
            self.draw_masked_chart_function = self.function_dict[func_id]["masked_img"]

            for category_id in METADATA_SCATTER[func_id].keys():
                # List of entries
                chart_metadata = METADATA_SCATTER[func_id][category_id]

                for chart_index, chart_entry in enumerate(chart_metadata):
                    entry_idx += 1

                    for chart_direction in ["vertical", "horizontal"]:
                        for show_label in ["labeled"]:  # currently all labeled for strict eval
                            for x_axis_pos in ["xtop", "xbottom"]:
                                for y_axis_pos in ["yleft", "yright"]:
                                    for show_legend in ["w_legend"]:  # currently all with legend for strict eval
                                        chart_idx += 1
                                        chart_id = f"{self.args.chart_type}__img_{chart_idx}__category{category_id.split(' ')[0]}__{chart_direction}__{show_label}__{show_legend}__{x_axis_pos}__{y_axis_pos}"
                                        chart_entry["chart_direction"] = chart_direction
                                        logger.info(
                                            f"{'=' * 100}"
                                            f"\n{' ' * 10} Image Index: {chart_idx}"
                                            f"\n{' ' * 10} Chart ID: {chart_id}"
                                            f"\n{'=' * 100}"
                                        )

                                        # Subtask 1: Original chart
                                        if '1' in self.args.construction_subtask:
                                            self.draw_chart_function(
                                                args=self.args, 
                                                scatter_x_data=chart_entry["scatter_x_data"], 
                                                scatter_y_data=chart_entry["scatter_y_data"], 
                                                scatter_labels=chart_entry["scatter_labels"], 
                                                scatter_colors=chart_entry["scatter_colors"],
                                                scatter_sizes=chart_entry["scatter_sizes"],
                                                x_label=chart_entry["x_label"],
                                                y_label=chart_entry["y_label"],
                                                img_title=chart_entry["img_title"],
                                                horizontal=chart_direction=="horizontal",
                                                show_text_label=show_label=="labeled",
                                                show_legend=show_legend=="w_legend",
                                                change_x_axis_pos=x_axis_pos=="xtop",
                                                change_y_axis_pos=y_axis_pos=="yright",
                                                img_save_name=f"{self.root_path}/{chart_id}.png",
                                            )

                                        # Init chart QA data generator
                                        self.vqa_generator = ScatterChartGenerator(self.args, chart_id)                                            

                                        # Chart QA data generation & mask chart
                                        # Pass func_id, category_id, and chart_index for hardcoded questions
                                        qa_data_condidates = self.vqa_generator.chart_qa_generator(
                                            chart_metadata=chart_entry,
                                            func_id=func_id,
                                            category=category_id,
                                            chart_index=chart_index,
                                            use_hardcoded=True,  # Enable hardcoded questions
                                            use_random=True,     # Enable random questions
                                            random_seed=42,
                                            num_questions=20
                                        )

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
                                                "eval_mode": show_label,
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
                                                    horizontal=chart_direction,
                                                    show_text_label=show_label,
                                                    show_legend=show_legend,
                                                    change_x_axis_pos=x_axis_pos,
                                                    change_y_axis_pos=y_axis_pos,
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

