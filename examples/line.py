import os
import json
import copy
import numpy as np
import pandas as pd
from typing import List, Dict
import seaborn as sns
import matplotlib.pyplot as plt

from constructor.source.metadata import METADATA_LINE
from constructor.mask import mask_generation
from constructor.source.bar_generator import BarChartGenerator
from utils.logger import logger
from utils.json_util import read_from_json


def draw__4_line__func_1(
        args,
        line_data: List[List],
        line_labels: List,
        line_colors: List,
        x_labels: List,
        x_label: str,
        y_label: str,
        img_title: str,
        horizontal: bool = False,
        line_styles: List = None,
        line_widths: List = None,
        marker_styles: List = None,
        show_markers: bool = False,
        show_text_label: bool = False,
        show_legend: bool = False,
        change_x_axis_pos: bool = False,
        change_y_axis_pos: bool = False,
        img_save_name: str = None,
    ):
    """
    Draw a line chart with customizable axes, colors, and positioning.
    
    This function creates a line chart with specified data series, labels, and colors.
    It allows for customization of line orientation (horizontal or vertical), line styles, 
    markers, axis positions, display of data value labels, and saving the resulting chart.
    
    IMPORTANT NOTE ON PARAMETERS:
    - When horizontal=False (default): 
      * x_labels appears on the x-axis
      * line_data values are displayed on the y-axis
      * x_label labels the x-axis
      * y_label labels the y-axis
      
    - When horizontal=True: 
      * x_labels appears on the y-axis
      * line_data values are displayed on the x-axis
      * x_label is used for the y-axis
      * y_label is used for the x-axis
      * The axis labels are effectively swapped to maintain logical orientation
    
    Args:
        args: Configuration object containing global figure settings
        line_data (List[List]): A list of lists, where each inner list contains values for one line
        line_labels (List): A list of strings for the line series labels
        line_colors (List): A list of hex color codes for the lines
        x_labels (List): A list of axis values (x-axis in vertical mode, y-axis in horizontal mode)
        x_label (str): The label for the primary axis (x-axis in vertical mode, y-axis in horizontal mode)
        y_label (str): The label for the values axis (y-axis in vertical mode, x-axis in horizontal mode)
        img_title (str): The title of the chart
        horizontal (bool, optional): If True, lines are drawn horizontally; if False, vertically. Default is False.
        line_styles (List, optional): List of line styles ('-', '--', '-.', ':'). Default is solid lines.
        line_widths (List, optional): List of line widths. Default is 2.0 for all lines.
        show_markers (bool, optional): If True, show markers on data points. Default is False.
        marker_styles (List, optional): List of marker styles ('o', 's', '^', etc.). Default is circles.
        show_text_label (bool, optional): If True, displays the data value on each point. Default is False.
        show_legend (bool, optional): If True, show the legend; if False, hide the legend. Default is False.
        change_x_axis_pos (bool, optional): If True, X axis is at the top; if False, at the bottom. Default is False.
        change_y_axis_pos (bool, optional): If True, Y axis is at the right; if False, at the left. Default is False.
        img_save_name (str, optional): Filepath to save the image. If None, image is not saved. Default is None.
    
    Returns:
        matplotlib.figure.Figure: The figure object containing the line chart
    """
    # Set default values
    if line_styles is None:
        line_styles = ['-'] * len(line_data)
    if line_widths is None:
        line_widths = [3.0] * len(line_data)
    if marker_styles is None:
        marker_styles = ['o'] * len(line_data)
    
    # Ensure all lists have the same length
    num_lines = len(line_data)
    line_styles = (line_styles * num_lines)[:num_lines]
    line_widths = (line_widths * num_lines)[:num_lines]
    marker_styles = (marker_styles * num_lines)[:num_lines]
    line_colors = (line_colors * num_lines)[:num_lines]
    
    # Create figure
    fig, ax = plt.subplots(figsize=args.global_figsize)
    
    # Draw lines
    lines = []
    for i, (y_data, label, color, style, width, marker) in enumerate(
        zip(line_data, line_labels, line_colors, line_styles, line_widths, marker_styles)
    ):
        if horizontal:
            # Horizontal lines: x_labels on y-axis, y_data on x-axis
            if show_markers:
                line = ax.plot(y_data, x_labels, color=color, linestyle=style, 
                              linewidth=width, marker=marker, markersize=6, label=label)[0]
            else:
                line = ax.plot(y_data, x_labels, color=color, linestyle=style, 
                              linewidth=width, label=label)[0]
        else:
            # Vertical lines: x_labels on x-axis, y_data on y-axis
            if show_markers:
                line = ax.plot(x_labels, y_data, color=color, linestyle=style, 
                              linewidth=width, marker=marker, markersize=6, label=label)[0]
            else:
                line = ax.plot(x_labels, y_data, color=color, linestyle=style, 
                              linewidth=width, label=label)[0]
        lines.append(line)
    
    # Add text labels on data points
    if show_text_label:
        for i, y_data in enumerate(line_data):
            if horizontal:
                # For horizontal lines, text positioning
                for j, (x, y) in enumerate(zip(x_labels, y_data)):
                    ax.text(y * 1.02, x, f'{y:.1f}', ha='left', va='center', fontsize=8)
            else:
                # For vertical lines, text positioning
                for j, (x, y) in enumerate(zip(x_labels, y_data)):
                    ax.text(x, y * 1.02, f'{y:.1f}', ha='center', va='bottom', fontsize=8)
    
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
    
    # Set axis ticks based on orientation
    if horizontal:
        # For horizontal lines, x_labels appears on y-axis
        ax.set_yticks(x_labels)
    else:
        # For vertical lines, x_labels appears on x-axis
        ax.set_xticks(x_labels)
    
    # Add legend
    if show_legend:
        ax.legend(loc='best')
    
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


