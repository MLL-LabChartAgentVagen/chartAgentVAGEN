"""
Bar chart
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

from metadata.metadata import METADATA_BAR
from utils.masks.mask_generator import mask_generation
from chartGenerators.bar_chart.bar_chart_generator import BarChartGenerator
from utils.logger import logger
from utils.json_util import read_from_json


# ============================================================
#                        Function 1
# Draw a bar chart with X and Y axises, different bars in different colors, and the corresponding legend(s)
# 
# Args:
#   - data
#       - bar_data (list): a list of data as bar values on the Y axis
#       - bar_labels (list): a list of data as bar labels on the X axis
#       - bar_colors (list): a list of hex colors
#       - x_label (str): a string as the title of the X axis
#       - y_label (str): a string as the title of the Y axis
#       - img_title (str): a string as the title of image
#   - manipulations
#       - horizontal (bool): the direction of bars as either horizontal or vertical (set to False for vertical, set to True for horizontal)
#       - show_text_label (bool): whether to show the value label of each bar (set to False to hide all bar values as textual labels, set to True to show all bar values as textual labels)
#       - show_legend (bool): whether to show chart legend(s)  (set to False to hide chart legend(s), set to True to show chart legend(s))
#       - change_x_axis_pos (bool): the position of the X axis (set to False to place the X axis at the bottom of the chart, set to True to place the X axis at the top of the chart)
#       - change_y_axis_pos (bool): the position of the Y axis (set to False to place the Y axis at the left of the chart, set to True to place the X axis at the right of the chart)
#   - save the image
#       - img_save_name (str): the absolute image save path to be used as `plt.savefig(img_save_name, dpi=300)`
# ============================================================
def draw__1_bar__func_1(
        args,
        bar_data: List,
        bar_labels: List,
        bar_colors: List,
        x_label: str,
        y_label: str,
        img_title: str,
        label_angle: int,
        horizontal: bool=False,
        show_text_label: bool=False,
        show_legend: bool=False,
        change_x_axis_pos: bool=False,
        change_y_axis_pos: bool=False,
        img_save_name: str=None,
    ):
    """
    Draw a bar chart with customizable axes, colors, and positioning.
    
    This function creates a bar chart with specified data values, labels, and colors.
    It allows for customization of bar orientation (horizontal or vertical),
    axis positions, display of data value labels, and saving the resulting chart.
    
    IMPORTANT NOTE ON PARAMETERS:
    - When horizontal=False (default): 
      * bar_labels appear on the x-axis (rotated 45 degrees)
      * bar_data values are displayed on the y-axis
      * x_label labels the x-axis (categories) 
      * y_label labels the y-axis (values)
      
    - When horizontal=True: 
      * bar_labels appear on the y-axis
      * bar_data values are displayed on the x-axis
      * x_label is used for the y-axis (categories)
      * y_label is used for the x-axis (values)
      * The axis labels are effectively swapped to maintain logical orientation
    
    Args:
        args: Configuration object containing global figure settings
        bar_data (List): A list of numerical values for the bar heights/lengths
        bar_labels (List): A list of strings for the bar categories/labels
        bar_colors (List): A list of hex color codes for the bars
        x_label (str): The label for categories axis (x-axis in vertical mode, y-axis in horizontal mode)
        y_label (str): The label for values axis (y-axis in vertical mode, x-axis in horizontal mode)
        img_title (str): The title of the chart
        horizontal (bool, optional): If True, bars are drawn horizontally; if False, vertically. Default is False.
        show_text_label (bool, optional): If True, displays the data value on each bar. Default is False.
        show_legend (bool, optional): If True, show the legend; if False, hide the legend. Default is False.
        change_x_axis_pos (bool, optional): If True, X axis is at the top; if False, at the bottom. Default is False.
        change_y_axis_pos (bool, optional): If True, Y axis is at the right; if False, at the left. Default is False.
        img_save_name (str, optional): Filepath to save the image. If None, image is not saved. Default is None.
    
    Returns:
        matplotlib.figure.Figure: The figure object containing the bar chart
    """
    # Create figure
    fig, ax = plt.subplots(figsize=args.global_figsize)
    
    # Set positions for bars
    positions = np.arange(len(bar_data))
    
    # Draw bars based on orientation
    if horizontal:
        # Horizontal bars (categories on y-axis, values on x-axis)
        bars = ax.barh(positions, bar_data, color=bar_colors)
    else:
        # Vertical bars (categories on x-axis, values on y-axis)
        bars = ax.bar(positions, bar_data, color=bar_colors)
    
    # Add text labels on bars
    if show_text_label:
        for i, bar in enumerate(bars):
            if horizontal:
                # For horizontal bars, text is to the right of the bar end
                x_pos = bar.get_width() * 1.01
                y_pos = bar.get_y() + bar.get_height() / 2
                ax.text(x_pos, y_pos, f'{bar_data[i]}', va='center')
            else:
                # For vertical bars, text is above the bar
                x_pos = bar.get_x() + bar.get_width() / 2
                y_pos = bar.get_height() * 1.01
                ax.text(x_pos, y_pos, f'{bar_data[i]}', ha='center')
    
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
    
    # Set the tick labels based on orientation
    if horizontal:
        # For horizontal bars, categories are on y-axis
        ax.set_yticks(positions)
        ax.set_yticklabels(bar_labels)
    else:
        # For vertical bars, categories are on x-axis
        ax.set_xticks(positions)
        ha_config = 'left' if change_x_axis_pos else 'right'
        ax.set_xticklabels(bar_labels, rotation=label_angle, ha=ha_config)
        plt.subplots_adjust(bottom=0.2)  # Add more space for rotated labels
    
    # Add legend
    if show_legend:
        ax.legend(bars, bar_labels, loc='best')
    
    # Adjust layout to make sure everything fits
    plt.tight_layout()
    
    # Save the image if a save path is provided
    if img_save_name:
        plt.savefig(img_save_name, dpi=300)
    
    return fig


def draw__1_bar__func_1__mask(
        args,
        bar_data: List,
        bar_labels: List,
        bar_colors: List,
        x_label: str,
        y_label: str,
        img_title: str,
        label_angle: int,
        horizontal: bool=False,
        show_text_label: bool=False,
        show_legend: bool=False,
        change_x_axis_pos: bool=False,
        change_y_axis_pos: bool=False,
        img_save_name: str=None,
        mask_color: str=None,
        mask_idx: list=None,
    ):
    """
    Draw a bar chart with customizable axes, colors, and positioning, with masking capability.
    
    IMPORTANT NOTE ON PARAMETERS:
    - When horizontal=False (default): 
      * bar_labels appear on the x-axis (rotated 45 degrees)
      * bar_data values are displayed on the y-axis
      * x_label labels the x-axis (categories) 
      * y_label labels the y-axis (values)
      
    - When horizontal=True: 
      * bar_labels appear on the y-axis
      * bar_data values are displayed on the x-axis
      * x_label is used for the y-axis (categories)
      * y_label is used for the x-axis (values)
      * The axis labels are effectively swapped to maintain logical orientation
    
    Args:
        args: Configuration object containing global figure settings
        bar_data (List): A list of numerical values for the bar heights/lengths
        bar_labels (List): A list of strings for the bar categories/labels
        bar_colors (List): A list of hex color codes for the bars
        x_label (str): The label for categories axis (x-axis in vertical mode, y-axis in horizontal mode)
        y_label (str): The label for values axis (y-axis in vertical mode, x-axis in horizontal mode)
        img_title (str): The title of the chart
        horizontal (bool, optional): If True, bars are drawn horizontally; if False, vertically. Default is False.
        show_text_label (bool, optional): If True, displays the data value on each bar. Default is False.
        show_legend (bool, optional): If True, show the legend; if False, hide the legend. Default is False.
        change_x_axis_pos (bool, optional): If True, X axis is at the top; if False, at the bottom. Default is False.
        change_y_axis_pos (bool, optional): If True, Y axis is at the right; if False, at the left. Default is False.
        img_save_name (str, optional): Filepath to save the image. If None, image is not saved. Default is None.
        mask_color (str, optional): Color to use for masking. If None, uses args.gray_mask. Default is None.
        mask_idx (list, optional): List of indices to mask. If None, no masking is applied. Default is None.
    
    Returns:
        matplotlib.figure.Figure: The figure object containing the masked bar chart
    """
    if mask_color is None:
        mask_color = args.gray_mask
    
    # Validate mask_idx
    if mask_idx is None:
        mask_idx = []
    
    # Create a copy of colors list to mask specific bars
    masked_colors = bar_colors.copy()
    
    # Apply mask color to the specified bar indices
    for idx in mask_idx:
        if 0 <= idx < len(masked_colors):
            masked_colors[idx] = mask_color
    
    # Create figure
    fig, ax = plt.subplots(figsize=args.global_figsize)
    
    # Set positions for bars
    positions = np.arange(len(bar_data))
    
    # Draw bars based on orientation with masked colors
    if horizontal:
        # Horizontal bars (categories on y-axis, values on x-axis)
        bars = ax.barh(positions, bar_data, color=masked_colors)
    else:
        # Vertical bars (categories on x-axis, values on y-axis)
        bars = ax.bar(positions, bar_data, color=masked_colors)
    
    # Add text labels on bars
    if show_text_label:
        for i, bar in enumerate(bars):
            if horizontal:
                # For horizontal bars, text is to the right of the bar end
                x_pos = bar.get_width() * 1.01
                y_pos = bar.get_y() + bar.get_height() / 2
                ax.text(x_pos, y_pos, f'{bar_data[i]}', va='center')
            else:
                # For vertical bars, text is above the bar
                x_pos = bar.get_x() + bar.get_width() / 2
                y_pos = bar.get_height() * 1.01
                ax.text(x_pos, y_pos, f'{bar_data[i]}', ha='center')
    
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
    
    # Set the tick labels based on orientation
    if horizontal:
        # For horizontal bars, categories are on y-axis
        ax.set_yticks(positions)
        ax.set_yticklabels(bar_labels)
    else:
        # For vertical bars, categories are on x-axis
        ax.set_xticks(positions)
        ha_config = 'left' if change_x_axis_pos else 'right'
        ax.set_xticklabels(bar_labels, rotation=label_angle, ha=ha_config)
        plt.subplots_adjust(bottom=0.2)  # Add more space for rotated labels
    
    # Add legend
    if show_legend:
        legend = ax.legend(bars, bar_labels, loc='best')
    
    # Adjust layout to make sure everything fits
    plt.tight_layout()
    
    # Now apply specific masks only for valid mask_idx
    if mask_idx:
        # 1. Mask the text labels on the bars if present by adjusting style
        if show_text_label:
            for idx in mask_idx:
                if 0 <= idx < len(bars) and idx < len(ax.texts):
                    text = ax.texts[idx]
                    text.set_color(mask_color)
                    text.set_alpha(0.0)
        
        # 2. Mask the category labels based on orientation by dimming them
        if horizontal:
            labels = ax.get_yticklabels()
        else:
            labels = ax.get_xticklabels()
            
        for idx in mask_idx:
            if 0 <= idx < len(labels):
                label = labels[idx]
                label.set_color(mask_color)
                label.set_alpha(0.0)
        
        # 3. Mask the legend if present by dimming text and handles
        if show_legend and legend:
            texts = legend.get_texts()
            handles = legend.legend_handles
            
            for idx in mask_idx:
                if 0 <= idx < len(texts):
                    texts[idx].set_color(mask_color)
                    texts[idx].set_alpha(0.0)
                if 0 <= idx < len(handles):
                    handle = handles[idx]
                    if hasattr(handle, "set_facecolor"):
                        handle.set_facecolor(mask_color)
                    if hasattr(handle, "set_edgecolor"):
                        handle.set_edgecolor(mask_color)
    
    # Save the image if a filename is provided
    if img_save_name:
        plt.savefig(img_save_name, dpi=300)
    
    return fig


def draw__1_bar__func_1__axis_mask(
        args,
        bar_data: List,
        bar_labels: List,
        bar_colors: List,
        x_label: str,
        y_label: str,
        img_title: str,
        label_angle: int,
        horizontal: bool=False,
        show_text_label: bool=False,
        show_legend: bool=False,
        change_x_axis_pos: bool=False,
        change_y_axis_pos: bool=False,
        img_save_name: str=None,
        mask_color: str=None,
        mask_axis: str='y',
    ):
    """
    Draw a bar chart with customizable axes, colors, and positioning, with axis masking capability.
    
    This function creates a bar chart and can mask entire axes (x or y) including all labels,
    tick marks, and axis lines. When horizontal=True, the axis interpretation is swapped:
    - mask_axis='x' will mask the y-axis (categories axis in horizontal mode)
    - mask_axis='y' will mask the x-axis (values axis in horizontal mode)
    
    IMPORTANT NOTE ON PARAMETERS:
    - When horizontal=False (default): 
      * bar_labels appear on the x-axis (rotated 45 degrees)
      * bar_data values are displayed on the y-axis
      * x_label labels the x-axis (categories) 
      * y_label labels the y-axis (values)
      
    - When horizontal=True: 
      * bar_labels appear on the y-axis
      * bar_data values are displayed on the x-axis
      * x_label is used for the y-axis (categories)
      * y_label is used for the x-axis (values)
      * The axis labels are effectively swapped to maintain logical orientation
    
    Args:
        args: Configuration object containing global figure settings
        bar_data (List): A list of numerical values for the bar heights/lengths
        bar_labels (List): A list of strings for the bar categories/labels
        bar_colors (List): A list of hex color codes for the bars
        x_label (str): The label for categories axis (x-axis in vertical mode, y-axis in horizontal mode)
        y_label (str): The label for values axis (y-axis in vertical mode, x-axis in horizontal mode)
        img_title (str): The title of the chart
        horizontal (bool, optional): If True, bars are drawn horizontally; if False, vertically. Default is False.
        show_text_label (bool, optional): If True, displays the data value on each bar. Default is False.
        show_legend (bool, optional): If True, show the legend; if False, hide the legend. Default is False.
        change_x_axis_pos (bool, optional): If True, X axis is at the top; if False, at the bottom. Default is False.
        change_y_axis_pos (bool, optional): If True, Y axis is at the right; if False, at the left. Default is False.
        img_save_name (str, optional): Filepath to save the image. If None, image is not saved. Default is None.
        mask_color (str, optional): Color to use for masking. If None, uses args.gray_mask. Default is None.
        mask_axis (str, optional): Axis to mask ('x' or 'y'). Default is 'y'.
    
    Returns:
        matplotlib.figure.Figure: The figure object containing the bar chart with masked axis
    """
    if mask_color is None:
        mask_color = args.gray_mask
    
    # Create figure
    fig, ax = plt.subplots(figsize=args.global_figsize)
    
    # Set positions for bars
    positions = np.arange(len(bar_data))
    
    # Draw bars based on orientation
    if horizontal:
        # Horizontal bars (categories on y-axis, values on x-axis)
        bars = ax.barh(positions, bar_data, color=bar_colors)
    else:
        # Vertical bars (categories on x-axis, values on y-axis)
        bars = ax.bar(positions, bar_data, color=bar_colors)
    
    # Add text labels on bars
    if show_text_label:
        for i, bar in enumerate(bars):
            if horizontal:
                # For horizontal bars, text is to the right of the bar end
                x_pos = bar.get_width() * 1.01
                y_pos = bar.get_y() + bar.get_height() / 2
                ax.text(x_pos, y_pos, f'{bar_data[i]}', va='center')
            else:
                # For vertical bars, text is above the bar
                x_pos = bar.get_x() + bar.get_width() / 2
                y_pos = bar.get_height() * 1.01
                ax.text(x_pos, y_pos, f'{bar_data[i]}', ha='center')
    
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
    
    # Set the tick labels based on orientation
    if horizontal:
        # For horizontal bars, categories are on y-axis
        ax.set_yticks(positions)
        ax.set_yticklabels(bar_labels)
    else:
        # For vertical bars, categories are on x-axis
        ax.set_xticks(positions)
        ha_config = 'left' if change_x_axis_pos else 'right'
        ax.set_xticklabels(bar_labels, rotation=label_angle, ha=ha_config)
        plt.subplots_adjust(bottom=0.2)  # Add more space for rotated labels
    
    # Add legend
    if show_legend:
        legend = ax.legend(bars, bar_labels, loc='best')
    
    # Adjust layout to make sure everything fits
    plt.tight_layout()
    
    # Apply axis masking
    if mask_axis in ['x', 'y']:
        # Draw the canvas to get proper coordinates
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        
        # Determine which physical axis to mask based on orientation and mask_axis
        if horizontal:
            # In horizontal mode: mask_axis='x' masks y-axis, mask_axis='y' masks x-axis
            mask_physical_x = (mask_axis == 'y')
            mask_physical_y = (mask_axis == 'x')
        else:
            # In vertical mode: mask_axis='x' masks x-axis, mask_axis='y' masks y-axis
            mask_physical_x = (mask_axis == 'x')
            mask_physical_y = (mask_axis == 'y')
        
        # Mask X-axis components (bottom or top)
        if mask_physical_x:
            # Mask x-axis label
            xlabel = ax.xaxis.label
            if xlabel.get_text():
                bbox = xlabel.get_window_extent(renderer=renderer)
                bbox_fig = bbox.transformed(fig.transFigure.inverted())
                rect = plt.Rectangle(
                    (bbox_fig.x0 - 0.01, bbox_fig.y0 - 0.01),
                    bbox_fig.width + 0.02, bbox_fig.height + 0.02,
                    transform=fig.transFigure,
                    color=mask_color,
                    zorder=100
                )
                fig.patches.append(rect)
            
            # Mask x-axis tick labels
            for label in ax.get_xticklabels():
                if label.get_text():
                    bbox = label.get_window_extent(renderer=renderer)
                    bbox_fig = bbox.transformed(fig.transFigure.inverted())
                    # Extra padding for rotated labels
                    padding = 0.015 if not horizontal else 0.01
                    rect = plt.Rectangle(
                        (bbox_fig.x0 - padding, bbox_fig.y0 - padding),
                        bbox_fig.width + (padding * 2), bbox_fig.height + (padding * 2),
                        transform=fig.transFigure,
                        color=mask_color,
                        zorder=100
                    )
                    fig.patches.append(rect)
            
            # Mask x-axis line and ticks
            # Get the axis position (top or bottom)
            if change_x_axis_pos:
                # X-axis is at the top
                y_axis_line = ax.transData.transform([(ax.get_xlim()[0], ax.get_ylim()[1]), 
                                                     (ax.get_xlim()[1], ax.get_ylim()[1])])
            else:
                # X-axis is at the bottom
                y_axis_line = ax.transData.transform([(ax.get_xlim()[0], ax.get_ylim()[0]), 
                                                     (ax.get_xlim()[1], ax.get_ylim()[0])])
            
            y_axis_line_fig = fig.transFigure.inverted().transform(y_axis_line)
            
            # Create a rectangle to mask the axis line
            rect = plt.Rectangle(
                (y_axis_line_fig[0][0] - 0.01, y_axis_line_fig[0][1] - 0.01),
                y_axis_line_fig[1][0] - y_axis_line_fig[0][0] + 0.02, 0.02,
                transform=fig.transFigure,
                color=mask_color,
                zorder=100
            )
            fig.patches.append(rect)
        
        # Mask Y-axis components (left or right)
        if mask_physical_y:
            # Mask y-axis label
            ylabel = ax.yaxis.label
            if ylabel.get_text():
                bbox = ylabel.get_window_extent(renderer=renderer)
                bbox_fig = bbox.transformed(fig.transFigure.inverted())
                rect = plt.Rectangle(
                    (bbox_fig.x0 - 0.01, bbox_fig.y0 - 0.01),
                    bbox_fig.width + 0.02, bbox_fig.height + 0.02,
                    transform=fig.transFigure,
                    color=mask_color,
                    zorder=100
                )
                fig.patches.append(rect)
            
            # Mask y-axis tick labels
            for label in ax.get_yticklabels():
                if label.get_text():
                    bbox = label.get_window_extent(renderer=renderer)
                    bbox_fig = bbox.transformed(fig.transFigure.inverted())
                    rect = plt.Rectangle(
                        (bbox_fig.x0 - 0.01, bbox_fig.y0 - 0.01),
                        bbox_fig.width + 0.02, bbox_fig.height + 0.02,
                        transform=fig.transFigure,
                        color=mask_color,
                        zorder=100
                    )
                    fig.patches.append(rect)
            
            # Mask y-axis line and ticks
            # Get the axis position (left or right)
            if change_y_axis_pos:
                # Y-axis is at the right
                x_axis_line = ax.transData.transform([(ax.get_xlim()[1], ax.get_ylim()[0]), 
                                                     (ax.get_xlim()[1], ax.get_ylim()[1])])
            else:
                # Y-axis is at the left
                x_axis_line = ax.transData.transform([(ax.get_xlim()[0], ax.get_ylim()[0]), 
                                                     (ax.get_xlim()[0], ax.get_ylim()[1])])
            
            x_axis_line_fig = fig.transFigure.inverted().transform(x_axis_line)
            
            # Create a rectangle to mask the axis line
            rect = plt.Rectangle(
                (x_axis_line_fig[0][0] - 0.01, x_axis_line_fig[0][1] - 0.01),
                0.02, x_axis_line_fig[1][1] - x_axis_line_fig[0][1] + 0.02,
                transform=fig.transFigure,
                color=mask_color,
                zorder=100
            )
            fig.patches.append(rect)
    
    # Save the image if a filename is provided
    if img_save_name:
        plt.savefig(img_save_name, dpi=300)
    
    return fig


class BarChartRunDraw(RunDraw):
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
            "draw__1_bar__func_1": {
                "original_img": draw__1_bar__func_1,
                "masked_img": draw__1_bar__func_1__mask,
            },
            # "draw__1_bar__func_2": draw__1_bar__func_2,
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
            label_angle: int,
            chart_direction: str,
            show_label: str,
            show_legend: str,
            x_axis_pos: str,
            y_axis_pos: str,
            chart_id: str,
            mask_id: str,
        ):
        # Subtask 0: Generate image with masked color (0_auto_maskcolor)
        if '0' in self.args.construction_subtask:
            self.draw_masked_chart_function(
                args=self.args, 
                bar_data=chart_entry["bar_data"], 
                bar_labels=chart_entry["bar_labels"], 
                bar_colors=chart_entry["bar_colors"],
                x_label=chart_entry["x_label"],
                y_label=chart_entry["y_label"],
                img_title=chart_entry["img_title"],
                label_angle=label_angle,
                horizontal=chart_direction=="horizontal",
                show_text_label=show_label=="labeled",
                show_legend=show_legend=="w_legend",
                change_x_axis_pos=x_axis_pos=="xtop",
                change_y_axis_pos=y_axis_pos=="yright",
                img_save_name=f"{self.root_path}/{mask_id}__gray_mask.png",
                mask_color=self.args.gray_mask,
                mask_idx=mask_idx_list,
            )
        
        # Subtask 2-3: Generate mask
        if ('2' in self.args.construction_subtask) or ('3' in self.args.construction_subtask):
            mask_generation(self.args, self.root_path, chart_id, f"{mask_id}")

    def run_draw_single_figure(self):
        """Bar chart generation"""
        # Single chart generation
        self._init_dir(self.root_path)
        self.total_img_num = 0
        self.total_vqa_num = 0
        chart_idx = 0  # track image num
        entry_idx = -1

        for func_id in METADATA_BAR.keys():
            self.draw_chart_function = self.function_dict[func_id]["original_img"]
            self.draw_masked_chart_function = self.function_dict[func_id]["masked_img"]

            for category_id in METADATA_BAR[func_id].keys():
                # List of entries
                chart_metadata = METADATA_BAR[func_id][category_id]

                for chart_entry in chart_metadata:
                    entry_idx += 1

                    for chart_direction in ["vertical", "horizontal"]:
                        for show_label in ["labeled"]:  # currently all labeled for strict eval, or set to ["labeled", "unlabeled"] when with LLM-as-a-judge
                            for x_axis_pos in ["xtop", "xbottom"]:
                                for y_axis_pos in ["yleft", "yright"]:
                                    for show_legend in ["w_legend"]:  # currently all with legend for strict eval, or set to ["w_legend", "wo_legend"] when with LLM-as-a-judge
                                        for label_angle in [30, 45, 60, 90]:
                                            chart_idx += 1
                                            chart_id = f"{self.args.chart_type}__img_{chart_idx}__category{category_id.split(' ')[0]}__angle{label_angle}__{chart_direction}__{show_label}__{show_legend}__{x_axis_pos}__{y_axis_pos}"
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
                                                    bar_data=chart_entry["bar_data"], 
                                                    bar_labels=chart_entry["bar_labels"], 
                                                    bar_colors=chart_entry["bar_colors"],
                                                    x_label=chart_entry["x_label"],
                                                    y_label=chart_entry["y_label"],
                                                    img_title=chart_entry["img_title"],
                                                    label_angle=label_angle,
                                                    horizontal=chart_direction=="horizontal",
                                                    show_text_label=show_label=="labeled",
                                                    show_legend=show_legend=="w_legend",
                                                    change_x_axis_pos=x_axis_pos=="xtop",
                                                    change_y_axis_pos=y_axis_pos=="yright",
                                                    img_save_name=f"{self.root_path}/{chart_id}.png",
                                                )

                                            # Init chart QA data generator
                                            self.vqa_generator = BarChartGenerator(self.args, chart_id)                                            

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
                                                        label_angle=label_angle,
                                                        chart_direction=chart_direction,
                                                        show_label=show_label,
                                                        show_legend=show_legend,
                                                        x_axis_pos=x_axis_pos,
                                                        y_axis_pos=y_axis_pos,
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


if __name__ == "__main__":
    # Create simple test args object
    class SimpleArgs:
        def __init__(self):
            self.global_figsize = (10, 6)
            self.gray_mask = '#CCCCCC'
    
    # Create test data
    test_args = SimpleArgs()
    
    # Test data - bar chart data
    bar_data = [25, 30, 15, 40, 35]
    bar_labels = ['Product A', 'Product B', 'Product C', 'Product D', 'Product E']
    bar_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
    
    print("Testing draw__1_bar__func_1 function...")
    
    # Test 1: Basic vertical bar chart
    print("Test 1: Basic vertical bar chart")
    fig1 = draw__1_bar__func_1(
        args=test_args,
        bar_data=bar_data,
        bar_labels=bar_labels,
        bar_colors=bar_colors,
        x_label="Products",
        y_label="Sales (in thousands)",
        img_title="Test Bar Chart - Vertical",
        label_angle=45,
        horizontal=False,
        show_text_label=True,
        show_legend=True,
        img_save_name="test_bar_vertical.png"
    )
    print("✓ Vertical bar chart saved as 'test_bar_vertical.png'")
    
    # Test 2: Horizontal bar chart
    print("Test 2: Horizontal bar chart")
    fig2 = draw__1_bar__func_1(
        args=test_args,
        bar_data=bar_data,
        bar_labels=bar_labels,
        bar_colors=bar_colors,
        x_label="Products",
        y_label="Sales (in thousands)",
        img_title="Test Bar Chart - Horizontal",
        label_angle=0,
        horizontal=True,
        show_text_label=True,
        show_legend=True,
        img_save_name="test_bar_horizontal.png"
    )
    print("✓ Horizontal bar chart saved as 'test_bar_horizontal.png'")
    
    # Test 3: Bar chart with axis position changes
    print("Test 3: Bar chart with axis position changes")
    fig3 = draw__1_bar__func_1(
        args=test_args,
        bar_data=bar_data,
        bar_labels=bar_labels,
        bar_colors=bar_colors,
        x_label="Products",
        y_label="Sales (in thousands)",
        img_title="Test Bar Chart - Axis Position Changed",
        label_angle=30,
        horizontal=False,
        show_text_label=True,
        show_legend=True,
        change_x_axis_pos=True,
        change_y_axis_pos=True,
        img_save_name="test_bar_axis_pos.png"
    )
    print("✓ Bar chart with changed axis positions saved as 'test_bar_axis_pos.png'")
    
    # Test 4: Masked bar chart
    print("Test 4: Masked bar chart")
    fig4 = draw__1_bar__func_1__mask(
        args=test_args,
        bar_data=bar_data,
        bar_labels=bar_labels,
        bar_colors=bar_colors,
        x_label="Products",
        y_label="Sales (in thousands)",
        img_title="Test Bar Chart - Masked",
        label_angle=45,
        horizontal=False,
        show_text_label=True,
        show_legend=True,
        mask_idx=[1, 3],  # Mask second and fourth bars
        img_save_name="test_bar_masked.png"
    )
    print("✓ Masked bar chart saved as 'test_bar_masked.png'")
    
    # Test 5: Axis masked bar chart
    print("Test 5: Axis masked bar chart")
    fig5 = draw__1_bar__func_1__axis_mask(
        args=test_args,
        bar_data=bar_data,
        bar_labels=bar_labels,
        bar_colors=bar_colors,
        x_label="Products",
        y_label="Sales (in thousands)",
        img_title="Test Bar Chart - Y-Axis Masked",
        label_angle=45,
        horizontal=False,
        show_text_label=True,
        show_legend=True,
        mask_axis='y',
        img_save_name="test_bar_axis_masked.png"
    )
    print("✓ Y-axis masked bar chart saved as 'test_bar_axis_masked.png'")
    
    # Show charts
    plt.show()
    
    print("\nAll tests completed!")
    print("Generated image files:")
    print("- test_bar_vertical.png")
    print("- test_bar_horizontal.png")
    print("- test_bar_axis_pos.png")
    print("- test_bar_masked.png")
    print("- test_bar_axis_masked.png")
