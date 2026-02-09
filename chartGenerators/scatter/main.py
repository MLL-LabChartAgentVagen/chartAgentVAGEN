"""
Scatter chart
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

from metadata.metadata import METADATA_SCATTER
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
    
    # Use uniform size for scatter points (sizes should represent tertiary dimension, not duplicate x/y data)
    # If scatter_sizes vary significantly and don't represent a meaningful third dimension, use uniform size
    uniform_size = 200  # Standard size for scatter points when no tertiary dimension
    
    # Create scatter plot based on orientation
    scatter_points = []
    if horizontal:
        # Swap x and y data for horizontal orientation
        for i in range(len(scatter_x_data)):
            scatter = ax.scatter(
                scatter_y_data[i],  # y_data becomes x-axis
                scatter_x_data[i],  # x_data becomes y-axis
                c=scatter_colors[i], 
                s=uniform_size,  # Use uniform size instead of scatter_sizes[i]
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
                s=uniform_size,  # Use uniform size instead of scatter_sizes[i]
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
    # By default, don't show legend if text labels are shown (labels provide the same information)
    # However, if show_legend=True is explicitly passed, respect that (user may want both)
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


def draw__3_scatter__func_1__bbox(
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
        bbox_color: str=None,
        bbox_idx: list=None,
        scatter_size_in_legend: int=100,
    ):
    """
    Draw a scatter plot with customizable colors, labels, and positioning, with bounding box highlighting capability.
    
    This function creates a scatter plot and draws bounding boxes around relevant scatter points to highlight them.
    Unlike masking which hides information, bounding boxes highlight relevant information.
    
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
        bbox_color (str, optional): Color to use for bounding boxes. If None, uses red. Default is None.
        bbox_idx (List[int], optional): List of scatter point indices to highlight with bounding boxes. If None, no boxes are drawn. Default is None.
        scatter_size_in_legend (int, optional): Size for markers in legend. Default is 100.
    
    Returns:
        matplotlib.figure.Figure: The figure object containing the scatter plot with bounding boxes
    """
    if bbox_color is None:
        bbox_color = '#FF0000'  # Red color for bounding boxes
    
    # Validate bbox_idx
    if bbox_idx is None:
        bbox_idx = []
    
    # Create figure
    fig, ax = plt.subplots(figsize=args.global_figsize)
    
    # Use uniform size for scatter points (sizes should represent tertiary dimension, not duplicate x/y data)
    # If scatter_sizes vary significantly and don't represent a meaningful third dimension, use uniform size
    uniform_size = 200  # Standard size for scatter points when no tertiary dimension
    
    # Create scatter plot based on orientation
    scatter_points = []
    if horizontal:
        # Swap x and y data for horizontal orientation
        for i in range(len(scatter_x_data)):
            scatter = ax.scatter(
                scatter_y_data[i],  # y_data becomes x-axis
                scatter_x_data[i],  # x_data becomes y-axis
                c=scatter_colors[i], 
                s=uniform_size,  # Use uniform size instead of scatter_sizes[i]
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
                s=uniform_size,  # Use uniform size instead of scatter_sizes[i]
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
    # By default, don't show legend if text labels are shown (labels provide the same information)
    # However, if show_legend=True is explicitly passed, respect that (user may want both)
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
    
    # Draw bounding boxes around relevant scatter points
    if bbox_idx:
        # Draw the canvas to get proper coordinates
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        
        for idx in bbox_idx:
            if 0 <= idx < len(scatter_points):
                # Get the scatter point's position
                if horizontal:
                    x_pos = scatter_y_data[idx]
                    y_pos = scatter_x_data[idx]
                else:
                    x_pos = scatter_x_data[idx]
                    y_pos = scatter_y_data[idx]
                
                # Scatter size is in points^2 (uniform_size = 200)
                # Calculate the radius in points
                uniform_size = 200
                radius_points = np.sqrt(uniform_size / np.pi)  # Radius in points ≈ 7.98 points
                
                # Convert radius from points to display pixels
                # 1 point = 1/72 inch, and pixels = inches * dpi
                radius_pixels = radius_points * (fig.dpi / 72.0)
                
                # Get the point position in display coordinates (pixels)
                point_display = ax.transData.transform((x_pos, y_pos))
                
                # Get the axes bbox in display coordinates (pixels)
                ax_bbox_display = ax.get_window_extent(renderer=renderer)
                ax_bbox_fig = ax.get_position()  # Axes bbox in figure coordinates (0-1)
                
                # Convert point from display to figure coordinates
                point_fig = fig.transFigure.inverted().transform(point_display)
                
                # Convert radius from pixels to figure coordinates
                # To ensure a perfect square, use the average of axes dimensions
                # This ensures consistent scaling in both directions
                ax_width_pixels = ax_bbox_display.width
                ax_height_pixels = ax_bbox_display.height
                avg_axes_pixels = (ax_width_pixels + ax_height_pixels) / 2.0
                avg_axes_fig = (ax_bbox_fig.width + ax_bbox_fig.height) / 2.0
                
                # Calculate radius in figure coordinates using average dimensions
                # This ensures the box appears square on screen
                radius_fig = (radius_pixels / avg_axes_pixels) * avg_axes_fig
                
                # Add padding after scaling to figure coordinates (10% extra)
                # This ensures padding is consistent regardless of axes aspect ratio
                padding_factor = 1.1
                radius_fig_with_padding = radius_fig * padding_factor
                
                # Draw square bounding box rectangle in figure coordinates
                # This ensures it appears square on screen regardless of axis aspect ratio
                rect = plt.Rectangle(
                    (point_fig[0] - radius_fig_with_padding, point_fig[1] - radius_fig_with_padding),
                    2 * radius_fig_with_padding, 2 * radius_fig_with_padding,
                    transform=fig.transFigure,
                    fill=False,
                    edgecolor=bbox_color,
                    linewidth=2,
                    linestyle='-',
                    zorder=100
                )
                fig.patches.append(rect)
        
        # Draw bounding boxes around text labels if shown
        if show_text_label:
            for idx in bbox_idx:
                if 0 <= idx < len(scatter_labels):
                    # Find the annotation text
                    for text in ax.texts:
                        if text.get_text() == scatter_labels[idx]:
                            bbox = text.get_window_extent(renderer=renderer)
                            bbox_fig = bbox.transformed(fig.transFigure.inverted())
                            
                            rect = plt.Rectangle(
                                (bbox_fig.x0 - 0.005, bbox_fig.y0 - 0.005),
                                bbox_fig.width + 0.01, bbox_fig.height + 0.01,
                                transform=fig.transFigure,
                                fill=False,
                                edgecolor=bbox_color,
                                linewidth=2,
                                linestyle='-',
                                zorder=101
                            )
                            fig.patches.append(rect)
        
        # Draw bounding boxes around legend entries if present
        if show_legend and legend:
            legend_texts = legend.get_texts()
            legend_handles = legend.legend_handles
            
            for idx in bbox_idx:
                if 0 <= idx < len(legend_texts):
                    # Bounding box for legend text
                    text = legend_texts[idx]
                    bbox = text.get_window_extent(renderer=renderer)
                    bbox_fig = bbox.transformed(fig.transFigure.inverted())
                    
                    rect = plt.Rectangle(
                        (bbox_fig.x0 - 0.005, bbox_fig.y0 - 0.005),
                        bbox_fig.width + 0.01, bbox_fig.height + 0.01,
                        transform=fig.transFigure,
                        fill=False,
                        edgecolor=bbox_color,
                        linewidth=2,
                        linestyle='-',
                        zorder=101
                    )
                    fig.patches.append(rect)
                    
                    # Bounding box for legend handle (the colored marker)
                    if 0 <= idx < len(legend_handles):
                        handle = legend_handles[idx]
                        bbox = handle.get_window_extent(renderer=renderer)
                        bbox_fig = bbox.transformed(fig.transFigure.inverted())
                        
                        rect = plt.Rectangle(
                            (bbox_fig.x0 - 0.005, bbox_fig.y0 - 0.005),
                            bbox_fig.width + 0.01, bbox_fig.height + 0.01,
                            transform=fig.transFigure,
                            fill=False,
                            edgecolor=bbox_color,
                            linewidth=2,
                            linestyle='-',
                            zorder=101
                        )
                        fig.patches.append(rect)
    
    # Save the image if a filename is provided
    if img_save_name:
        plt.savefig(img_save_name, dpi=300)
    
    return fig


def load_metadata(metadata_path: Optional[str] = None) -> Dict:
    """
    Load metadata from a custom JSON file or use default METADATA_SCATTER.
    
    Supports two JSON formats:
    1. Standard format: {func_id: {category_id: [chart_entry, ...]}}
    2. Generated format: [{category_id, category_name, chart_entries: {bar, pie, scatter}}, ...]
    
    Args:
        metadata_path: Optional path to a custom metadata JSON file.
                      If None, uses the default METADATA_SCATTER from metadata.metadata.
    
    Returns:
        Dictionary containing chart metadata in the same format as METADATA_SCATTER.
    
    Raises:
        FileNotFoundError: If metadata_path is provided but the file doesn't exist.
    """
    if metadata_path is None:
        return METADATA_SCATTER
    
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
        raw_data = json.load(f)
    
    # Check if it's the generated format (array of category objects)
    if isinstance(raw_data, list) and len(raw_data) > 0 and isinstance(raw_data[0], dict) and 'chart_entries' in raw_data[0]:
        # Transform from generated format to expected format
        logger.info(f"Detected generated metadata format, transforming to standard format...")
        metadata = _transform_generated_metadata(raw_data, chart_type='scatter')
        logger.info(f"Transformed {len(raw_data)} categories from generated format")
    else:
        # Assume it's already in the standard format
        metadata = raw_data
    
    logger.info(f"Loaded custom metadata from: {metadata_path}")
    return metadata


def _transform_generated_metadata(generated_data: List[Dict], chart_type: str = 'scatter') -> Dict:
    """
    Transform generated metadata format to standard metadata format.
    
    Generated format: [{category_id, category_name, chart_entries: {bar, pie, scatter}}, ...]
    Standard format: {func_id: {category_name: [chart_entry, ...]}}
    
    Args:
        generated_data: List of category objects with chart_entries
        chart_type: Type of chart to extract ('bar', 'pie', 'scatter')
    
    Returns:
        Dictionary in standard metadata format
    """
    # Map chart types to function IDs
    func_id_map = {
        'bar': 'draw__1_bar__func_1',
        'pie': 'draw__8_pie__func_1',
        'scatter': 'draw__3_scatter__func_1'
    }
    
    func_id = func_id_map.get(chart_type, f'draw__1_{chart_type}__func_1')
    result = {func_id: {}}
    
    for category_obj in generated_data:
        category_name = category_obj.get('category_name', f"{category_obj.get('category_id', 'Unknown')} - Unknown")
        chart_entries = category_obj.get('chart_entries', {})
        
        # Extract the chart type entry
        chart_entry = chart_entries.get(chart_type)
        if chart_entry:
            # Initialize category if it doesn't exist
            if category_name not in result[func_id]:
                result[func_id][category_name] = []
            
            # Add the chart entry
            result[func_id][category_name].append(chart_entry)
    
    return result


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


class ScatterChartRunDraw(RunDraw):
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
            "draw__3_scatter__func_1": {
                "original_img": draw__3_scatter__func_1,
                "bbox_img": draw__3_scatter__func_1__bbox,
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
            horizontal: str,
            show_text_label: str,
            show_legend: str,
            change_x_axis_pos: str,
            change_y_axis_pos: str,
            chart_id: str,
            bbox_id: str,
        ):
        """Generate scatter plot chart with bounding boxes highlighting relevant scatter points."""
        # Use bbox drawing function to highlight relevant scatter points
        if '0' in self.args.construction_subtask:
            bbox_color = getattr(self.args, 'bbox_color', '#FF0000')  # Default red
            
            # Determine legend display based on labels and user options (same logic as main chart)
            force_show_legend = getattr(self.args, 'show_legend', None)
            force_no_legend = getattr(self.args, 'no_legend', None)
            
            # Determine if legend should be shown (as boolean for drawing function)
            if force_no_legend:
                show_legend_bool = False
            elif force_show_legend:
                # User explicitly wants legend, even if labels are shown
                show_legend_bool = True
            elif show_text_label == "labeled":
                # Default: No legend when labels are shown (redundant information)
                show_legend_bool = False
            else:
                # No labels shown, use the show_legend string value
                show_legend_bool = show_legend == "w_legend"
            
            # Draw scatter plot with bounding boxes
            self.draw_bbox_chart_function(
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
                show_legend=show_legend_bool,
                change_x_axis_pos=change_x_axis_pos=="xtop",
                change_y_axis_pos=change_y_axis_pos=="yright",
                img_save_name=f"{self.root_path}/{bbox_id}__bbox.png",
                bbox_color=bbox_color,
                bbox_idx=bbox_idx_list,
            )

    def run_draw_single_figure(self):
        """Scatter chart generation with support for custom metadata, random selection, and configurable questions."""
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
            self.draw_bbox_chart_function = self.function_dict[func_id]["bbox_img"]

            # Generate only one configuration per chart entry (randomly selected)
            chart_idx += 1
            
            # Use a deterministic random selection based on chart_idx and random_seed
            entry_rng = random.Random(self.random_seed + chart_idx)
            
            # Randomly select one configuration from all possible combinations
            chart_direction = entry_rng.choice(["vertical", "horizontal"])
            show_label = entry_rng.choice(["labeled"])  # Can be extended to ["labeled", "unlabeled"] if needed
            x_axis_pos = entry_rng.choice(["xtop", "xbottom"])
            y_axis_pos = entry_rng.choice(["yleft", "yright"])
            
            # Determine legend display based on labels and user options
            # By default: if labels are shown, don't show legend (redundant information)
            force_show_legend = getattr(self.args, 'show_legend', None)
            force_no_legend = getattr(self.args, 'no_legend', None)
            
            # Determine if legend should be shown (as boolean for drawing function)
            if force_no_legend:
                show_legend_bool = False
                show_legend = "wo_legend"
            elif force_show_legend:
                # User explicitly wants legend, even if labels are shown
                show_legend_bool = True
                show_legend = "w_legend"
            elif show_label == "labeled":
                # Default: No legend when labels are shown (redundant information)
                show_legend_bool = False
                show_legend = "wo_legend"
            else:
                # No labels shown, randomly choose whether to show legend
                show_legend = entry_rng.choice(["w_legend", "wo_legend"])
                show_legend_bool = show_legend == "w_legend"

            chart_id = f"{self.args.chart_type}__img_{chart_idx}__category{category_id.split(' ')[0]}__{chart_direction}__{show_label}__{show_legend}__{x_axis_pos}__{y_axis_pos}"
            chart_entry["chart_direction"] = chart_direction
            logger.info(
                f"{'=' * 100}"
                f"\n{' ' * 10} Image Index: {chart_idx}"
                f"\n{' ' * 10} Chart ID: {chart_id}"
                f"\n{' ' * 10} Configuration: {chart_direction}, label={show_label}, legend={show_legend}, x={x_axis_pos}, y={y_axis_pos}"
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
                    show_legend=show_legend_bool,
                    change_x_axis_pos=x_axis_pos=="xtop",
                    change_y_axis_pos=y_axis_pos=="yright",
                    img_save_name=f"{self.root_path}/{chart_id}.png",
                )

            # Init chart QA data generator
            self.vqa_generator = ScatterChartGenerator(self.args, chart_id)                                            

            # Chart QA data generation & bbox chart
            # Use configurable number of questions per chart
            # Note: chart_index is set to 0 since we're using random selection and don't have the original index
            qa_data_condidates = self.vqa_generator.chart_qa_generator(
                chart_metadata=chart_entry,
                func_id=func_id,
                category=category_id,
                chart_index=0,  # Use 0 as default since we're using random selection
                use_hardcoded=True,  # Enable hardcoded questions
                use_random=True,     # Enable random questions
                random_seed=self.random_seed + chart_idx,  # Different seed per chart
                num_questions=self.num_questions_per_chart
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
                
                # Generate bbox chart (highlighting relevant scatter points)
                for step_key in new_bbox_path:
                    curr_bbox_id = new_bbox_path[step_key].split("/")[-1].replace(".png", "").strip()
                    self._plot_bbox_chart(
                        bbox_idx_list=new_qa_data["bbox"][step_key],  # Indices to highlight
                        chart_entry=chart_entry,
                        horizontal=chart_direction,
                        show_text_label=show_label,
                        show_legend=show_legend,
                        change_x_axis_pos=x_axis_pos,
                        change_y_axis_pos=y_axis_pos,
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
        description="Scatter Chart Generation with QA Data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings (all charts, 20 questions per chart)
  python chartGenerators/scatter/main.py
  
  # Generate only 5 random charts with 10 questions each
  python chartGenerators/scatter/main.py --num-charts 5 --num-questions 10
  
  # Use custom metadata file and output path
  python chartGenerators/scatter/main.py --metadata-path ./custom_metadata.json --data-path ./custom_output
  
  # Generate 10 charts with 15 questions each, using random seed 123
  python chartGenerators/scatter/main.py --num-charts 10 --num-questions 15 --random-seed 123
  
  # Only generate original images (no bbox images)
  python chartGenerators/scatter/main.py --stages 1
  
  # Generate with custom bbox color
  python chartGenerators/scatter/main.py --bbox-color "#00FF00" --num-charts 3
  
  # Full example with all options
  python chartGenerators/scatter/main.py \\
      --num-charts 5 \\
      --num-questions 12 \\
      --data-path ./my_output \\
      --metadata-path ./my_metadata.json \\
      --random-seed 42 \\
      --bbox-color "#FF0000" \\
      --stages 01 \\
      --figsize 12,8

Default Behavior:
  - Processes all charts from default metadata
  - Generates 20 questions per chart
  - Uses random seed 42
  - Outputs to ./data directory
  - Generates both original and bbox images (stages 01)
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
        help="Path to custom metadata JSON file. If not specified, uses default METADATA_SCATTER. (default: None)"
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
        "--show-legend",
        action="store_true",
        default=None,
        help="Force show legend even when labels are present. By default, legend is hidden when labels are shown."
    )
    
    parser.add_argument(
        "--no-legend",
        action="store_true",
        default=None,
        help="Force hide legend. By default, legend is hidden when labels are shown."
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create configuration object
    class ScatterChartArgs:
        def __init__(self):
            self.chart_type = "scatter"
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
            self.composition_types = None  # Scatter doesn't use composition_types yet
            self.show_legend = args.show_legend
            self.no_legend = args.no_legend
    
    # Create args object
    config = ScatterChartArgs()
    
    # Handle figsize - argparse doesn't call type function on defaults
    if isinstance(config.global_figsize, str):
        config.global_figsize = parse_figsize(config.global_figsize)
    
    # Log configuration
    logger.info("=" * 100)
    logger.info("Scatter Chart Generation Configuration")
    logger.info("=" * 100)
    logger.info(f"Chart Type: {config.chart_type}")
    logger.info(f"Chart Mode: {config.chart_mode}")
    logger.info(f"Data Path: {config.data_path}")
    logger.info(f"Metadata Path: {config.metadata_path or 'Default (METADATA_SCATTER)'}")
    logger.info(f"Number of Charts: {config.num_charts or 'All charts'}")
    logger.info(f"Questions per Chart: {config.num_questions_per_chart}")
    logger.info(f"Random Seed: {config.random_seed}")
    logger.info(f"Stages: {config.construction_subtask}")
    logger.info(f"Figure Size: {config.global_figsize}")
    logger.info(f"Gray Mask: {config.gray_mask}")
    logger.info(f"Bbox Color: {config.bbox_color}")
    logger.info("=" * 100)
    
    try:
        # Create and run chart generator
        generator = ScatterChartRunDraw(config)
        logger.info("Starting scatter chart generation...")
        generator.run_draw_single_figure()
        
        logger.info("=" * 100)
        logger.info("Scatter chart generation completed successfully!")
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