def draw__4_line__func_1__mask(
        args,
        line_data: List[List],
        line_labels: List,
        line_colors: List,
        x_labels: List,
        x_label: str,
        y_label: str,
        img_title: str,
        horizontal: bool = False,
        line_styles: List = None,
        line_widths: List = None,
        marker_styles: List = None,
        show_markers: bool = False,
        show_text_label: bool = False,
        show_legend: bool = False,
        change_x_axis_pos: bool = False,
        change_y_axis_pos: bool = False,
        img_save_name: str = None,
        mask_color: str = None,
        mask_idx: list = None,
    ):
    """
    Draw a line chart with customizable axes, colors, and positioning, with masking capability.
    
    IMPORTANT NOTE ON PARAMETERS:
    - When horizontal=False (default): 
      * x_labels appears on the x-axis
      * line_data values are displayed on the y-axis
      * x_label labels the x-axis
      * y_label labels the y-axis
      
    - When horizontal=True: 
      * x_labels appears on the y-axis
      * line_data values are displayed on the x-axis
      * x_label is used for the y-axis
      * y_label is used for the x-axis
      * The axis labels are effectively swapped to maintain logical orientation
    
    Args:
        args: Configuration object containing global figure settings
        line_data (List[List]): A list of lists, where each inner list contains values for one line
        line_labels (List): A list of strings for the line series labels
        line_colors (List): A list of hex color codes for the lines
        x_labels (List): A list of axis values (x-axis in vertical mode, y-axis in horizontal mode)
        x_label (str): The label for the primary axis (x-axis in vertical mode, y-axis in horizontal mode)
        y_label (str): The label for the values axis (y-axis in vertical mode, x-axis in horizontal mode)
        img_title (str): The title of the chart
        horizontal (bool, optional): If True, lines are drawn horizontally; if False, vertically. Default is False.
        line_styles (List, optional): List of line styles ('-', '--', '-.', ':'). Default is solid lines.
        line_widths (List, optional): List of line widths. Default is 2.0 for all lines.
        show_markers (bool, optional): If True, show markers on data points. Default is False.
        marker_styles (List, optional): List of marker styles ('o', 's', '^', etc.). Default is circles.
        show_text_label (bool, optional): If True, displays the data value on each point. Default is False.
        show_legend (bool, optional): If True, show the legend; if False, hide the legend. Default is False.
        change_x_axis_pos (bool, optional): If True, X axis is at the top; if False, at the bottom. Default is False.
        change_y_axis_pos (bool, optional): If True, Y axis is at the right; if False, at the left. Default is False.
        img_save_name (str, optional): Filepath to save the image. If None, image is not saved. Default is None.
        mask_color (str, optional): Color to use for masking. If None, uses args.gray_mask. Default is None.
        mask_idx (list, optional): List of line indices to mask. If None, no masking is applied. Default is None.
    
    Returns:
        matplotlib.figure.Figure: The figure object containing the masked line chart
    """
    if mask_color is None:
        mask_color = args.gray_mask
    
    # Validate mask_idx
    if mask_idx is None:
        mask_idx = []
    
    # Set default values
    if line_styles is None:
        line_styles = ['-'] * len(line_data)
    if line_widths is None:
        line_widths = [3.0] * len(line_data)
    if marker_styles is None:
        marker_styles = ['o'] * len(line_data)
    
    # Ensure all lists have the same length
    num_lines = len(line_data)
    line_styles = (line_styles * num_lines)[:num_lines]
    line_widths = (line_widths * num_lines)[:num_lines]
    marker_styles = (marker_styles * num_lines)[:num_lines]
    
    # Create a copy of colors list to mask specific lines
    masked_colors = line_colors.copy()
    
    # Apply mask color to the specified line indices
    for idx in mask_idx:
        if 0 <= idx < len(masked_colors):
            masked_colors[idx] = mask_color
    
    # Ensure colors list has the same length
    masked_colors = (masked_colors * num_lines)[:num_lines]
    
    # Create figure
    fig, ax = plt.subplots(figsize=args.global_figsize)
    
    # Draw lines with masked colors
    lines = []
    for i, (y_data, label, color, style, width, marker) in enumerate(
        zip(line_data, line_labels, masked_colors, line_styles, line_widths, marker_styles)
    ):
        if horizontal:
            # Horizontal lines: x_labels on y-axis, y_data on x-axis
            if show_markers:
                line = ax.plot(y_data, x_labels, color=color, linestyle=style, 
                              linewidth=width, marker=marker, markersize=6, label=label)[0]
            else:
                line = ax.plot(y_data, x_labels, color=color, linestyle=style, 
                              linewidth=width, label=label)[0]
        else:
            # Vertical lines: x_labels on x-axis, y_data on y-axis
            if show_markers:
                line = ax.plot(x_labels, y_data, color=color, linestyle=style, 
                              linewidth=width, marker=marker, markersize=6, label=label)[0]
            else:
                line = ax.plot(x_labels, y_data, color=color, linestyle=style, 
                              linewidth=width, label=label)[0]
        lines.append(line)
    
    # Add text labels on data points
    if show_text_label:
        for i, y_data in enumerate(line_data):
            if horizontal:
                # For horizontal lines, text positioning
                for j, (x, y) in enumerate(zip(x_labels, y_data)):
                    ax.text(y * 1.02, x, f'{y:.1f}', ha='left', va='center', fontsize=8)
            else:
                # For vertical lines, text positioning
                for j, (x, y) in enumerate(zip(x_labels, y_data)):
                    ax.text(x, y * 1.02, f'{y:.1f}', ha='center', va='bottom', fontsize=8)
    
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
    
    # Set axis ticks based on orientation
    if horizontal:
        # For horizontal lines, x_labels appears on y-axis
        ax.set_yticks(x_labels)
    else:
        # For vertical lines, x_labels appears on x-axis
        ax.set_xticks(x_labels)
    
    # Add legend
    legend = None
    if show_legend:
        legend = ax.legend(loc='best')
    
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
    
    # Now apply specific masks only for valid mask_idx
    if mask_idx:
        # Draw the canvas to get proper coordinates
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        
        # 1. Mask the actual lines using bounding boxes
        for idx in mask_idx:
            if 0 <= idx < len(lines):
                line = lines[idx]
                
                # Get the line's path and transform to figure coordinates
                path = line.get_path()
                transform = line.get_transform()
                path_in_display = transform.transform_path(path)
                
                # Get bounding box in display coordinates
                bbox_display = path_in_display.get_extents()
                
                # Transform to figure coordinates
                bbox_fig = bbox_display.transformed(fig.transFigure.inverted())
                
                # Add some padding around the line
                padding_x = 0.015
                padding_y = 0.015
                
                # Create rectangle mask over the line
                rect = plt.Rectangle(
                    (bbox_fig.x0 - padding_x, bbox_fig.y0 - padding_y),
                    bbox_fig.width + (padding_x * 2), bbox_fig.height + (padding_y * 2),
                    transform=fig.transFigure,
                    color=mask_color,
                    zorder=100
                )
                fig.patches.append(rect)
        
        # 2. Mask the text labels on the data points if present
        if show_text_label:
            text_counter = 0
            for i, y_data in enumerate(line_data):
                if i in mask_idx:
                    # Mask all text labels for this line
                    for j in range(len(y_data)):
                        if text_counter < len(ax.texts):
                            text = ax.texts[text_counter]
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
                        text_counter += 1
                else:
                    text_counter += len(y_data)
        
        # 3. Mask the legend if present
        if show_legend and legend:
            texts = legend.get_texts()
            handles = legend.legend_handles
            
            for idx in mask_idx:
                if 0 <= idx < len(texts):
                    # Mask legend text
                    text = texts[idx]
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
                    
                    # Mask legend handle (line)
                    if 0 <= idx < len(handles):
                        handle = handles[idx]
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



