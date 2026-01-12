import os
import json
import copy
import numpy as np
import pandas as pd
from typing import List, Dict
import seaborn as sns
import matplotlib.pyplot as plt

from constructor.source.metadata import METADATA_HEATMAP
from constructor.mask import mask_generation
from constructor.source.heatmap_generator import ScatterChartGenerator
from utils.logger import logger
from utils.json_util import read_from_json


def draw__7_heatmap__func_1(
        args,
        heatmap_data: Union[List[List], np.ndarray],
        x_labels: List[str],
        y_labels: List[str],
        x_label: str,
        y_label: str,
        img_title: str,
        colormap: str = 'Set3',
        show_values: bool = False,
        show_colorbar: bool = True,
        change_x_axis_pos: bool = False,
        change_y_axis_pos: bool = False,
        img_save_name: str = None,
    ):
    """
    Draw a heatmap with customizable axes, colors, and positioning.
    
    This function creates a heatmap with specified data values, labels, and colormap.
    It allows for customization of axis positions, display of data values, and saving the resulting chart.
    
    Args:
        args: Configuration object containing global figure settings
        heatmap_data (Union[List[List], np.ndarray]): 2D array or list of lists containing the heatmap values
        x_labels (List[str]): Labels for the x-axis (columns)
        y_labels (List[str]): Labels for the y-axis (rows)
        x_label (str): The label for the x-axis
        y_label (str): The label for the y-axis
        img_title (str): The title of the chart
        colormap (str, optional): Colormap to use for the heatmap. Default is 'Set3'.
        show_values (bool, optional): If True, displays the data value in each cell. Default is False.
        show_colorbar (bool, optional): If True, show the colorbar; if False, hide it. Default is True.
        change_x_axis_pos (bool, optional): If True, X axis is at the top; if False, at the bottom. Default is False.
        change_y_axis_pos (bool, optional): If True, Y axis is at the right; if False, at the left. Default is False.
        img_save_name (str, optional): Filepath to save the image. If None, image is not saved. Default is None.
    
    Returns:
        matplotlib.figure.Figure: The figure object containing the heatmap
    """
    # Convert data to numpy array for easier handling
    heatmap_data = np.array(heatmap_data)
    
    # Create figure
    fig, ax = plt.subplots(figsize=args.global_figsize)
    
    # Create the heatmap
    im = ax.imshow(heatmap_data, cmap=colormap, aspect='auto')
    
    # Set the ticks and labels
    ax.set_xticks(np.arange(len(x_labels)))
    ax.set_yticks(np.arange(len(y_labels)))
    ax.set_xticklabels(x_labels)
    ax.set_yticklabels(y_labels)
    
    # Rotate the tick labels and set their alignment
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    
    # Set the position of the axes
    if change_x_axis_pos:
        ax.xaxis.tick_top()
        ax.xaxis.set_label_position('top')
        plt.setp(ax.get_xticklabels(), rotation=45, ha="left", rotation_mode="anchor")
    
    if change_y_axis_pos:
        ax.yaxis.tick_right()
        ax.yaxis.set_label_position('right')
    
    # Set labels and title
    ax.set_xlabel(x_label, fontsize=13)
    ax.set_ylabel(y_label, fontsize=13)
    ax.set_title(img_title, fontsize=16)
    
    # Add text annotations if requested
    if show_values:
        for i in range(len(y_labels)):
            for j in range(len(x_labels)):
                text = ax.text(j, i, f'{heatmap_data[i, j]:.2f}',
                             ha="center", va="center", color="black", fontweight="bold")
    
    # Add colorbar
    if show_colorbar:
        cbar = plt.colorbar(im, ax=ax)
        cbar.ax.tick_params(labelsize=12)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the image if a save path is provided
    if img_save_name:
        plt.savefig(img_save_name, dpi=300, bbox_inches='tight')
    
    return fig


