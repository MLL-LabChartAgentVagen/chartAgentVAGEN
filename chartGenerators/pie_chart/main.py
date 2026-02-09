"""
Pie chart
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
from matplotlib.patches import Arc

from abc import ABC, abstractmethod
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
from templates.run_draw import RunDraw

from metadata.metadata import METADATA_PIE
from chartGenerators.pie_chart.pie_chart_generator import PieChartGenerator
from utils.logger import logger
from utils.json_util import read_from_json


def _pie_layout_params(num_slices: int, show_autopct: bool) -> dict:
    """
    Return radius, pctdistance, labeldistance (and autopct font size) to reduce label overlap.
    Smaller pie + larger distances when many slices so labels and autopct text don't overlap.
    Also returns top margin and title_pad so the title does not overlap external labels.
    """
    if num_slices >= 9:
        radius = 0.6
        pctdistance = 0.85
        labeldistance = 1.35
        autopct_fontsize = 8
        top = 0.80
        title_pad = 32
    elif num_slices >= 7:
        radius = 0.7
        pctdistance = 0.78
        labeldistance = 1.25
        autopct_fontsize = 9
        top = 0.84
        title_pad = 28
    elif num_slices >= 5:
        radius = 0.85
        pctdistance = 0.7
        labeldistance = 1.15
        autopct_fontsize = 10
        top = 0.88
        title_pad = 24
    else:
        radius = 1.0
        pctdistance = 0.6
        labeldistance = 1.1
        autopct_fontsize = 12
        top = 0.92
        title_pad = 20
    return {
        'radius': radius,
        'pctdistance': pctdistance if show_autopct else 0.6,
        'labeldistance': labeldistance,
        'autopct_fontsize': autopct_fontsize,
        'top': top,
        'title_pad': title_pad,
    }


def _place_pie_legend_outside(ax, wedges, pie_labels):
    """
    Place legend outside the plot area to prevent overlap with pie chart labels.
    Dynamically positions the legend based on label positions.
    
    Args:
        ax: Matplotlib axes object
        wedges: Pie chart wedge objects
        pie_labels: Labels for the legend
    
    Returns:
        Legend object
    """
    fig = ax.figure
    
    # First, do a tight layout to fit the plot content
    plt.tight_layout()
    
    # Draw the canvas to get accurate measurements
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    
    # Get the bounding boxes of all pie chart labels (texts outside the pie)
    # These are the labels returned from ax.pie() - they're in ax.texts
    label_bboxes = []
    for text in ax.texts:
        text_str = text.get_text()
        # Only consider non-empty labels that are outside the pie (not autopct)
        # Autopct texts are usually shorter and inside slices
        if text_str and len(text_str) > 0:
            bbox = text.get_window_extent(renderer=renderer)
            # Convert to figure coordinates for easier comparison
            bbox_fig = bbox.transformed(fig.transFigure.inverted())
            label_bboxes.append(bbox_fig)
    
    # Get axes position in figure coordinates
    ax_bbox = ax.get_position()
    
    # Try different legend positions and find one that doesn't overlap
    # Priority: right side, then left side, then bottom
    legend_positions = [
        ((1.05, 0.5), 'center left'),      # Right side
        ((-0.05, 0.5), 'center right'),    # Left side
        ((0.5, -0.1), 'upper center'),     # Bottom center
        ((1.05, 0.3), 'upper left'),       # Right side, lower
        ((1.05, 0.7), 'lower left'),       # Right side, upper
    ]
    
    best_legend = None
    best_overlap = float('inf')
    best_bbox_anchor = None
    best_loc = None
    
    for bbox_anchor, loc in legend_positions:
        # Create a temporary legend to measure its size
        temp_legend = ax.legend(wedges, pie_labels, title="Categories", 
                                loc=loc, bbox_to_anchor=bbox_anchor, 
                                frameon=True)
        temp_bbox = temp_legend.get_window_extent(renderer=renderer)
        temp_bbox_fig = temp_bbox.transformed(fig.transFigure.inverted())
        temp_legend.remove()
        
        # Check for overlap with labels
        overlap_count = 0
        for label_bbox in label_bboxes:
            # Check if legend bbox intersects with label bbox
            if (temp_bbox_fig.x0 < label_bbox.x1 and temp_bbox_fig.x1 > label_bbox.x0 and
                temp_bbox_fig.y0 < label_bbox.y1 and temp_bbox_fig.y1 > label_bbox.y0):
                overlap_count += 1
        
        if overlap_count == 0:
            # No overlap, use this position
            legend = ax.legend(wedges, pie_labels, title="Categories", 
                             loc=loc, bbox_to_anchor=bbox_anchor, 
                             frameon=True, fancybox=True, shadow=True)
            
            # Adjust axes position to make room for legend
            if bbox_anchor[0] > 1.0:  # Legend on right
                new_right = min(0.95, ax_bbox.x1 - 0.1)
                ax.set_position([ax_bbox.x0, ax_bbox.y0, new_right - ax_bbox.x0, ax_bbox.height])
            elif bbox_anchor[0] < 0:  # Legend on left
                new_left = max(0.05, ax_bbox.x0 + 0.1)
                ax.set_position([new_left, ax_bbox.y0, ax_bbox.x1 - new_left, ax_bbox.height])
            elif bbox_anchor[1] < 0:  # Legend on bottom
                new_bottom = max(0.05, ax_bbox.y0 + 0.1)
                ax.set_position([ax_bbox.x0, new_bottom, ax_bbox.width, ax_bbox.y1 - new_bottom])
            
            return legend
        
        if overlap_count < best_overlap:
            best_overlap = overlap_count
            best_bbox_anchor = bbox_anchor
            best_loc = loc
    
    # If all positions have some overlap, use the one with least overlap
    # and adjust axes to minimize it
    if best_bbox_anchor is not None:
        legend = ax.legend(wedges, pie_labels, title="Categories", 
                          loc=best_loc, bbox_to_anchor=best_bbox_anchor, 
                          frameon=True, fancybox=True, shadow=True)
        
        # Adjust axes to make more room
        if best_bbox_anchor[0] > 1.0:  # Legend on right
            new_right = min(0.90, ax_bbox.x1 - 0.15)
            ax.set_position([ax_bbox.x0, ax_bbox.y0, new_right - ax_bbox.x0, ax_bbox.height])
        elif best_bbox_anchor[0] < 0:  # Legend on left
            new_left = max(0.10, ax_bbox.x0 + 0.15)
            ax.set_position([new_left, ax_bbox.y0, ax_bbox.x1 - new_left, ax_bbox.height])
        elif best_bbox_anchor[1] < 0:  # Legend on bottom
            new_bottom = max(0.10, ax_bbox.y0 + 0.15)
            ax.set_position([ax_bbox.x0, new_bottom, ax_bbox.width, ax_bbox.y1 - new_bottom])
    else:
        # Fallback to default position
        legend = ax.legend(wedges, pie_labels, title="Categories", 
                          loc="center left", bbox_to_anchor=(1.05, 0.5), 
                          frameon=True, fancybox=True, shadow=True)
    
    return legend


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
    
    # Layout params to reduce label overlap (smaller pie, larger distances when many slices)
    layout = _pie_layout_params(len(pie_data), show_autopct=(autopct is not None))
    
    # Create the pie chart
    wedges, texts, autotexts = ax.pie(
        pie_data,
        labels=pie_labels,
        colors=pie_colors,
        autopct=autopct,
        startangle=startangle,
        explode=explode_slices,
        radius=layout['radius'],
        pctdistance=layout['pctdistance'],
        labeldistance=layout['labeldistance'],
        textprops={'fontsize': min(12, layout['autopct_fontsize'] + 2)}
    )
    for t in autotexts:
        t.set_fontsize(layout['autopct_fontsize'])
    
    ax.set_title(img_title, fontsize=16, pad=layout['title_pad'])
    
    # Ensure the pie chart is circular
    ax.axis('equal')
    
    # Add legend (positioned to avoid label overlap)
    if show_legend:
        _place_pie_legend_outside(ax, wedges, pie_labels)
    
    # Adjust layout to make sure everything fits
    plt.tight_layout()
    # Reserve top margin after tight_layout so title never overlaps external labels
    fig.subplots_adjust(top=layout['top'])
    
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
    
    # Layout params to reduce label overlap
    layout = _pie_layout_params(len(pie_data), show_autopct=(autopct is not None))
    
    # Create the pie chart with original colors (we'll mask with rectangles later)
    wedges, texts, autotexts = ax.pie(
        pie_data,
        labels=pie_labels,
        colors=pie_colors,
        autopct=autopct,
        startangle=startangle,
        explode=explode_slices,
        radius=layout['radius'],
        pctdistance=layout['pctdistance'],
        labeldistance=layout['labeldistance'],
        textprops={'fontsize': min(12, layout['autopct_fontsize'] + 2)}
    )
    for t in autotexts:
        t.set_fontsize(layout['autopct_fontsize'])
    
    ax.set_title(img_title, fontsize=16, pad=layout['title_pad'])
    
    # Ensure the pie chart is circular
    ax.axis('equal')
    
    # Add legend (positioned to avoid label overlap)
    legend = None
    if show_legend:
        legend = _place_pie_legend_outside(ax, wedges, pie_labels)
    
    # Adjust layout to make sure everything fits
    plt.tight_layout()
    # Reserve top margin after tight_layout so title never overlaps external labels
    fig.subplots_adjust(top=layout['top'])
    
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


def draw__8_pie__func_1__bbox(
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
        bbox_color: str = None,
        bbox_idx: List[int] = None,
    ):
    """
    Draw a pie chart with customizable colors, labels, and positioning, with bounding box highlighting capability.
    
    This function creates a pie chart and draws bounding boxes around relevant slices to highlight them.
    Unlike masking which hides information, bounding boxes highlight relevant information.
    
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
        bbox_color (str, optional): Color to use for bounding boxes. If None, uses red. Default is None.
        bbox_idx (list, optional): List of slice indices to highlight with bounding boxes. If None, no boxes are drawn. Default is None.
    
    Returns:
        matplotlib.figure.Figure: The figure object containing the pie chart with bounding boxes
        Dict: Dictionary containing bounding box coordinates for each highlighted slice
    """
    if bbox_color is None:
        bbox_color = '#FF0000'  # Red color for bounding boxes
    
    # Validate bbox_idx
    if bbox_idx is None:
        bbox_idx = []
    
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
    
    # Layout params to reduce label overlap
    layout = _pie_layout_params(len(pie_data), show_autopct=(autopct is not None))
    
    # Create the pie chart
    wedges, texts, autotexts = ax.pie(
        pie_data,
        labels=pie_labels,
        colors=pie_colors,
        autopct=autopct,
        startangle=startangle,
        explode=explode_slices,
        radius=layout['radius'],
        pctdistance=layout['pctdistance'],
        labeldistance=layout['labeldistance'],
        textprops={'fontsize': min(12, layout['autopct_fontsize'] + 2)}
    )
    for t in autotexts:
        t.set_fontsize(layout['autopct_fontsize'])
    
    ax.set_title(img_title, fontsize=16, pad=layout['title_pad'])
    
    # Ensure the pie chart is circular
    ax.axis('equal')
    
    # Add legend (positioned to avoid label overlap)
    legend = None
    if show_legend:
        legend = _place_pie_legend_outside(ax, wedges, pie_labels)
    
    # Adjust layout to make sure everything fits
    plt.tight_layout()
    # Reserve top margin after tight_layout so title never overlaps external labels
    fig.subplots_adjust(top=layout['top'])
    
    # Dictionary to store bounding box coordinates
    bbox_coords = {}
    
    # Draw bounding boxes around relevant slices
    if bbox_idx:
        # Draw the canvas to get proper coordinates
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        
        for idx in bbox_idx:
            if 0 <= idx < len(wedges):
                wedge = wedges[idx]
                
                # Extract wedge properties for polar coordinates
                # Get the wedge's center, radius, and angles
                center = wedge.center
                radius = wedge.r
                theta1 = wedge.theta1
                theta2 = wedge.theta2
                
                # Draw wedge-shaped bounding box outline
                # Use a slightly larger radius for the outline to make it visible
                outline_radius = radius * 1.02  # 2% larger
                
                # Convert angles from degrees to radians for calculations
                theta1_rad = np.deg2rad(theta1)
                theta2_rad = np.deg2rad(theta2)
                
                # Draw the curved arc portion of the wedge outline
                arc = Arc(
                    xy=center,
                    width=outline_radius * 2,
                    height=outline_radius * 2,
                    angle=0,  # Rotation angle (0 for standard pie chart)
                    theta1=theta1,
                    theta2=theta2,
                    color=bbox_color,
                    linewidth=2.5,
                    zorder=10
                )
                ax.add_patch(arc)
                
                # Draw the two radial edges (straight lines from center to arc)
                # Calculate points on the arc at the outline radius
                x1 = center[0] + outline_radius * np.cos(theta1_rad)
                y1 = center[1] + outline_radius * np.sin(theta1_rad)
                x2 = center[0] + outline_radius * np.cos(theta2_rad)
                y2 = center[1] + outline_radius * np.sin(theta2_rad)
                
                # Draw radial lines from center to arc edges
                ax.plot([center[0], x1], [center[1], y1], 
                       color=bbox_color, linewidth=2.5, zorder=10)
                ax.plot([center[0], x2], [center[1], y2], 
                       color=bbox_color, linewidth=2.5, zorder=10)
                
                # Store bounding box coordinates (using polar coordinates)
                bbox_data = {
                    'center': center,
                    'radius': radius,
                    'outline_radius': outline_radius,
                    'theta1': theta1,
                    'theta2': theta2,
                    'theta1_rad': theta1_rad,
                    'theta2_rad': theta2_rad
                }
                bbox_coords[f'slice_{idx}'] = bbox_data
        
        # Also draw bounding boxes around labels and legend entries for highlighted slices
        for idx in bbox_idx:
            # Bounding box for slice label (outside the pie)
            if 0 <= idx < len(texts):
                text = texts[idx]
                bbox = text.get_window_extent(renderer=renderer)
                bbox_fig = bbox.transformed(fig.transFigure.inverted())
                
                rect = plt.Rectangle(
                    (bbox_fig.x0 - 0.005, bbox_fig.y0 - 0.005),
                    bbox_fig.width + 0.01, bbox_fig.height + 0.01,
                    transform=fig.transFigure,
                    fill=False,
                    edgecolor=bbox_color,
                    linewidth=1.5,
                    zorder=100
                )
                fig.patches.append(rect)
            
            # Bounding box for autopct text (percentages/values inside slices)
            if autotexts and 0 <= idx < len(autotexts):
                text = autotexts[idx]
                bbox = text.get_window_extent(renderer=renderer)
                bbox_fig = bbox.transformed(fig.transFigure.inverted())
                
                rect = plt.Rectangle(
                    (bbox_fig.x0 - 0.005, bbox_fig.y0 - 0.005),
                    bbox_fig.width + 0.01, bbox_fig.height + 0.01,
                    transform=fig.transFigure,
                    fill=False,
                    edgecolor=bbox_color,
                    linewidth=1.5,
                    zorder=100
                )
                fig.patches.append(rect)
            
            # Bounding box for legend entry if present
            if show_legend and legend:
                legend_texts = legend.get_texts()
                legend_handles = legend.legend_handles
                
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
                        linewidth=1.5,
                        zorder=100
                    )
                    fig.patches.append(rect)
                    
                    # Bounding box for legend handle (the colored patch)
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
                            linewidth=1.5,
                            zorder=100
                        )
                        fig.patches.append(rect)
    
    # Save the image if a filename is provided
    if img_save_name:
        plt.savefig(img_save_name, dpi=300, bbox_inches='tight')
    
    return fig, bbox_coords


def load_metadata(metadata_path: Optional[str] = None) -> Dict:
    """
    Load metadata from a custom JSON file or use default METADATA_PIE.
    
    Supports two JSON formats:
    1. Standard format: {func_id: {category_id: [chart_entry, ...]}}
    2. Generated format: [{category_id, category_name, chart_entries: {bar, pie, scatter}}, ...]
    
    Args:
        metadata_path: Optional path to a custom metadata JSON file.
                      If None, uses the default METADATA_PIE from metadata.metadata.
    
    Returns:
        Dictionary containing chart metadata in the same format as METADATA_PIE.
    
    Raises:
        FileNotFoundError: If metadata_path is provided but the file doesn't exist.
    """
    if metadata_path is None:
        return METADATA_PIE
    
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
        metadata = _transform_generated_metadata(raw_data, chart_type='pie')
        logger.info(f"Transformed {len(raw_data)} categories from generated format")
    else:
        # Assume it's already in the standard format
        metadata = raw_data
    
    logger.info(f"Loaded custom metadata from: {metadata_path}")
    return metadata


def _transform_generated_metadata(generated_data: List[Dict], chart_type: str = 'pie') -> Dict:
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
        'scatter': 'draw__2_scatter__func_1'  # Assuming scatter uses this func_id
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


def _consolidate_pie_small_slices(chart_entry: Dict, threshold: float = 5.0) -> Dict:
    """
    Consolidate pie slices with percentage below threshold into a single "Other" category.
    Returns a new chart_entry; does not mutate the input.
    """
    if 'pie_data' not in chart_entry:
        return copy.deepcopy(chart_entry)
    pie_data = chart_entry['pie_data']
    pie_labels = chart_entry['pie_labels']
    pie_colors = chart_entry['pie_colors']
    total = sum(pie_data)
    if total <= 0:
        return copy.deepcopy(chart_entry)
    percentages = [100.0 * v / total for v in pie_data]
    small_indices = [i for i, p in enumerate(percentages) if p < threshold]
    if not small_indices:
        return copy.deepcopy(chart_entry)
    new_data = [v for i, v in enumerate(pie_data) if i not in small_indices]
    new_labels = [pie_labels[i] for i in range(len(pie_labels)) if i not in small_indices]
    new_colors = [pie_colors[i] for i in range(len(pie_colors)) if i not in small_indices]
    other_value = sum(pie_data[i] for i in small_indices)
    new_data.append(other_value)
    new_labels.append("Other")
    other_color = pie_colors[small_indices[0]] if small_indices else '#808080'
    new_colors.append(other_color)
    return {
        **chart_entry,
        'pie_data': new_data,
        'pie_labels': new_labels,
        'pie_colors': new_colors,
    }


def collect_all_chart_entries(metadata: Dict) -> List[tuple]:
    """
    Collect all chart entries from metadata with their context.
    Pie chart entries are processed to consolidate slices below 5% into "Other".
    
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
                if 'pie_data' in chart_entry:
                    chart_entry = _consolidate_pie_small_slices(chart_entry)
                all_entries.append((func_id, category_id, chart_entry))
    return all_entries