class RunDraw:
    def __init__(self, args):
        self.args = args
        self.function_dict = self._init_plot_functions()
        self.draw_chart_function = None
        self.total_img_num = 0
        self.root_path = f"{self.args.data_path}/imgs/{self.args.chart_type}/{self.args.chart_mode}"
        self.generated_vqa_data_save_path = f"{self.args.data_path}/{self.args.chart_type}__meta_qa_data.json"
        self.generated_vqa_data = {}
        self._init_generated_chart_qa_data()

    def _init_plot_functions(self):
        function_dict = {
            "draw__4_line__func_1": {
                "original_img": draw__4_line__func_1,
                "masked_img": draw__4_line__func_1__mask,
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
            chart_direction: str,
            line_styles: List,
            line_widths: List,
            marker_styles: List,
            show_markers: str,
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
                line_data=chart_entry["line_data"], 
                line_labels=chart_entry["line_labels"], 
                line_colors=chart_entry["line_colors"],
                x_labels=chart_entry["x_labels"],
                x_label=chart_entry["x_label"],
                y_label=chart_entry["y_label"],
                img_title=chart_entry["img_title"],
                line_styles=line_styles,
                line_widths=line_widths,
                marker_styles=marker_styles,
                horizontal=chart_direction=="horizontal",
                show_markers=show_markers=="w_markers",
                show_text_label=show_label=="labeled",
                show_legend=show_legend=="withlegend",
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

        for func_id in METADATA_LINE.keys():
            self.draw_chart_function = self.function_dict[func_id]["original_img"]
            self.draw_masked_chart_function = self.function_dict[func_id]["masked_img"]

            for category_id in METADATA_LINE[func_id].keys():
                # List of entries
                chart_metadata = METADATA_LINE[func_id][category_id]

                for chart_entry in chart_metadata:
                    entry_idx += 1

                    for chart_direction in ["vertical", "horizontal"]:
                        for show_label in ["labeled"]:  # currently all labeled for strict eval, or set to ["labeled", "unlabeled"] when with LLM-as-a-judge
                            for x_axis_pos in ["xtop", "xbottom"]:
                                for y_axis_pos in ["yleft", "yright"]:
                                    for show_markers in ["w_markers"]:
                                        for show_legend in ["withlegend"]:  # currently all with legend for strict eval, or set to ["withlegend", "nolegend"] when with LLM-as-a-judge
                                            for line_styles in [["-", ":", "--", "-."]]:
                                                for line_widths in [[3.5, 3.5, 3.5, 3.5]]:
                                                    for marker_styles in [["o", "^", "*", "D"]]:
                                                        chart_idx += 1
                                                        chart_id = f"{self.args.chart_type}__img_{chart_idx}__category{category_id.split(' ')[0]}__{chart_direction}__{show_markers}__{show_label}__{show_legend}__{x_axis_pos}__{y_axis_pos}"
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
                                                                line_data=chart_entry["line_data"], 
                                                                line_labels=chart_entry["line_labels"], 
                                                                line_colors=chart_entry["line_colors"],
                                                                x_labels=chart_entry["x_labels"],
                                                                x_label=chart_entry["x_label"],
                                                                y_label=chart_entry["y_label"],
                                                                img_title=chart_entry["img_title"],
                                                                line_styles=line_styles,
                                                                line_widths=line_widths,
                                                                marker_styles=marker_styles,
                                                                horizontal=chart_direction=="horizontal",
                                                                show_markers=show_markers=="w_markers",
                                                                show_text_label=show_label=="labeled",
                                                                show_legend=show_legend=="withlegend",
                                                                change_x_axis_pos=x_axis_pos=="xtop",
                                                                change_y_axis_pos=y_axis_pos=="yright",
                                                                img_save_name=f"{self.root_path}/{chart_id}.png",
                                                            )

                                                        # Init chart QA data generator
                                                        self.vqa_generator = ScatterChartGenerator(self.args, chart_id)                                            

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