def draw__7_heatmap__func_1__mask(
        args,
        heatmap_data: Union[List[List], np.ndarray],
        x_labels: List[str],
        y_labels: List[str],
        x_label: str,
        y_label: str,
        img_title: str,
        colormap: str = 'Set3',
        show_values: bool = False,
        show_colorbar: bool = True,
        change_x_axis_pos: bool = False,
        change_y_axis_pos: bool = False,
        img_save_name: str = None,
        mask_color: str = None,
        mask_cells: List[tuple] = None,
        mask_rows: List[int] = None,
        mask_cols: List[int] = None,
    ):
    """
    Draw a heatmap with customizable axes, colors, and positioning, with masking capability.
    
    This function creates a heatmap with specified data values, labels, and colormap,
    and applies masking to specified cells, rows, or columns.
    
    Args:
        args: Configuration object containing global figure settings
        heatmap_data (Union[List[List], np.ndarray]): 2D array or list of lists containing the heatmap values
        x_labels (List[str]): Labels for the x-axis (columns)
        y_labels (List[str]): Labels for the y-axis (rows)
        x_label (str): The label for the x-axis
        y_label (str): The label for the y-axis
        img_title (str): The title of the chart
        colormap (str, optional): Colormap to use for the heatmap. Default is 'Set3'.
        show_values (bool, optional): If True, displays the data value in each cell. Default is False.
        show_colorbar (bool, optional): If True, show the colorbar; if False, hide it. Default is True.
        change_x_axis_pos (bool, optional): If True, X axis is at the top; if False, at the bottom. Default is False.
        change_y_axis_pos (bool, optional): If True, Y axis is at the right; if False, at the left. Default is False.
        img_save_name (str, optional): Filepath to save the image. If None, image is not saved. Default is None.
        mask_color (str, optional): Color to use for masking. If None, uses args.gray_mask. Default is None.
        mask_cells (List[tuple], optional): List of (row, col) tuples to mask specific cells. Default is None.
        mask_rows (List[int], optional): List of row indices to mask entirely. Default is None.
        mask_cols (List[int], optional): List of column indices to mask entirely. Default is None.
    
    Returns:
        matplotlib.figure.Figure: The figure object containing the masked heatmap
    """
    if mask_color is None:
        mask_color = args.gray_mask
    
    # Initialize mask lists if None
    if mask_cells is None:
        mask_cells = []
    if mask_rows is None:
        mask_rows = []
    if mask_cols is None:
        mask_cols = []
    
    # Convert data to numpy array for easier handling
    heatmap_data = np.array(heatmap_data)
    
    # Create figure
    fig, ax = plt.subplots(figsize=args.global_figsize)
    
    # Create the heatmap
    im = ax.imshow(heatmap_data, cmap=colormap, aspect='auto')
    
    # Set the ticks and labels
    ax.set_xticks(np.arange(len(x_labels)))
    ax.set_yticks(np.arange(len(y_labels)))
    ax.set_xticklabels(x_labels)
    ax.set_yticklabels(y_labels)
    
    # Rotate the tick labels and set their alignment
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    
    # Set the position of the axes
    if change_x_axis_pos:
        ax.xaxis.tick_top()
        ax.xaxis.set_label_position('top')
        plt.setp(ax.get_xticklabels(), rotation=45, ha="left", rotation_mode="anchor")
    
    if change_y_axis_pos:
        ax.yaxis.tick_right()
        ax.yaxis.set_label_position('right')
    
    # Set labels and title
    ax.set_xlabel(x_label, fontsize=13)
    ax.set_ylabel(y_label, fontsize=13)
    ax.set_title(img_title, fontsize=16)
    
    # Add text annotations if requested
    text_objects = []
    if show_values:
        for i in range(len(y_labels)):
            for j in range(len(x_labels)):
                text = ax.text(j, i, f'{heatmap_data[i, j]:.2f}',
                             ha="center", va="center", color="black", fontweight="bold")
                text_objects.append((text, i, j))
    
    # Add colorbar
    if show_colorbar:
        cbar = plt.colorbar(im, ax=ax)
        cbar.ax.tick_params(labelsize=12)
    
    # Adjust layout
    plt.tight_layout()
    
    # Apply masking
    if mask_cells or mask_rows or mask_cols:
        # Draw the canvas to get proper coordinates
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        
        # Collect all cells to mask
        cells_to_mask = set()
        
        # Add specific cells
        for cell in mask_cells:
            if len(cell) == 2:
                row, col = cell
                if 0 <= row < len(y_labels) and 0 <= col < len(x_labels):
                    cells_to_mask.add((row, col))
        
        # Add entire rows
        for row in mask_rows:
            if 0 <= row < len(y_labels):
                for col in range(len(x_labels)):
                    cells_to_mask.add((row, col))
        
        # Add entire columns
        for col in mask_cols:
            if 0 <= col < len(x_labels):
                for row in range(len(y_labels)):
                    cells_to_mask.add((row, col))
        
        # Mask heatmap cells
        for row, col in cells_to_mask:
            # Create a rectangle to mask the cell
            rect = patches.Rectangle((col - 0.5, row - 0.5), 1, 1, 
                                   linewidth=0, facecolor=mask_color, zorder=10)
            ax.add_patch(rect)
        
        # Mask text values if they exist
        if show_values and text_objects:
            for text, row, col in text_objects:
                if (row, col) in cells_to_mask:
                    bbox = text.get_window_extent(renderer=renderer)
                    bbox_fig = bbox.transformed(fig.transFigure.inverted())
                    
                    mask_rect = plt.Rectangle(
                        (bbox_fig.x0 - 0.005, bbox_fig.y0 - 0.005),
                        bbox_fig.width + 0.01, bbox_fig.height + 0.01,
                        transform=fig.transFigure,
                        color=mask_color,
                        zorder=100
                    )
                    fig.patches.append(mask_rect)
        
        # Mask x-axis labels
        x_labels_to_mask = set()
        for col in mask_cols:
            if 0 <= col < len(x_labels):
                x_labels_to_mask.add(col)
        
        for col in x_labels_to_mask:
            if col < len(ax.get_xticklabels()):
                label = ax.get_xticklabels()[col]
                bbox = label.get_window_extent(renderer=renderer)
                bbox_fig = bbox.transformed(fig.transFigure.inverted())
                
                mask_rect = plt.Rectangle(
                    (bbox_fig.x0 - 0.01, bbox_fig.y0 - 0.005),
                    bbox_fig.width + 0.02, bbox_fig.height + 0.01,
                    transform=fig.transFigure,
                    color=mask_color,
                    zorder=100
                )
                fig.patches.append(mask_rect)
        
        # Mask y-axis labels
        y_labels_to_mask = set()
        for row in mask_rows:
            if 0 <= row < len(y_labels):
                y_labels_to_mask.add(row)
        
        for row in y_labels_to_mask:
            if row < len(ax.get_yticklabels()):
                label = ax.get_yticklabels()[row]
                bbox = label.get_window_extent(renderer=renderer)
                bbox_fig = bbox.transformed(fig.transFigure.inverted())
                
                mask_rect = plt.Rectangle(
                    (bbox_fig.x0 - 0.005, bbox_fig.y0 - 0.005),
                    bbox_fig.width + 0.01, bbox_fig.height + 0.01,
                    transform=fig.transFigure,
                    color=mask_color,
                    zorder=100
                )
                fig.patches.append(mask_rect)
    
    # Save the image if a filename is provided
    if img_save_name:
        plt.savefig(img_save_name, dpi=300, bbox_inches='tight')
    
    return fig