class PieChartRunDraw(RunDraw):
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
            "draw__8_pie__func_1": {
                "original_img": draw__8_pie__func_1,
                "bbox_img": draw__8_pie__func_1__bbox,
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
            show_percentages: str,
            show_values: str,
            show_legend: str,
            explode_slices: List,
            startangle: float,
            chart_id: str,
            bbox_id: str,
        ):
        """Generate chart with bounding boxes highlighting relevant slices."""
        # Use bbox drawing function to highlight relevant slices
        if '0' in self.args.construction_subtask:
            bbox_color = getattr(self.args, 'bbox_color', '#FF0000')  # Default red
            self.draw_bbox_chart_function(
                args=self.args, 
                pie_data=chart_entry["pie_data"], 
                pie_labels=chart_entry["pie_labels"], 
                pie_colors=chart_entry["pie_colors"],
                img_title=chart_entry["img_title"],
                show_percentages=show_percentages=="w_percent",
                show_values=show_values=="w_value",
                show_legend=show_legend=="w_legend",
                explode_slices=explode_slices,
                startangle=startangle,
                img_save_name=f"{self.root_path}/{bbox_id}__bbox.png",
                bbox_color=bbox_color,
                bbox_idx=bbox_idx_list,
            )

    def run_draw_single_figure(self):
        """Pie chart generation with support for custom metadata, random selection, and configurable questions."""
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
            show_percentages = entry_rng.choice(["w_percent"])  # Can be extended to ["w_percent", "wo_percent"] if needed
            show_values = entry_rng.choice(["w_value"])  # Can be extended to ["w_value", "wo_value"] if needed
            show_legend = entry_rng.choice(["w_legend"])  # Can be extended to ["w_legend", "wo_legend"] if needed
            
            # For pie charts, we need to handle explode_slices and startangle
            # Assume pie_data has 5 slices (as in original code)
            num_slices = len(chart_entry["pie_data"])
            explode_slice_idx = entry_rng.choice(range(num_slices))
            startangle = entry_rng.choice([0, 30, 45, 60, 90])
            
            explode_slices = [0 for _ in range(num_slices)]
            explode_slices[explode_slice_idx] = 0.1
            
            chart_id = f"{self.args.chart_type}__img_{chart_idx}__category{category_id.split(' ')[0]}__{show_percentages}__{show_values}__{show_legend}__segment{explode_slice_idx}__angle{startangle}"
            chart_entry["chart_direction"] = "circular"  # Pie charts are always circular
            logger.info(
                f"{'=' * 100}"
                f"\n{' ' * 10} Image Index: {chart_idx}"
                f"\n{' ' * 10} Chart ID: {chart_id}"
                f"\n{' ' * 10} Configuration: percentages={show_percentages}, values={show_values}, legend={show_legend}, segment={explode_slice_idx}, angle={startangle}"
                f"\n{'=' * 100}"
            )

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
                    startangle=startangle,
                    img_save_name=f"{self.root_path}/{chart_id}.png",
                )

            # Init chart QA data generator
            self.vqa_generator = PieChartGenerator(self.args, chart_id)                                            

            # Chart QA data generation & bbox chart
            # Use configurable number of questions per chart
            qa_data_condidates = self.vqa_generator.chart_qa_generator(
                chart_entry, 
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
                    "eval_mode": show_percentages,
                    "img_path": f"{self.args.data_path}/imgs/{self.args.chart_type}/{self.args.chart_mode}/{chart_id}.png",
                    "bbox_path": new_bbox_path,  # Changed from mask_path
                    "bbox_indices": new_qa_data["bbox"],  # Changed from mask_indices
                    "question": new_qa_data["question"],
                    "reasoning": new_qa_data["reasoning"],
                    "answer": new_qa_data["answer"],
                }

                # Generate bbox chart (highlighting relevant slices)
                for step_key in new_bbox_path:
                    curr_bbox_id = new_bbox_path[step_key].split("/")[-1].replace(".png", "").strip()
                    self._plot_bbox_chart(
                        bbox_idx_list=new_qa_data["bbox"][step_key],  # Indices to highlight
                        chart_entry=chart_entry,
                        show_percentages=show_percentages,
                        show_values=show_values,
                        show_legend=show_legend,
                        explode_slices=explode_slices,
                        startangle=startangle,
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
        description="Pie Chart Generation with QA Data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings (all charts, 20 questions per chart)
  python chartGenerators/pie_chart/main.py
  
  # Generate only 5 random charts with 10 questions each
  python chartGenerators/pie_chart/main.py --num-charts 5 --num-questions 10
  
  # Use custom metadata file and output path
  python chartGenerators/pie_chart/main.py --metadata-path ./custom_metadata.json --data-path ./custom_output
  
  # Generate 10 charts with 15 questions each, using random seed 123
  python chartGenerators/pie_chart/main.py --num-charts 10 --num-questions 15 --random-seed 123
  
  # Only generate original images (no bbox images)
  python chartGenerators/pie_chart/main.py --stages 1
  
  # Generate with custom bbox color
  python chartGenerators/pie_chart/main.py --bbox-color "#00FF00" --num-charts 3
  
  # Full example with all options
  python chartGenerators/pie_chart/main.py \\
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
        help="Path to custom metadata JSON file. If not specified, uses default METADATA_PIE. (default: None)"
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
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create configuration object
    class PieChartArgs:
        def __init__(self):
            self.chart_type = "pie"
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
            self.composition_types = None  # Pie chart generator doesn't support this yet
    
    # Create args object
    config = PieChartArgs()
    
    # Handle figsize - argparse doesn't call type function on defaults
    if isinstance(config.global_figsize, str):
        config.global_figsize = parse_figsize(config.global_figsize)
    
    # Log configuration
    logger.info("=" * 100)
    logger.info("Pie Chart Generation Configuration")
    logger.info("=" * 100)
    logger.info(f"Chart Type: {config.chart_type}")
    logger.info(f"Chart Mode: {config.chart_mode}")
    logger.info(f"Data Path: {config.data_path}")
    logger.info(f"Metadata Path: {config.metadata_path or 'Default (METADATA_PIE)'}")
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
        generator = PieChartRunDraw(config)
        logger.info("Starting pie chart generation...")
        generator.run_draw_single_figure()
        
        logger.info("=" * 100)
        logger.info("Pie chart generation completed successfully!")
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

