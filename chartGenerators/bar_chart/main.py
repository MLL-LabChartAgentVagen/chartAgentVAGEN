"""
Bar chart
"""

import os
import json
import copy
import random
import numpy as np
import pandas as pd
from typing import List, Dict, Optional
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


def _place_legend_outside(ax, bars, bar_labels, change_x_axis_pos, change_y_axis_pos, horizontal):
    """
    Place legend outside the plot area to prevent overlap with chart content.
    Uses dynamic spacing based on legend size.
    
    Args:
        ax: Matplotlib axes object
        bars: Bar chart objects
        bar_labels: Labels for the legend
        change_x_axis_pos: Whether x-axis is at top
        change_y_axis_pos: Whether y-axis is at right
        horizontal: Whether bars are horizontal
    
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
        bbox_to_anchor = (1.0, 0.5)  # At right edge of axes
        loc = 'center left'
        side = 'left'
    else:
        # Y-axis on left, place legend on right side of plot
        bbox_to_anchor = (1.0, 0.5)  # At right edge of axes
        loc = 'center left'
        side = 'right'
    
    # Create legend outside the plot area (in axes coordinates)
    legend = ax.legend(bars, bar_labels, loc=loc, bbox_to_anchor=bbox_to_anchor, 
                      frameon=True, fancybox=True, shadow=True)
    
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
    
    # Add legend outside plot area to prevent overlap
    if show_legend:
        _place_legend_outside(ax, bars, bar_labels, change_x_axis_pos, change_y_axis_pos, horizontal)
    else:
        # Adjust layout only if no legend
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
    
    # Add legend outside plot area to prevent overlap
    legend = None
    if show_legend:
        legend = _place_legend_outside(ax, bars, bar_labels, change_x_axis_pos, change_y_axis_pos, horizontal)
    else:
        # Adjust layout only if no legend
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


def draw__1_bar__func_1__bbox(
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
        bbox_color: str=None,
        bbox_idx: list=None,
    ):
    """
    Draw a bar chart with customizable axes, colors, and positioning, with bounding box highlighting capability.
    
    This function creates a bar chart and draws bounding boxes around relevant bars to highlight them.
    Unlike masking which hides information, bounding boxes highlight relevant information.
    
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
        bbox_color (str, optional): Color to use for bounding boxes. If None, uses red. Default is None.
        bbox_idx (list, optional): List of bar indices to highlight with bounding boxes. If None, no boxes are drawn. Default is None.
    
    Returns:
        matplotlib.figure.Figure: The figure object containing the bar chart with bounding boxes
        Dict: Dictionary containing bounding box coordinates for each highlighted bar
    """
    if bbox_color is None:
        bbox_color = '#FF0000'  # Red color for bounding boxes
    
    # Validate bbox_idx
    if bbox_idx is None:
        bbox_idx = []
    
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
    
    # Add legend outside plot area to prevent overlap
    legend = None
    if show_legend:
        legend = _place_legend_outside(ax, bars, bar_labels, change_x_axis_pos, change_y_axis_pos, horizontal)
    else:
        # Adjust layout only if no legend
        plt.tight_layout()
    
    # Dictionary to store bounding box coordinates
    bbox_coords = {}
    
    # Draw bounding boxes around relevant bars
    if bbox_idx:
        # Draw the canvas to get proper coordinates
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        
        for idx in bbox_idx:
            if 0 <= idx < len(bars):
                bar = bars[idx]
                
                # Get bar bounding box in data coordinates
                if horizontal:
                    # Horizontal bar: x from 0 to bar width, y from bar_y to bar_y + bar_height
                    bar_x0 = 0
                    bar_x1 = bar.get_width()
                    bar_y0 = bar.get_y()
                    bar_y1 = bar.get_y() + bar.get_height()
                else:
                    # Vertical bar: x from bar_x to bar_x + bar_width, y from 0 to bar_height
                    bar_x0 = bar.get_x()
                    bar_x1 = bar.get_x() + bar.get_width()
                    bar_y0 = 0
                    bar_y1 = bar.get_height()
                
                # Transform to figure coordinates for drawing
                bar_bbox_data = [(bar_x0, bar_y0), (bar_x1, bar_y1)]
                bar_bbox_fig = [ax.transData.transform(point) for point in bar_bbox_data]
                bar_bbox_fig = fig.transFigure.inverted().transform(bar_bbox_fig)
                
                # Calculate bounding box with padding
                padding = 0.01
                x0 = bar_bbox_fig[0][0] - padding
                y0 = bar_bbox_fig[0][1] - padding
                width = (bar_bbox_fig[1][0] - bar_bbox_fig[0][0]) + (2 * padding)
                height = (bar_bbox_fig[1][1] - bar_bbox_fig[0][1]) + (2 * padding)
                
                # Draw bounding box rectangle
                rect = plt.Rectangle(
                    (x0, y0),
                    width, height,
                    transform=fig.transFigure,
                    fill=False,
                    edgecolor=bbox_color,
                    linewidth=3,
                    linestyle='--',
                    zorder=100
                )
                fig.patches.append(rect)
                
                # Store bounding box coordinates in normalized figure coordinates [x0, y0, x1, y1]
                bbox_coords[idx] = {
                    'x0': float(x0),
                    'y0': float(y0),
                    'x1': float(x0 + width),
                    'y1': float(y0 + height),
                    'bar_index': idx,
                    'bar_label': bar_labels[idx] if idx < len(bar_labels) else None
                }
                
                # Also highlight text labels if present
                if show_text_label and idx < len(ax.texts):
                    text = ax.texts[idx]
                    text_bbox = text.get_window_extent(renderer=renderer)
                    text_bbox_fig = text_bbox.transformed(fig.transFigure.inverted())
                    
                    # Draw bounding box around text
                    text_rect = plt.Rectangle(
                        (text_bbox_fig.x0 - 0.005, text_bbox_fig.y0 - 0.005),
                        text_bbox_fig.width + 0.01, text_bbox_fig.height + 0.01,
                        transform=fig.transFigure,
                        fill=False,
                        edgecolor=bbox_color,
                        linewidth=2,
                        linestyle='--',
                        zorder=101
                    )
                    fig.patches.append(text_rect)
                    
                    # Store text bounding box
                    if idx not in bbox_coords:
                        bbox_coords[idx] = {}
                    bbox_coords[idx]['text_bbox'] = {
                        'x0': float(text_bbox_fig.x0 - 0.005),
                        'y0': float(text_bbox_fig.y0 - 0.005),
                        'x1': float(text_bbox_fig.x0 + text_bbox_fig.width + 0.005),
                        'y1': float(text_bbox_fig.y0 + text_bbox_fig.height + 0.005)
                    }
                
                # Also highlight category labels
                if horizontal:
                    labels = ax.get_yticklabels()
                else:
                    labels = ax.get_xticklabels()
                
                if idx < len(labels):
                    label = labels[idx]
                    label_bbox = label.get_window_extent(renderer=renderer)
                    label_bbox_fig = label_bbox.transformed(fig.transFigure.inverted())
                    
                    # Draw bounding box around label
                    padding_x = 0.01 if not horizontal else 0.005
                    padding_y = 0.01 if not horizontal else 0.005
                    
                    label_rect = plt.Rectangle(
                        (label_bbox_fig.x0 - padding_x, label_bbox_fig.y0 - padding_y),
                        label_bbox_fig.width + (padding_x * 2), label_bbox_fig.height + (padding_y * 2),
                        transform=fig.transFigure,
                        fill=False,
                        edgecolor=bbox_color,
                        linewidth=2,
                        linestyle='--',
                        zorder=101
                    )
                    fig.patches.append(label_rect)
                    
                    # Store label bounding box
                    if idx not in bbox_coords:
                        bbox_coords[idx] = {}
                    bbox_coords[idx]['label_bbox'] = {
                        'x0': float(label_bbox_fig.x0 - padding_x),
                        'y0': float(label_bbox_fig.y0 - padding_y),
                        'x1': float(label_bbox_fig.x0 + label_bbox_fig.width + padding_x),
                        'y1': float(label_bbox_fig.y0 + label_bbox_fig.height + padding_y)
                    }
    
    # Save the image if a filename is provided
    if img_save_name:
        plt.savefig(img_save_name, dpi=300)
    
    return fig, bbox_coords


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
    
    # Add legend outside plot area to prevent overlap
    legend = None
    if show_legend:
        legend = _place_legend_outside(ax, bars, bar_labels, change_x_axis_pos, change_y_axis_pos, horizontal)
    else:
        # Adjust layout only if no legend
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


def load_metadata(metadata_path: Optional[str] = None) -> Dict:
    """
    Load metadata from a custom JSON file or use default METADATA_BAR.
    
    Args:
        metadata_path: Optional path to a custom metadata JSON file.
                      If None, uses the default METADATA_BAR from metadata.metadata.
    
    Returns:
        Dictionary containing chart metadata in the same format as METADATA_BAR.
    
    Raises:
        FileNotFoundError: If metadata_path is provided but the file doesn't exist.
    """
    if metadata_path is None:
        return METADATA_BAR
    
    # Create parent directory if it doesn't exist
    metadata_dir = os.path.dirname(os.path.abspath(metadata_path))
    if metadata_dir and not os.path.exists(metadata_dir):
        os.makedirs(metadata_dir, exist_ok=True)
        logger.info(f"Created metadata directory: {metadata_dir}")
    
    if not os.path.exists(metadata_path):
        raise FileNotFoundError(
            f"Metadata file not found: {metadata_path}\n"
            f"Please create the metadata file or remove --metadata-path to use default metadata."
        )
    
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    logger.info(f"Loaded custom metadata from: {metadata_path}")
    return metadata


def collect_all_chart_entries(metadata: Dict) -> List[tuple]:
    """
    Collect all chart entries from metadata with their context.
    
    Args:
        metadata: Dictionary containing chart metadata.
    
    Returns:
        List of tuples: (func_id, category_id, chart_entry)
    """
    all_entries = []
    for func_id in metadata.keys():
        for category_id in metadata[func_id].keys():
            chart_metadata = metadata[func_id][category_id]
            for chart_entry in chart_metadata:
                all_entries.append((func_id, category_id, chart_entry))
    return all_entries


class BarChartRunDraw(RunDraw):
    def __init__(self, args):
        self.args = args
        self.function_dict = self._init_plot_functions()
        self.draw_chart_function = None
        self.total_img_num = 0
        
        # Create data path directory if it doesn't exist
        data_path = os.path.abspath(args.data_path)
        if not os.path.exists(data_path):
            os.makedirs(data_path, exist_ok=True)
            logger.info(f"Created data directory: {data_path}")
        
        self.root_path = f"{args.data_path}/imgs/{args.chart_type}/{args.chart_mode}"
        self.generated_vqa_data_save_path = f"{args.data_path}/{args.chart_type}__meta_qa_data.json"
        self.generated_vqa_data = {}
        self._init_generated_chart_qa_data()
        
        # Load metadata (custom or default)
        self.metadata = load_metadata(getattr(args, 'metadata_path', None))
        
        # Get configuration for random generation
        self.num_charts = getattr(args, 'num_charts', None)  # None means all charts
        self.num_questions_per_chart = getattr(args, 'num_questions_per_chart', 20)
        self.random_seed = getattr(args, 'random_seed', 42)
        self.composition_types = getattr(args, 'composition_types', None)

    def _init_plot_functions(self):
        function_dict = {
            "draw__1_bar__func_1": {
                "original_img": draw__1_bar__func_1,
                "masked_img": draw__1_bar__func_1__mask,
                "bbox_img": draw__1_bar__func_1__bbox,  # Added bounding box function
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
        save_dir = os.path.dirname(os.path.abspath(self.generated_vqa_data_save_path))
        if save_dir:  # Only create if there's a directory path
            os.makedirs(save_dir, exist_ok=True)
        
        # Write the JSON data to file with pretty formatting
        with open(self.generated_vqa_data_save_path, 'w', encoding='utf-8') as f:
            json.dump(self.generated_vqa_data, f, indent=4, ensure_ascii=False)
            
        logger.info(f"Chart QA data successfully saved to: {self.generated_vqa_data_save_path}")

    def _plot_bbox_chart(
            self,
            bbox_idx_list: List,
            chart_entry: Dict,
            label_angle: int,
            chart_direction: str,
            show_label: str,
            show_legend: str,
            x_axis_pos: str,
            y_axis_pos: str,
            chart_id: str,
            bbox_id: str,
        ):
        """Generate chart with bounding boxes highlighting relevant bars."""
        # Use bbox drawing function to highlight relevant bars
        if '0' in self.args.construction_subtask:
            bbox_color = getattr(self.args, 'bbox_color', '#FF0000')  # Default red
            self.draw_bbox_chart_function(
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
                img_save_name=f"{self.root_path}/{bbox_id}__bbox.png",
                bbox_color=bbox_color,
                bbox_idx=bbox_idx_list,
            )

    def run_draw_single_figure(self):
        """Bar chart generation with support for custom metadata, random selection, and configurable questions."""
        # Single chart generation
        self._init_dir(self.root_path)
        self.total_img_num = 0
        self.total_vqa_num = 0
        chart_idx = 0  # track image num
        
        # Collect all chart entries
        all_entries = collect_all_chart_entries(self.metadata)
        
        # If num_charts is specified, randomly sample that many entries
        if self.num_charts is not None and self.num_charts > 0:
            if self.num_charts > len(all_entries):
                logger.warning(f"Requested {self.num_charts} charts but only {len(all_entries)} available. Using all entries.")
                selected_entries = all_entries
            else:
                random.seed(self.random_seed)
                selected_entries = random.sample(all_entries, self.num_charts)
                logger.info(f"Randomly selected {len(selected_entries)} charts from {len(all_entries)} total entries (seed={self.random_seed})")
        else:
            selected_entries = all_entries
            logger.info(f"Processing all {len(selected_entries)} chart entries")

        for func_id, category_id, chart_entry in selected_entries:
            self.draw_chart_function = self.function_dict[func_id]["original_img"]
            self.draw_masked_chart_function = self.function_dict[func_id]["masked_img"]
            self.draw_bbox_chart_function = self.function_dict[func_id]["bbox_img"]  # Bounding box function

            # Generate only one configuration per chart entry (randomly selected)
            chart_idx += 1
            
            # Use a deterministic random selection based on chart_idx and random_seed
            entry_rng = random.Random(self.random_seed + chart_idx)
            
            # Randomly select one configuration from all possible combinations
            chart_direction = entry_rng.choice(["vertical", "horizontal"])
            show_label = entry_rng.choice(["labeled"])  # Can be extended to ["labeled", "unlabeled"] if needed
            x_axis_pos = entry_rng.choice(["xtop", "xbottom"])
            y_axis_pos = entry_rng.choice(["yleft", "yright"])
            show_legend = entry_rng.choice(["w_legend"])  # Can be extended to ["w_legend", "wo_legend"] if needed
            label_angle = entry_rng.choice([30, 45, 60, 90])
            
            chart_id = f"{self.args.chart_type}__img_{chart_idx}__category{category_id.split(' ')[0]}__angle{label_angle}__{chart_direction}__{show_label}__{show_legend}__{x_axis_pos}__{y_axis_pos}"
            chart_entry["chart_direction"] = chart_direction
            logger.info(
                f"{'=' * 100}"
                f"\n{' ' * 10} Image Index: {chart_idx}"
                f"\n{' ' * 10} Chart ID: {chart_id}"
                f"\n{' ' * 10} Configuration: {chart_direction}, angle={label_angle}, label={show_label}, legend={show_legend}, x={x_axis_pos}, y={y_axis_pos}"
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

            # Chart QA data generation & bbox chart
            # Use configurable number of questions per chart
            composition_types = getattr(self.args, 'composition_types', None)
            qa_data_condidates = self.vqa_generator.chart_qa_generator(
                chart_entry, 
                random_seed=self.random_seed + chart_idx,  # Different seed per chart
                num_questions=self.num_questions_per_chart,
                composition_types=composition_types
            )

            for new_qa_data in qa_data_condidates:
                new_qa_id = new_qa_data["qa_id"]

                if self._check_if_skip_existing_data(new_qa_id):
                    continue

                # Bbox paths - use args.data_path instead of hardcoded "./data"
                new_bbox_path = {}
                for step_key in new_qa_data["bbox"]:
                    new_bbox_path[step_key] = f"{self.args.data_path}/imgs/{self.args.chart_type}/{self.args.chart_mode}/{new_qa_id}__bbox_{step_key}.png"

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
                    "img_path": f"{self.args.data_path}/imgs/{self.args.chart_type}/{self.args.chart_mode}/{chart_id}.png",
                    "bbox_path": new_bbox_path,  # Changed from mask_path
                    "bbox_indices": new_qa_data["bbox"],  # Changed from mask_indices
                    "question": new_qa_data["question"],
                    "reasoning": new_qa_data["reasoning"],
                    "answer": new_qa_data["answer"],
                }

                # Generate bbox chart (highlighting relevant bars)
                for step_key in new_bbox_path:
                    curr_bbox_id = new_bbox_path[step_key].split("/")[-1].replace(".png", "").strip()
                    self._plot_bbox_chart(
                        bbox_idx_list=new_qa_data["bbox"][step_key],  # Indices to highlight
                        chart_entry=chart_entry,
                        label_angle=label_angle,
                        chart_direction=chart_direction,
                        show_label=show_label,
                        show_legend=show_legend,
                        x_axis_pos=x_axis_pos,
                        y_axis_pos=y_axis_pos,
                        chart_id=chart_id,
                        bbox_id=curr_bbox_id,
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
    import argparse
    
    def parse_figsize(figsize_str: str) -> tuple:
        """Parse figure size string 'width,height' into tuple."""
        try:
            parts = figsize_str.split(",")
            if len(parts) != 2:
                raise ValueError("Figure size must be in format 'width,height'")
            return (float(parts[0]), float(parts[1]))
        except (ValueError, IndexError) as e:
            raise argparse.ArgumentTypeError(f"Invalid figure size format: {e}. Expected format: 'width,height'")
    
    def parse_stages(stages_str: str) -> str:
        """Parse and validate construction stages string."""
        stages_str = stages_str.replace(",", "").replace(" ", "")
        valid_stages = set("01")
        stages_set = set(stages_str)
        
        if not stages_set.issubset(valid_stages):
            invalid = stages_set - valid_stages
            raise argparse.ArgumentTypeError(
                f"Invalid stages: {invalid}. Valid stages are: 0 (bbox images), 1 (original images)"
            )
        
        # Remove duplicates while preserving order
        seen = set()
        unique_stages = []
        for stage in stages_str:
            if stage not in seen:
                seen.add(stage)
                unique_stages.append(stage)
        
        return "".join(unique_stages)
    
    # Create argument parser
    parser = argparse.ArgumentParser(
        description="Bar Chart Generation with QA Data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings (all charts, 20 questions per chart)
  python chartGenerators/bar_chart/main.py
  
  # Generate only 5 random charts with 10 questions each
  python chartGenerators/bar_chart/main.py --num-charts 5 --num-questions 10
  
  # Use custom metadata file and output path
  python chartGenerators/bar_chart/main.py --metadata-path ./custom_metadata.json --data-path ./custom_output
  
  # Generate 10 charts with 15 questions each, using random seed 123
  python chartGenerators/bar_chart/main.py --num-charts 10 --num-questions 15 --random-seed 123
  
  # Only generate original images (no bbox images)
  python chartGenerators/bar_chart/main.py --stages 1
  
  # Generate with custom bbox color
  python chartGenerators/bar_chart/main.py --bbox-color "#00FF00" --num-charts 3
  
  # Generate only parallel composition questions
  python chartGenerators/bar_chart/main.py --num-charts 5 --composition-types parallel
  
  # Generate both one-step and nested compositions
  python chartGenerators/bar_chart/main.py --num-charts 5 --composition-types one_step nested
  
  # Full example with all options
  python chartGenerators/bar_chart/main.py \\
      --num-charts 5 \\
      --num-questions 12 \\
      --data-path ./my_output \\
      --metadata-path ./my_metadata.json \\
      --random-seed 42 \\
      --bbox-color "#FF0000" \\
      --stages 01 \\
      --figsize 12,8 \\
      --composition-types one_step parallel nested

Default Behavior:
  - Processes all charts from default metadata
  - Generates 20 questions per chart
  - Uses random seed 42
  - Outputs to ./data directory
  - Generates both original and bbox images (stages 01)
  - Generates all composition types with default weights (40% one_step, 40% parallel, 20% nested)
        """
    )
    
    # Chart generation options
    parser.add_argument(
        "--num-charts",
        type=int,
        default=None,
        help="Number of charts to randomly generate. If not specified, processes all charts. (default: None = all charts)"
    )
    
    parser.add_argument(
        "--num-questions",
        type=int,
        default=20,
        help="Number of questions to generate per chart (default: 20)"
    )
    
    parser.add_argument(
        "--random-seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)"
    )
    
    # File paths
    parser.add_argument(
        "--data-path",
        type=str,
        default="./data",
        help="Base path for saving generated data (default: ./data)"
    )
    
    parser.add_argument(
        "--metadata-path",
        type=str,
        default=None,
        help="Path to custom metadata JSON file. If not specified, uses default METADATA_BAR. (default: None)"
    )
    
    # Chart configuration
    parser.add_argument(
        "--chart-mode",
        type=str,
        default="single",
        help="Mode of chart generation (default: single)"
    )
    
    parser.add_argument(
        "--stages",
        type=parse_stages,
        default="01",
        help="Stages to run: '0'=bbox images, '1'=original images. Can be '0', '1', or '01'. (default: 01)"
    )
    
    parser.add_argument(
        "--figsize",
        type=parse_figsize,
        default="10,6",
        help="Figure size as 'width,height' (default: 10,6)"
    )
    
    parser.add_argument(
        "--gray-mask",
        type=str,
        default="#CCCCCC",
        help="Gray color code for masking (default: #CCCCCC)"
    )
    
    parser.add_argument(
        "--bbox-color",
        type=str,
        default="#FF0000",
        help="Color for bounding boxes (default: #FF0000 = red)"
    )
    
    parser.add_argument(
        "--composition-types",
        type=str,
        nargs="+",
        choices=["one_step", "parallel", "nested"],
        default=None,
        help="Composition types to generate. Options: 'one_step', 'parallel', 'nested'. "
             "Can specify multiple types (e.g., --composition-types one_step parallel). "
             "If not specified, generates all types with default weights. (default: None = all types)"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create configuration object
    class BarChartArgs:
        def __init__(self):
            self.chart_type = "bar"
            self.chart_mode = args.chart_mode
            self.data_path = args.data_path
            self.construction_subtask = args.stages
            self.global_figsize = args.figsize
            self.gray_mask = args.gray_mask
            self.bbox_color = args.bbox_color
            # Optional parameters
            self.metadata_path = args.metadata_path
            self.num_charts = args.num_charts
            self.num_questions_per_chart = args.num_questions
            self.random_seed = args.random_seed
            self.composition_types = args.composition_types
    
    # Create args object
    config = BarChartArgs()
    
    # Handle figsize - argparse doesn't call type function on defaults
    if isinstance(config.global_figsize, str):
        config.global_figsize = parse_figsize(config.global_figsize)
    
    # Log configuration
    logger.info("=" * 100)
    logger.info("Bar Chart Generation Configuration")
    logger.info("=" * 100)
    logger.info(f"Chart Type: {config.chart_type}")
    logger.info(f"Chart Mode: {config.chart_mode}")
    logger.info(f"Data Path: {config.data_path}")
    logger.info(f"Metadata Path: {config.metadata_path or 'Default (METADATA_BAR)'}")
    logger.info(f"Number of Charts: {config.num_charts or 'All charts'}")
    logger.info(f"Questions per Chart: {config.num_questions_per_chart}")
    logger.info(f"Random Seed: {config.random_seed}")
    logger.info(f"Stages: {config.construction_subtask}")
    logger.info(f"Figure Size: {config.global_figsize}")
    logger.info(f"Gray Mask: {config.gray_mask}")
    logger.info(f"Bbox Color: {config.bbox_color}")
    logger.info(f"Composition Types: {config.composition_types or 'All types (default weights)'}")
    logger.info("=" * 100)
    
    try:
        # Create and run chart generator
        generator = BarChartRunDraw(config)
        logger.info("Starting bar chart generation...")
        generator.run_draw_single_figure()
        
        logger.info("=" * 100)
        logger.info("Bar chart generation completed successfully!")
        logger.info("=" * 100)
        
    except FileNotFoundError as e:
        logger.error(f"{e}")
        logger.error("Please create the metadata file or remove --metadata-path to use default metadata.")
        sys.exit(1)
    except Exception as e:
        import traceback
        logger.error(f"Error during chart generation: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