class RunDraw:
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
            "draw__7_heatmap__func_1": {
                "original_img": draw__7_heatmap__func_1,
                "masked_img": draw__7_heatmap__func_1__mask,
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
            colormap: str,
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
                heatmap_data=chart_entry["heatmap_data"], 
                x_labels=chart_entry["x_labels"], 
                y_labels=chart_entry["y_labels"],
                x_label=chart_entry["x_label"],
                y_label=chart_entry["y_label"],
                img_title=chart_entry["img_title"],
                colormap=colormap,
                horizontal=chart_direction=="horizontal",
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

        for func_id in METADATA_HEATMAP.keys():
            self.draw_chart_function = self.function_dict[func_id]["original_img"]
            self.draw_masked_chart_function = self.function_dict[func_id]["masked_img"]

            for category_id in METADATA_HEATMAP[func_id].keys():
                # List of entries
                chart_metadata = METADATA_HEATMAP[func_id][category_id]

                for chart_entry in chart_metadata:
                    entry_idx += 1

                    for chart_direction in ["vertical", "horizontal"]:
                        for show_label in ["labeled"]:  # currently all labeled for strict eval, or set to ["labeled", "unlabeled"] when with LLM-as-a-judge
                            for x_axis_pos in ["xtop", "xbottom"]:
                                for y_axis_pos in ["yleft", "yright"]:
                                    for show_legend in ["withlegend"]:  # currently all with legend for strict eval, or set to ["withlegend", "nolegend"] when with LLM-as-a-judge
                                        for colormap in ["Pastel1"]:
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
                                                    heatmap_data=chart_entry["heatmap_data"], 
                                                    x_labels=chart_entry["x_labels"], 
                                                    y_labels=chart_entry["y_labels"],
                                                    x_label=chart_entry["x_label"],
                                                    y_label=chart_entry["y_label"],
                                                    img_title=chart_entry["img_title"],
                                                    colormap=colormap,
                                                    horizontal=chart_direction=="horizontal",
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
                                                        colormap=colormap,
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
