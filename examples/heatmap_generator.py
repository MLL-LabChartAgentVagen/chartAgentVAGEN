import os
import json
import copy
from typing import List, Dict, Union, Tuple


class HeatmapGenerator:
    def __init__(self, args, chart_id):
        self.chart_type = args.chart_type
        self.chart_id = chart_id
        self.all_qa_data_list = []
        self.round_num = 2
        self.qa_idx = 0
    
    def _qa_pool_converter(self, qa_pool: Dict, curriculum_level: int):
        """Convert qa pool to a list of Chart QA data dicts."""
        
        for qa_type_key in qa_pool:
            qa_metadata = qa_pool[qa_type_key]
            constraint = qa_metadata["constraint"]
            gt_answer = qa_metadata["answer"]
            gt_mask = qa_metadata["mask"]

            # Reformat answer
            if isinstance(gt_answer, float):
                # gt_answer = round(gt_answer, self.round_num)
                gt_answer = format(gt_answer, f'.{self.round_num}f')
            if not isinstance(gt_answer, str):
                gt_answer = str(gt_answer)

            for new_question in qa_metadata["question"]:
                for new_reasoning in qa_metadata["reasoning"]:
                    self.qa_idx += 1
                    
                    # Align mask with reasoning
                    new_gt_mask = {}
                    for step_key in new_reasoning:
                        new_gt_mask[step_key] = gt_mask[step_key]
                    new_gt_mask["answer"] = gt_mask["answer"]

                    # New QA data
                    new_qa_data = {
                        "qa_id": f"{self.chart_id}_qa{self.qa_idx}",
                        "qa_type": qa_type_key,
                        "curriculum_level": str(curriculum_level),
                        "constraint": constraint,
                        "question": new_question,
                        "reasoning": new_reasoning,
                        "answer": gt_answer,
                        "mask": new_gt_mask,
                    }

                    self.all_qa_data_list.append(new_qa_data)


    ############################################################
    #                     Utility Functions
    ############################################################

    def _compute_data_sum(self, data: List):
        """
        Compute the sum of all elements in the input list.
        
        Args:
            data: A list of integers or floats
            
        Returns:
            The sum of all elements in the list
            
        Raises:
            TypeError: If any element in the list is not an int or float
        """
        # Check if input is a list
        if not isinstance(data, List):
            raise TypeError("Input must be a list")
        
        # Initialize sum
        total = 0
        
        # Iterate through each element and add to total
        for item in data:
            # Check if item is a number (int or float)
            if not isinstance(item, (int, float)):
                raise TypeError(f"All elements must be numbers, got {type(item)} instead")
            
            # Add to total
            total += item
        
        return total
    
    def _compute_matrix_row_sum(self, matrix: List[List[Union[int, float]]]) -> List[float]:
        return [sum(row) for row in matrix]

    def _compute_matrix_column_sum(self, matrix: List[List[Union[int, float]]]) -> List[float]:
        return [sum(column) for column in zip(*matrix)]


    def _compute_data_mean(self, data):
        """
        Compute the mean value of a list of numeric data.
        
        Args:
            data: A list of integers or floats
            
        Returns:
            The mean (average) of all values in the list
            
        Raises:
            ValueError: If the input list is empty
            TypeError: If the input contains non-numeric values
        """
        if not data:
            raise ValueError("Cannot compute mean of empty list")
        
        # Validate all elements are numeric
        for value in data:
            if not isinstance(value, (int, float)):
                raise TypeError(f"All elements must be numeric, found {type(value)}")
        
        # Calculate the mean
        total = sum(data)
        count = len(data)
        mean_value = total / count
        return mean_value

    def _compute_data_median(self, data):
        """
        Compute the median of a list of numeric data and return both the median value
        and the corresponding index/indices from the original data.
        
        Args:
            data: List of int or float values
            
        Returns:
            tuple: (median_value, median_indices)
                - median_value: float or list of two floats
                - median_indices: list of one integer index or two integer indices
        """
        # Handle empty list
        if not data:
            return None, []
        
        # Create a list of (value, index) tuples
        indexed_data = [(value, index) for index, value in enumerate(data)]
        
        # Sort by value
        indexed_data.sort(key=lambda x: x[0])
        
        n = len(indexed_data)
        
        # If odd number of elements
        if n % 2 == 1:
            middle_idx = n // 2
            median_value = indexed_data[middle_idx][0]
            median_indices = [indexed_data[middle_idx][1]]
            return median_value, median_indices
        
        # If even number of elements
        else:
            middle_idx1 = n // 2 - 1
            middle_idx2 = n // 2
            
            value1, orig_idx1 = indexed_data[middle_idx1]
            value2, orig_idx2 = indexed_data[middle_idx2]
            
            median_value = (value1 + value2) / 2
            median_indices = [orig_idx1, orig_idx2]
            
            return median_value, median_indices

    def _get_middle_value_rows(self, heatmap_data):
        """
        Get rows that contain values that are neither the global minimum nor maximum.
        
        Args:
            heatmap_data: 2D matrix of heatmap values
            
        Returns:
            List of row indices that contain middle values
        """
        # Find global min and max values
        all_values = [val for row in heatmap_data for val in row]
        min_val = min(all_values)
        max_val = max(all_values)
        
        middle_rows = []
        for row_idx, row in enumerate(heatmap_data):
            # Check if this row contains any values that are not min or max
            has_middle_values = any(min_val < val < max_val for val in row)
            if has_middle_values:
                middle_rows.append(row_idx)
        
        return middle_rows

    def _find_matrix_extrema_with_pos(self, matrix):
        """
        Find the minimum and maximum elements in a 2D list (list of sublists)
        and return their values along with their positions.
        
        Args:
            matrix: List of sublists containing numeric values
        
        Returns:
            Dictionary with min_value, min_pos, max_value, max_pos
        """
        if not matrix or not matrix[0]:
            raise ValueError("Matrix cannot be empty")
        
        # Initialize with first element
        min_value = max_value = matrix[0][0]
        min_pos = max_pos = [0, 0]
        
        # Iterate through all elements
        for row_idx, row in enumerate(matrix):
            for col_idx, value in enumerate(row):
                if value < min_value:
                    min_value = value
                    min_pos = [row_idx, col_idx]
                if value > max_value:
                    max_value = value
                    max_pos = [row_idx, col_idx]
        
        return {
            "min_value": min_value,
            "min_pos": min_pos,
            "max_value": max_value,
            "max_pos": max_pos
        }

    def _idx_of_the_largest_data(self, data_list) -> List:
        """
        Find the indices of all occurrences of the largest value in a list of numeric data.
        
        Parameters:
        data_list (list): A list of integers or floats
        
        Returns:
        list: A list of indices where the largest value occurs (0-based indexing)
        
        Raises:
        ValueError: If the input list is empty
        """
        if not data_list:
            raise ValueError("Input list cannot be empty")
        
        # Find the maximum value in the list
        max_value = max(data_list)
        
        # Find all indices where this maximum value occurs
        max_indices = [i for i, value in enumerate(data_list) if value == max_value]
        
        return max_indices

    def _idx_of_the_smallest_data(self, data_list) -> List:
        """
        Find the indices of all occurrences of the smallest value in a list of numeric data.
        
        Parameters:
        data_list (list): A list of integers or floats
        
        Returns:
        list: A list of indices where the smallest value occurs (0-based indexing)
        
        Raises:
        ValueError: If the input list is empty
        """
        if not data_list:
            raise ValueError("Input list cannot be empty")
        
        # Find the minimum value in the list
        min_value = min(data_list)
        
        # Find all indices where this minimum value occurs
        min_indices = [i for i, value in enumerate(data_list) if value == min_value]
        
        return min_indices

    def _filter_middle_indices(self, numbers: List):
        if not numbers:
            return []

        # Find the min and max values
        min_val = min(numbers)
        max_val = max(numbers)

        # Find indices of min and max values
        min_indices = {i for i, num in enumerate(numbers) if num == min_val}
        max_indices = {i for i, num in enumerate(numbers) if num == max_val}

        # Filter out indices that are neither min nor max
        result = [i for i in range(len(numbers)) if i not in min_indices and i not in max_indices]
        return result

    def _convert_answer_idx_to_str(self, chart_labels: List, ans_indices: List) -> str:
        """Convert to answer string"""
        ans_list = [chart_labels[ans_idx] for ans_idx in ans_indices]
        return ", ".join(ans_list)

    def _convert_idx_to_pos(self, chart_idx):
        """Convert chart index to position"""
        pos = [
            "1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th",
            "11th", "12th", "13th", "14th", "15th", "16th", "17th", "18th", "19th", "20th",
            "21st", "22nd", "23rd", "24th", "25th", "26th", "27th", "28th", "29th", "30th",
        ]
        return pos[chart_idx]

    def _get_pos_compare_relative(self, chart_direction: str, pos: str) -> str:
        assert chart_direction in ["vertical", "horizontal"]
        assert pos in ["left", "right"]

        if chart_direction == "vertical":
            return pos
        else:
            if pos == "left":
                return "upper"
            else:
                return "lower"

    def _get_pos_compare_extrema(self, chart_direction: str, pos: str) -> str:
        assert chart_direction in ["vertical", "horizontal"]
        assert pos in ["leftmost", "rightmost"]

        if chart_direction == "vertical":
            return pos
        else:
            if pos == "left":
                return "top"
            else:
                return "bottom"

    def _sort_y_order_for_x(self, data_list: List, label_list: List, sort_order: str) -> str:
        # Create pairs of (data, label) to keep track of corresponding labels
        pairs = list(zip(data_list, label_list))
        
        # Sort the pairs based on the data values
        if sort_order == "ascending":
            sorted_pairs = sorted(pairs, key=lambda x: x[0])
        else:  # "descending"
            sorted_pairs = sorted(pairs, key=lambda x: x[0], reverse=True)
        
        # Extract the sorted labels
        sorted_labels = [label for _, label in sorted_pairs]
        
        # Join the sorted labels with commas and return
        return ", ".join(sorted_labels)

    def _find_kth_highest_index(self, data_list, k):
        """
        Find the index(es) of the k-th highest value in data_list.
        
        Args:
            data_list: List of floats
            k: Integer (1-indexed, where 1 = highest value)
        
        Returns:
            List of indices where the k-th highest value appears
        
        Raises:
            ValueError: If k is out of valid range
        """
        if not data_list:
            raise ValueError("data_list cannot be empty")
        
        # Get unique values and sort in descending order
        unique_values = sorted(set(data_list), reverse=True)
        
        if k < 1 or k > len(unique_values):
            raise ValueError(f"k must be between 1 and {len(unique_values)}")
        
        # Find the k-th highest unique value
        kth_highest_value = unique_values[k-1]
        
        # Return all indices where this value appears
        return [i for i, value in enumerate(data_list) if value == kth_highest_value]

    def _find_kth_lowest_index(self, data_list, k):
        """
        Find the index(es) of the k-th lowest value in data_list.
        
        Args:
            data_list: List of floats
            k: Integer (1-indexed, where 1 = lowest value)
        
        Returns:
            List of indices where the k-th lowest value appears
        
        Raises:
            ValueError: If k is out of valid range
        """
        if not data_list:
            raise ValueError("data_list cannot be empty")
        
        # Get unique values and sort in ascending order (lowest first)
        unique_values = sorted(set(data_list))
        
        if k < 1 or k > len(unique_values):
            raise ValueError(f"k must be between 1 and {len(unique_values)}")
        
        # Find the k-th lowest unique value
        kth_lowest_value = unique_values[k-1]
        
        # Return all indices where this value appears
        return [i for i, value in enumerate(data_list) if value == kth_lowest_value]

    def _find_indices_in_list(self, data_list: List, target: float):
        """
        Find all indices where the target value appears in the data list.
        
        Args:
            data_list (list): List of float values to search through
            target (float): The value to find indices for
        
        Returns:
            list: List of indices where target appears in data_list
        """
        return [i for i, value in enumerate(data_list) if value == target]



    ############################################################
    #   One-step Operator: h(list[Bar] | list[v]) → list[v]
    ############################################################
    
    def _one_step_statistics(self, chart_metadata: Dict):
    """
    Statistics: sum, mean, median, count
    """
    x_axis_title = chart_metadata['x_label'].lower()
    y_axis_title = chart_metadata['y_label'].lower()
    heatmap_category = copy.deepcopy(chart_metadata["heatmap_category"])
    target_row_data = copy.deepcopy(chart_metadata["heatmap_data"])  # matrix
    target_column_data = [list(column_list) for column_list in zip(*target_row_data)]
    target_x_labels = copy.deepcopy(chart_metadata["x_labels"])
    target_y_labels = copy.deepcopy(chart_metadata["y_labels"])
    target_heatmap_indices = [x_idx for x_idx in range(len(target_x_labels))]

    # Sum
    row_sum = self._compute_matrix_row_sum(target_row_data)
    column_sum = self._compute_matrix_column_sum(target_row_data)
    total_sum = sum([sum(row) for row in target_row_data])
    
    # Mean
    total_cells = len(target_y_labels) * len(target_x_labels)
    overall_mean = total_sum / total_cells
    row_mean = [curr_sum / len(target_x_labels) for curr_sum in row_sum]
    column_mean = [curr_sum / len(target_y_labels) for curr_sum in column_sum]

    # Median
    all_values = [val for row in target_row_data for val in row]
    overall_median_value, overall_median_indices = self._compute_data_median(all_values)
    
    row_median_value, row_median_indices = [], []
    for kth_row_data_list in target_row_data:
        kth_row_median_value, kth_row_median_indices = self._compute_data_median(kth_row_data_list)
        row_median_value.append(kth_row_median_value)
        row_median_indices.append(kth_row_median_indices)

    column_median_value, column_median_indices = [], []
    for kth_column_data_list in target_column_data:
        kth_column_median_value, kth_column_median_indices = self._compute_data_median(kth_column_data_list)
        column_median_value.append(kth_column_median_value)
        column_median_indices.append(kth_column_median_indices)

    # Count
    count_row_num = len(target_y_labels)
    count_column_num = len(target_x_labels)
    count_total_cells = count_row_num * count_column_num

    # All cell indices for masking
    all_cell_indices = []
    for row_idx in range(len(target_y_labels)):
        for col_idx in range(len(target_x_labels)):
            all_cell_indices.append((row_idx, col_idx))

    # Chart QA Pool
    easy_qa_pool = {
        "one_step__statistics__sum_total": {
            "question": [
                f"What is the total sum of all {heatmap_category['plural']} in this heatmap?",
                f"What is the sum of all {heatmap_category['plural']} shown in this heatmap?",
                f"Can you help calculate the total sum of all {heatmap_category['plural']} in this heatmap?",
                f"Please compute the sum of all {heatmap_category['plural']} in this heatmap.",
            ],
            "reasoning": [
                {
                    "step_1": f"First, I need to read all the {heatmap_category['plural']} in this heatmap.",
                    "step_2": f"Second, I need to sum them up to calculate the total sum of all {heatmap_category['plural']}.",
                },
            ],
            "constraint": None,
            "answer": total_sum,
            "mask": {
                "step_1": all_cell_indices,
                "step_2": all_cell_indices,
                "answer": all_cell_indices,
            },
        },
        "one_step__statistics__mean_total": {
            "question": [
                f"What is the mean {heatmap_category['singular']} of all cells in this heatmap? Please round to two decimal places.",
                f"What is the average {heatmap_category['singular']} of all cells in this heatmap? Please round to two decimal places.",
                f"Can you help calculate the mean {heatmap_category['singular']} of all cells in this heatmap? Please round to two decimal places.",
                f"Please compute the average {heatmap_category['singular']} of all cells in this heatmap. Please round to two decimal places.",
            ],
            "reasoning": [
                {
                    "step_1": f"First, I need to read all the {heatmap_category['plural']} in this heatmap.",
                    "step_2": f"Second, I need to calculate the mean {heatmap_category['singular']} of all cells.",
                },
            ],
            "constraint": None,
            "answer": overall_mean,
            "mask": {
                "step_1": all_cell_indices,
                "step_2": all_cell_indices,
                "answer": all_cell_indices,
            },
        },
        "one_step__statistics__median_total": {
            "question": [
                f"What is the median {heatmap_category['singular']} of all cells in this heatmap?",
                f"What is the median value of all {heatmap_category['plural']} in this heatmap?",
                f"Can you help calculate the median {heatmap_category['singular']} of all cells in this heatmap?",
                f"Please compute the median {heatmap_category['singular']} of all cells in this heatmap.",
            ],
            "reasoning": [
                {
                    "step_1": f"First, I need to read all the {heatmap_category['plural']} in this heatmap.",
                    "step_2": f"Second, I need to calculate the median {heatmap_category['singular']} of all cells.",
                },
            ],
            "constraint": None,
            "answer": overall_median_value,
            "mask": {
                "step_1": all_cell_indices,
                "step_2": all_cell_indices,
                "answer": all_cell_indices,
            },
        },
        "one_step__statistics__count_total": {
            "question": [
                f"How many cells are there in this heatmap?",
                f"What is the total number of cells in this heatmap?",
                f"Please help count the total number of cells in this heatmap.",
            ],
            "reasoning": [
                {
                    "step_1": f"First, I need to count the number of cells in this heatmap.",
                },
            ],
            "constraint": None,
            "answer": count_total_cells,
            "mask": {
                "step_1": all_cell_indices,
                "answer": all_cell_indices,
            },
        },
        "one_step__statistics__count_rows": {
            "question": [
                f"How many rows are there in this heatmap?",
                f"What is the number of rows shown in this heatmap?",
                f"Please help count the number of rows in this heatmap.",
            ],
            "reasoning": [
                {
                    "step_1": f"First, I need to count the number of rows in this heatmap.",
                },
            ],
            "constraint": None,
            "answer": count_row_num,
            "mask": {
                "step_1": list(range(len(target_y_labels))),
                "answer": list(range(len(target_y_labels))),
            },
        },
        "one_step__statistics__count_columns": {
            "question": [
                f"How many columns are there in this heatmap?",
                f"What is the number of columns shown in this heatmap?",
                f"Please help count the number of columns in this heatmap.",
            ],
            "reasoning": [
                {
                    "step_1": f"First, I need to count the number of columns in this heatmap.",
                },
            ],
            "constraint": None,
            "answer": count_column_num,
            "mask": {
                "step_1": list(range(len(target_x_labels))),
                "answer": list(range(len(target_x_labels))),
            },
        },
    }

    return easy_qa_pool
        
    def _one_step_extrema(self, chart_metadata: Dict):
        """
        Extrema: value (min, max), pos (left, right, top, bottom)
        """
        x_axis_title = chart_metadata['x_label'].lower()
        y_axis_title = chart_metadata['y_label'].lower()
        heatmap_category = copy.deepcopy(chart_metadata["heatmap_category"])
        target_row_data = copy.deepcopy(chart_metadata["heatmap_data"])  # matrix
        target_column_data = [list(column_list) for column_list in zip(*target_row_data)]
        target_x_labels = copy.deepcopy(chart_metadata["x_labels"])
        target_y_labels = copy.deepcopy(chart_metadata["y_labels"])

        # Value: Min & Max
        extrema_dict = self._find_matrix_extrema_with_pos(target_row_data)
        min_value, min_pos = extrema_dict["min_value"], extrema_dict["min_pos"]
        min_label_answer = f"{target_y_labels[min_pos[0]]}, {target_x_labels[min_pos[1]]}"
        max_value, max_pos = extrema_dict["max_value"], extrema_dict["max_pos"]
        max_label_answer = f"{target_y_labels[max_pos[0]]}, {target_x_labels[max_pos[1]]}"

        # All cell indices for masking
        all_cell_indices = []
        for row_idx in range(len(target_y_labels)):
            for col_idx in range(len(target_x_labels)):
                all_cell_indices.append((row_idx, col_idx))

        # Chart QA Pool
        easy_qa_pool = {
            "one_step__extrema__value__min__value": {
                "question": [
                    f"What is the lowest {heatmap_category['singular']} in this heatmap?",
                    f"What is the smallest {heatmap_category['singular']} in this heatmap?",
                    f"What is the minimum {heatmap_category['singular']} shown in this heatmap?",
                    f"Among all the {heatmap_category['plural']} in this heatmap, what is the lowest one?",
                    f"Among all the {heatmap_category['plural']} in this heatmap, what is the smallest one?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read all the {heatmap_category['plural']} in this heatmap.",
                        "step_2": f"Second, I need to compare them to find the lowest {heatmap_category['singular']}.",
                    },
                ],
                "constraint": None,
                "answer": min_value,
                "mask": {
                    "step_1": all_cell_indices,
                    "step_2": [(min_pos[0], min_pos[1])],
                    "answer": [(min_pos[0], min_pos[1])],
                },
            },
            "one_step__extrema__value__max__value": {
                "question": [
                    f"What is the highest {heatmap_category['singular']} in this heatmap?",
                    f"What is the largest {heatmap_category['singular']} in this heatmap?",
                    f"What is the maximum {heatmap_category['singular']} shown in this heatmap?",
                    f"Among all the {heatmap_category['plural']} in this heatmap, what is the highest one?",
                    f"Among all the {heatmap_category['plural']} in this heatmap, what is the largest one?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read all the {heatmap_category['plural']} in this heatmap.",
                        "step_2": f"Second, I need to compare them to find the highest {heatmap_category['singular']}.",
                    },
                ],
                "constraint": None,
                "answer": max_value,
                "mask": {
                    "step_1": all_cell_indices,
                    "step_2": [(max_pos[0], max_pos[1])],
                    "answer": [(max_pos[0], max_pos[1])],
                },
            },
            "one_step__extrema__value__min__position": {
                "question": [
                    f"What is the position (row, column) of the cell with the lowest {heatmap_category['singular']} in this heatmap?",
                    f"Which cell has the lowest {heatmap_category['singular']} in this heatmap? Please provide the {y_axis_title} and {x_axis_title}.",
                    f"What is the location of the minimum {heatmap_category['singular']} in this heatmap?",
                    f"Which {y_axis_title} and {x_axis_title} correspond to the lowest {heatmap_category['singular']}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read all the {heatmap_category['plural']} in this heatmap.",
                        "step_2": f"Second, I need to compare them to find the cell with the lowest {heatmap_category['singular']}.",
                        "step_3": f"Third, I need to identify the position of this cell.",
                    },
                ],
                "constraint": None,
                "answer": min_label_answer,
                "mask": {
                    "step_1": all_cell_indices,
                    "step_2": [(min_pos[0], min_pos[1])],
                    "step_3": [(min_pos[0], min_pos[1])],
                    "answer": [(min_pos[0], min_pos[1])],
                },
            },
            "one_step__extrema__value__max__position": {
                "question": [
                    f"What is the position (row, column) of the cell with the highest {heatmap_category['singular']} in this heatmap?",
                    f"Which cell has the highest {heatmap_category['singular']} in this heatmap? Please provide the {y_axis_title} and {x_axis_title}.",
                    f"What is the location of the maximum {heatmap_category['singular']} in this heatmap?",
                    f"Which {y_axis_title} and {x_axis_title} correspond to the highest {heatmap_category['singular']}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read all the {heatmap_category['plural']} in this heatmap.",
                        "step_2": f"Second, I need to compare them to find the cell with the highest {heatmap_category['singular']}.",
                        "step_3": f"Third, I need to identify the position of this cell.",
                    },
                ],
                "constraint": None,
                "answer": max_label_answer,
                "mask": {
                    "step_1": all_cell_indices,
                    "step_2": [(max_pos[0], max_pos[1])],
                    "step_3": [(max_pos[0], max_pos[1])],
                    "answer": [(max_pos[0], max_pos[1])],
                },
            },
        }

        return easy_qa_pool

    def _one_step_sort(self, chart_metadata: Dict):
        """
        Sort: ascending and descending
        """
        x_axis_title = chart_metadata['x_label'].lower()
        y_axis_title = chart_metadata['y_label'].lower()
        heatmap_category = copy.deepcopy(chart_metadata["heatmap_category"])
        target_row_data = copy.deepcopy(chart_metadata["heatmap_data"])  # matrix
        target_column_data = [list(column_list) for column_list in zip(*target_row_data)]
        target_x_labels = copy.deepcopy(chart_metadata["x_labels"])
        target_y_labels = copy.deepcopy(chart_metadata["y_labels"])

        # Calculate row sums and column sums for sorting
        row_sum = self._compute_matrix_row_sum(target_row_data)
        column_sum = self._compute_matrix_column_sum(target_row_data)

        # GT sort - rows by their sum
        sort_rows_ascending = self._sort_y_order_for_x(row_sum, target_y_labels, "ascending")
        sort_rows_descending = self._sort_y_order_for_x(row_sum, target_y_labels, "descending")

        # GT sort - columns by their sum
        sort_columns_ascending = self._sort_y_order_for_x(column_sum, target_x_labels, "ascending")
        sort_columns_descending = self._sort_y_order_for_x(column_sum, target_x_labels, "descending")

        # All cell indices for masking
        all_cell_indices = []
        for row_idx in range(len(target_y_labels)):
            for col_idx in range(len(target_x_labels)):
                all_cell_indices.append((row_idx, col_idx))

        # Chart QA Pool
        easy_qa_pool = {
            "one_step__sort__rows__ascending": {
                "question": [
                    f"If sorting all the {y_axis_title} in ascending order according to their total {heatmap_category['singular']}, can you help provide their sorted sequence separated with commas?",
                    f"If sorting all the rows in ascending order according to their sum of {heatmap_category['plural']}, can you help provide the sorted sequence of {y_axis_title} separated with commas?",
                    f"Please sort all the {y_axis_title} in ascending order according to their total {heatmap_category['singular']}, and provide their sorted sequence separated with commas.",
                    f"Can you help sort all the {y_axis_title} according to their sum of {heatmap_category['plural']} from low to high, and provide their sorted sequence separated with commas?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read all the {heatmap_category['plural']} in this heatmap.",
                        "step_2": f"Second, I need to calculate the sum of {heatmap_category['plural']} for each {y_axis_title}.",
                        "step_3": f"Third, I need to sort the {y_axis_title} in ascending order according to their sums.",
                    },
                ],
                "constraint": None,
                "answer": sort_rows_ascending,
                "mask": {
                    "step_1": all_cell_indices,
                    "step_2": all_cell_indices,
                    "step_3": all_cell_indices,
                    "answer": all_cell_indices,
                },
            },
            "one_step__sort__rows__descending": {
                "question": [
                    f"If sorting all the {y_axis_title} in descending order according to their total {heatmap_category['singular']}, can you help provide their sorted sequence separated with commas?",
                    f"If sorting all the rows in descending order according to their sum of {heatmap_category['plural']}, can you help provide the sorted sequence of {y_axis_title} separated with commas?",
                    f"Please sort all the {y_axis_title} in descending order according to their total {heatmap_category['singular']}, and provide their sorted sequence separated with commas.",
                    f"Can you help sort all the {y_axis_title} according to their sum of {heatmap_category['plural']} from high to low, and provide their sorted sequence separated with commas?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read all the {heatmap_category['plural']} in this heatmap.",
                        "step_2": f"Second, I need to calculate the sum of {heatmap_category['plural']} for each {y_axis_title}.",
                        "step_3": f"Third, I need to sort the {y_axis_title} in descending order according to their sums.",
                    },
                ],
                "constraint": None,
                "answer": sort_rows_descending,
                "mask": {
                    "step_1": all_cell_indices,
                    "step_2": all_cell_indices,
                    "step_3": all_cell_indices,
                    "answer": all_cell_indices,
                },
            },
            "one_step__sort__columns__ascending": {
                "question": [
                    f"If sorting all the {x_axis_title} in ascending order according to their total {heatmap_category['singular']}, can you help provide their sorted sequence separated with commas?",
                    f"If sorting all the columns in ascending order according to their sum of {heatmap_category['plural']}, can you help provide the sorted sequence of {x_axis_title} separated with commas?",
                    f"Please sort all the {x_axis_title} in ascending order according to their total {heatmap_category['singular']}, and provide their sorted sequence separated with commas.",
                    f"Can you help sort all the {x_axis_title} according to their sum of {heatmap_category['plural']} from low to high, and provide their sorted sequence separated with commas?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read all the {heatmap_category['plural']} in this heatmap.",
                        "step_2": f"Second, I need to calculate the sum of {heatmap_category['plural']} for each {x_axis_title}.",
                        "step_3": f"Third, I need to sort the {x_axis_title} in ascending order according to their sums.",
                    },
                ],
                "constraint": None,
                "answer": sort_columns_ascending,
                "mask": {
                    "step_1": all_cell_indices,
                    "step_2": all_cell_indices,
                    "step_3": all_cell_indices,
                    "answer": all_cell_indices,
                },
            },
            "one_step__sort__columns__descending": {
                "question": [
                    f"If sorting all the {x_axis_title} in descending order according to their total {heatmap_category['singular']}, can you help provide their sorted sequence separated with commas?",
                    f"If sorting all the columns in descending order according to their sum of {heatmap_category['plural']}, can you help provide the sorted sequence of {x_axis_title} separated with commas?",
                    f"Please sort all the {x_axis_title} in descending order according to their total {heatmap_category['singular']}, and provide their sorted sequence separated with commas.",
                    f"Can you help sort all the {x_axis_title} according to their sum of {heatmap_category['plural']} from high to low, and provide their sorted sequence separated with commas?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read all the {heatmap_category['plural']} in this heatmap.",
                        "step_2": f"Second, I need to calculate the sum of {heatmap_category['plural']} for each {x_axis_title}.",
                        "step_3": f"Third, I need to sort the {x_axis_title} in descending order according to their sums.",
                    },
                ],
                "constraint": None,
                "answer": sort_columns_descending,
                "mask": {
                    "step_1": all_cell_indices,
                    "step_2": all_cell_indices,
                    "step_3": all_cell_indices,
                    "answer": all_cell_indices,
                },
            },
        }

        return easy_qa_pool

    def _one_step_read(self, chart_metadata: Dict):
        """
        Read: value, label
        """
        x_axis_title = chart_metadata['x_label'].lower()
        y_axis_title = chart_metadata['y_label'].lower()
        heatmap_category = copy.deepcopy(chart_metadata["heatmap_category"])
        target_row_data = copy.deepcopy(chart_metadata["heatmap_data"])  # matrix
        target_column_data = [list(column_list) for column_list in zip(*target_row_data)]
        target_x_labels = copy.deepcopy(chart_metadata["x_labels"])
        target_y_labels = copy.deepcopy(chart_metadata["y_labels"])

        # Chart QA Pool
        easy_qa_pool = {}

        # Generate read questions for each cell
        for row_idx in range(len(target_y_labels)):
            for col_idx in range(len(target_x_labels)):
                gt_cell_value = target_row_data[row_idx][col_idx]
                gt_row_label = target_y_labels[row_idx]
                gt_col_label = target_x_labels[col_idx]
                
                # (1) Read - Value from position
                easy_qa_pool[f"one_step__read__value__row_{row_idx+1}_col_{col_idx+1}"] = {
                    "question": [
                        f"What is the {heatmap_category['singular']} for {gt_row_label} and {gt_col_label}?",
                        f"What is the value in the cell corresponding to {gt_row_label} and {gt_col_label}?",
                        f"What is the {heatmap_category['singular']} at the intersection of {gt_row_label} and {gt_col_label}?",
                        f"Can you tell me the {heatmap_category['singular']} for the cell at {gt_row_label}, {gt_col_label}?",
                    ],
                    "reasoning": [
                        {
                            "step_1": f"First, I need to locate the cell at the intersection of {gt_row_label} and {gt_col_label}.",
                            "step_2": f"Second, I need to read the {heatmap_category['singular']} in this cell.",
                        },
                    ],
                    "constraint": None,
                    "answer": gt_cell_value,
                    "mask": {
                        "step_1": [(row_idx, col_idx)],
                        "step_2": [(row_idx, col_idx)],
                        "answer": [(row_idx, col_idx)],
                    },
                }

                # (2) Read - Position from value (only for cells with unique values)
                # Check if this value is unique in the heatmap
                all_values = [val for row in target_row_data for val in row]
                if all_values.count(gt_cell_value) == 1:
                    easy_qa_pool[f"one_step__read__position__value_{gt_cell_value}"] = {
                        "question": [
                            f"Which cell has the {heatmap_category['singular']} of {gt_cell_value}? Please provide the {y_axis_title} and {x_axis_title}.",
                            f"What is the position of the cell with {heatmap_category['singular']} equal to {gt_cell_value}?",
                            f"Which {y_axis_title} and {x_axis_title} correspond to the {heatmap_category['singular']} of {gt_cell_value}?",
                            f"Can you tell me the location of the cell that has {heatmap_category['singular']} {gt_cell_value}?",
                        ],
                        "reasoning": [
                            {
                                "step_1": f"First, I need to find the cell with {heatmap_category['singular']} equal to {gt_cell_value}.",
                                "step_2": f"Second, I need to identify the position of this cell.",
                            },
                        ],
                        "constraint": None,
                        "answer": f"{gt_row_label}, {gt_col_label}",
                        "mask": {
                            "step_1": [(row_idx, col_idx)],
                            "step_2": [(row_idx, col_idx)],
                            "answer": [(row_idx, col_idx)],
                        },
                    }

        return easy_qa_pool


    ############################################################
    #                     Two-step Operator
    ############################################################

    def _two_step_statistics(self, chart_metadata: Dict, target_row_indices: List, constraint: str):
        """
        Statistics: sum, mean, median, count
        """
        x_axis_title = chart_metadata['x_label'].lower()
        y_axis_title = chart_metadata['y_label'].lower()
        heatmap_category = copy.deepcopy(chart_metadata["heatmap_category"])
        target_row_data = [chart_metadata["heatmap_data"][kk] for kk in target_row_indices]  # matrix
        target_column_data = [list(column_list) for column_list in zip(*target_row_data)]
        target_x_labels = copy.deepcopy(chart_metadata["x_labels"])
        target_y_labels = [chart_metadata["y_labels"][kk] for kk in target_row_indices]
        target_heatmap_indices = [x_idx for x_idx in range(len(target_x_labels))]

        # Sum
        row_sum = self._compute_matrix_row_sum(target_row_data)
        column_sum = self._compute_matrix_column_sum(target_row_data)
        total_sum = sum([sum(row) for row in target_row_data])
        
        # Mean
        total_cells = len(target_y_labels) * len(target_x_labels)
        overall_mean = total_sum / total_cells
        row_mean = [curr_sum / len(target_heatmap_indices) for curr_sum in row_sum]
        column_mean = [curr_sum / len(target_y_labels) for curr_sum in column_sum]

        # Median
        all_values = [val for row in target_row_data for val in row]
        overall_median_value, overall_median_indices = self._compute_data_median(all_values)
        
        row_median_value, row_median_indices = [], []
        for kth_row_data_list in target_row_data:
            kth_row_median_value, kth_row_median_indices = self._compute_data_median(kth_row_data_list)
            row_median_value.append(kth_row_median_value)
            row_median_indices.append(kth_row_median_indices)

        column_median_value, column_median_indices = [], []
        for kth_column_data_list in target_column_data:
            kth_column_median_value, kth_column_median_indices = self._compute_data_median(kth_column_data_list)
            column_median_value.append(kth_column_median_value)
            column_median_indices.append(kth_column_median_indices)

        # Count
        count_row_num = len(target_y_labels)
        count_column_num = len(target_x_labels)
        count_total_cells = count_row_num * count_column_num

        # Target cell indices for masking
        target_cell_indices = []
        for i, row_idx in enumerate(target_row_indices):
            for col_idx in range(len(target_x_labels)):
                target_cell_indices.append((row_idx, col_idx))

        # Chart QA Pool
        medium_qa_pool = {
            "two_step__statistics__sum_total": {
                "question": [
                    f"What is the total sum of {heatmap_category['plural']} for cells {constraint}?",
                    f"For cells {constraint}, what is the sum of their {heatmap_category['plural']}?",
                    f"Can you help calculate the sum of {heatmap_category['plural']} for cells {constraint}?",
                    f"Please compute the sum of {heatmap_category['plural']} for cells {constraint}.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to identify the cells {constraint}.",
                        "step_2": f"Second, I need to calculate their total sum of {heatmap_category['plural']}.",
                    },
                ],
                "constraint": constraint,
                "answer": total_sum,
                "mask": {
                    "step_1": target_cell_indices,
                    "step_2": target_cell_indices,
                    "answer": target_cell_indices,
                },
            },
            "two_step__statistics__mean_total": {
                "question": [
                    f"What is the mean {heatmap_category['singular']} for cells {constraint}? Please round to two decimal places.",
                    f"For cells {constraint}, what is their mean {heatmap_category['singular']}? Please round to two decimal places.",
                    f"Can you help calculate the mean {heatmap_category['singular']} for cells {constraint}? Please round to two decimal places.",
                    f"Please compute the mean {heatmap_category['singular']} for cells {constraint}. Please round to two decimal places.",
                    f"What is the average {heatmap_category['singular']} for cells {constraint}? Please round to two decimal places.",
                    f"For cells {constraint}, what is their average {heatmap_category['singular']}? Please round to two decimal places.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to identify the cells {constraint}.",
                        "step_2": f"Second, I need to calculate their average {heatmap_category['singular']}.",
                    },
                ],
                "constraint": constraint,
                "answer": overall_mean,
                "mask": {
                    "step_1": target_cell_indices,
                    "step_2": target_cell_indices,
                    "answer": target_cell_indices,
                },
            },
            "two_step__statistics__median_total": {
                "question": [
                    f"What is the median {heatmap_category['singular']} for cells {constraint}?",
                    f"For cells {constraint}, what is the median of their {heatmap_category['plural']}?",
                    f"Can you help calculate the median {heatmap_category['singular']} for cells {constraint}?",
                    f"Please compute the median {heatmap_category['singular']} for cells {constraint}.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to identify the cells {constraint}.",
                        "step_2": f"Second, I need to calculate their median {heatmap_category['singular']}.",
                    },
                ],
                "constraint": constraint,
                "answer": overall_median_value,
                "mask": {
                    "step_1": target_cell_indices,
                    "step_2": target_cell_indices,
                    "answer": target_cell_indices,
                },
            },
            "two_step__statistics__count_total": {
                "question": [
                    f"How many cells {constraint} are shown in this heatmap?",
                    f"What is the number of cells {constraint}?",
                    f"Please help count the number of cells {constraint}.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to find all the cells {constraint}.",
                        "step_2": f"Second, I need to count the total number of these cells.",
                    },
                ],
                "constraint": constraint,
                "answer": count_total_cells,
                "mask": {
                    "step_1": target_cell_indices,
                    "step_2": target_cell_indices,
                    "answer": target_cell_indices,
                },
            },
        }

        return medium_qa_pool

    def _two_step_extrema(self, chart_metadata: Dict, target_row_indices: List, constraint: str):
        """
        Extrema: value (min, max), pos (left, right, top, bottom)
        """
        x_axis_title = chart_metadata['x_label'].lower()
        y_axis_title = chart_metadata['y_label'].lower()
        heatmap_category = copy.deepcopy(chart_metadata["heatmap_category"])
        target_row_data = [chart_metadata["heatmap_data"][kk] for kk in target_row_indices]  # matrix
        target_column_data = [list(column_list) for column_list in zip(*target_row_data)]
        target_x_labels = copy.deepcopy(chart_metadata["x_labels"])
        target_y_labels = [chart_metadata["y_labels"][kk] for kk in target_row_indices]

        # Value: Min & Max
        extrema_dict = self._find_matrix_extrema_with_pos(target_row_data)
        min_value, min_pos = extrema_dict["min_value"], extrema_dict["min_pos"]
        # Adjust min_pos to original indices
        original_min_row_idx = target_row_indices[min_pos[0]]
        min_label_answer = f"{chart_metadata['y_labels'][original_min_row_idx]}, {target_x_labels[min_pos[1]]}"
        
        max_value, max_pos = extrema_dict["max_value"], extrema_dict["max_pos"]
        # Adjust max_pos to original indices
        original_max_row_idx = target_row_indices[max_pos[0]]
        max_label_answer = f"{chart_metadata['y_labels'][original_max_row_idx]}, {target_x_labels[max_pos[1]]}"

        # Target cell indices for masking
        target_cell_indices = []
        for i, row_idx in enumerate(target_row_indices):
            for col_idx in range(len(target_x_labels)):
                target_cell_indices.append((row_idx, col_idx))

        # Chart QA Pool
        medium_qa_pool = {
            "two_step__extrema__value__min__value": {
                "question": [
                    f"What is the lowest {heatmap_category['singular']} among cells {constraint}?",
                    f"What is the smallest {heatmap_category['singular']} among cells {constraint}?",
                    f"Among cells {constraint}, what is the lowest {heatmap_category['singular']}?",
                    f"Among cells {constraint}, what is the smallest {heatmap_category['singular']}?",
                    f"What is the minimum {heatmap_category['singular']} for cells {constraint}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to find all the cells {constraint}.",
                        "step_2": f"Second, I need to compare their {heatmap_category['plural']} to find the lowest one.",
                    },
                ],
                "constraint": constraint,
                "answer": min_value,
                "mask": {
                    "step_1": target_cell_indices,
                    "step_2": [(original_min_row_idx, min_pos[1])],
                    "answer": [(original_min_row_idx, min_pos[1])],
                },
            },
            "two_step__extrema__value__max__value": {
                "question": [
                    f"What is the highest {heatmap_category['singular']} among cells {constraint}?",
                    f"What is the largest {heatmap_category['singular']} among cells {constraint}?",
                    f"Among cells {constraint}, what is the highest {heatmap_category['singular']}?",
                    f"Among cells {constraint}, what is the largest {heatmap_category['singular']}?",
                    f"What is the maximum {heatmap_category['singular']} for cells {constraint}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to find all the cells {constraint}.",
                        "step_2": f"Second, I need to compare their {heatmap_category['plural']} to find the highest one.",
                    },
                ],
                "constraint": constraint,
                "answer": max_value,
                "mask": {
                    "step_1": target_cell_indices,
                    "step_2": [(original_max_row_idx, max_pos[1])],
                    "answer": [(original_max_row_idx, max_pos[1])],
                },
            },
            "two_step__extrema__value__min__position": {
                "question": [
                    f"What is the position of the cell with the lowest {heatmap_category['singular']} among cells {constraint}?",
                    f"Which cell has the lowest {heatmap_category['singular']} among cells {constraint}? Please provide the {y_axis_title} and {x_axis_title}.",
                    f"Among cells {constraint}, what is the location of the minimum {heatmap_category['singular']}?",
                    f"Which {y_axis_title} and {x_axis_title} correspond to the lowest {heatmap_category['singular']} among cells {constraint}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to find all the cells {constraint}.",
                        "step_2": f"Second, I need to compare their {heatmap_category['plural']} to find the cell with the lowest {heatmap_category['singular']}.",
                        "step_3": f"Third, I need to identify the position of this cell.",
                    },
                ],
                "constraint": constraint,
                "answer": min_label_answer,
                "mask": {
                    "step_1": target_cell_indices,
                    "step_2": [(original_min_row_idx, min_pos[1])],
                    "step_3": [(original_min_row_idx, min_pos[1])],
                    "answer": [(original_min_row_idx, min_pos[1])],
                },
            },
            "two_step__extrema__value__max__position": {
                "question": [
                    f"What is the position of the cell with the highest {heatmap_category['singular']} among cells {constraint}?",
                    f"Which cell has the highest {heatmap_category['singular']} among cells {constraint}? Please provide the {y_axis_title} and {x_axis_title}.",
                    f"Among cells {constraint}, what is the location of the maximum {heatmap_category['singular']}?",
                    f"Which {y_axis_title} and {x_axis_title} correspond to the highest {heatmap_category['singular']} among cells {constraint}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to find all the cells {constraint}.",
                        "step_2": f"Second, I need to compare their {heatmap_category['plural']} to find the cell with the highest {heatmap_category['singular']}.",
                        "step_3": f"Third, I need to identify the position of this cell.",
                    },
                ],
                "constraint": constraint,
                "answer": max_label_answer,
                "mask": {
                    "step_1": target_cell_indices,
                    "step_2": [(original_max_row_idx, max_pos[1])],
                    "step_3": [(original_max_row_idx, max_pos[1])],
                    "answer": [(original_max_row_idx, max_pos[1])],
                },
            },
        }

        return medium_qa_pool

    def _two_step_compare_two_heatmap_cells(self, chart_metadata: Dict, target_cell_positions: List):
        """
        Compare: value, pos
        """
        assert len(target_cell_positions) == 2 and target_cell_positions[0] != target_cell_positions[1]

        x_axis_title = chart_metadata['x_label'].lower()
        y_axis_title = chart_metadata['y_label'].lower()
        heatmap_category = copy.deepcopy(chart_metadata["heatmap_category"])
        target_row_data = copy.deepcopy(chart_metadata["heatmap_data"])  # matrix
        target_x_labels = copy.deepcopy(chart_metadata["x_labels"])
        target_y_labels = copy.deepcopy(chart_metadata["y_labels"])

        # Extract the two cells' data
        pos1, pos2 = target_cell_positions[0], target_cell_positions[1]
        row1, col1 = pos1[0], pos1[1]
        row2, col2 = pos2[0], pos2[1]
        
        target_cell_values = [target_row_data[row1][col1], target_row_data[row2][col2]]
        target_cell_labels = [f"{target_y_labels[row1]}, {target_x_labels[col1]}", 
                            f"{target_y_labels[row2]}, {target_x_labels[col2]}"]

        # GT answer & mask

        # (1) Value - higher
        if target_cell_values[0] > target_cell_values[1]:
            gt_answer_value_higher = target_cell_labels[0]
            gt_mask_value_higher = [target_cell_positions[0]]
            gt_symbol_value_higher = ">"
        elif target_cell_values[0] < target_cell_values[1]:
            gt_answer_value_higher = target_cell_labels[1]
            gt_mask_value_higher = [target_cell_positions[1]]
            gt_symbol_value_higher = "<"
        elif target_cell_values[0] == target_cell_values[1]:
            gt_answer_value_higher = f"They have the same {heatmap_category['singular']}."
            gt_mask_value_higher = copy.deepcopy(target_cell_positions)
            gt_symbol_value_higher = "="

        # (2) Value - lower
        if target_cell_values[0] < target_cell_values[1]:
            gt_answer_value_lower = target_cell_labels[0]
            gt_mask_value_lower = [target_cell_positions[0]]
            gt_symbol_value_lower = "<"
        elif target_cell_values[0] > target_cell_values[1]:
            gt_answer_value_lower = target_cell_labels[1]
            gt_mask_value_lower = [target_cell_positions[1]]
            gt_symbol_value_lower = ">"
        elif target_cell_values[0] == target_cell_values[1]:
            gt_answer_value_lower = f"They have the same {heatmap_category['singular']}."
            gt_mask_value_lower = copy.deepcopy(target_cell_positions)
            gt_symbol_value_lower = "="

        # (3) Value - diff
        gt_answer_value_diff = abs(target_cell_values[0] - target_cell_values[1])

        # Chart QA Pool
        medium_qa_pool = {
            f"two_step__compare__value__cell{pos1[0]+1}_{pos1[1]+1}_vs_cell{pos2[0]+1}_{pos2[1]+1}__higher": {
                "question": [
                    f"Comparing between the cell at {target_cell_labels[0]} and the cell at {target_cell_labels[1]}, which has a higher {heatmap_category['singular']}?",
                    f"Comparing between the cell at {target_cell_labels[0]} and the cell at {target_cell_labels[1]}, which has a larger {heatmap_category['singular']}?",
                    f"Between the cells at {target_cell_labels[0]} and {target_cell_labels[1]}, which one has the higher {heatmap_category['singular']}?",
                    f"Which cell has a higher {heatmap_category['singular']}: {target_cell_labels[0]} or {target_cell_labels[1]}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read their {heatmap_category['plural']}:\n- {target_cell_labels[0]}: {target_cell_values[0]}\n- {target_cell_labels[1]}: {target_cell_values[1]}",
                        "step_2": f"Second, I need to compare their {heatmap_category['plural']} to find the one with a higher {heatmap_category['singular']}:\n{target_cell_labels[0]}: {target_cell_values[0]} {gt_symbol_value_higher} {target_cell_labels[1]}: {target_cell_values[1]}",
                    },
                ],
                "constraint": target_cell_positions,
                "answer": gt_answer_value_higher,
                "mask": {
                    "step_1": target_cell_positions,
                    "step_2": gt_mask_value_higher,
                    "answer": gt_mask_value_higher,
                },
            },
            f"two_step__compare__value__cell{pos1[0]+1}_{pos1[1]+1}_vs_cell{pos2[0]+1}_{pos2[1]+1}__lower": {
                "question": [
                    f"Comparing between the cell at {target_cell_labels[0]} and the cell at {target_cell_labels[1]}, which has a lower {heatmap_category['singular']}?",
                    f"Comparing between the cell at {target_cell_labels[0]} and the cell at {target_cell_labels[1]}, which has a smaller {heatmap_category['singular']}?",
                    f"Between the cells at {target_cell_labels[0]} and {target_cell_labels[1]}, which one has the lower {heatmap_category['singular']}?",
                    f"Which cell has a lower {heatmap_category['singular']}: {target_cell_labels[0]} or {target_cell_labels[1]}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read their {heatmap_category['plural']}:\n- {target_cell_labels[0]}: {target_cell_values[0]}\n- {target_cell_labels[1]}: {target_cell_values[1]}",
                        "step_2": f"Second, I need to compare their {heatmap_category['plural']} to find the one with a lower {heatmap_category['singular']}:\n{target_cell_values[0]} {gt_symbol_value_lower} {target_cell_values[1]}",
                    },
                ],
                "constraint": target_cell_positions,
                "answer": gt_answer_value_lower,
                "mask": {
                    "step_1": target_cell_positions,
                    "step_2": gt_mask_value_lower,
                    "answer": gt_mask_value_lower,
                },
            },
            f"two_step__compare__value__cell{pos1[0]+1}_{pos1[1]+1}_vs_cell{pos2[0]+1}_{pos2[1]+1}__diff": {
                "question": [
                    f"What is the absolute difference in {heatmap_category['singular']} between the cell at {target_cell_labels[0]} and the cell at {target_cell_labels[1]}?",
                    f"What is the absolute value of the difference in {heatmap_category['singular']} between the cells at {target_cell_labels[0]} and {target_cell_labels[1]}?",
                    f"Comparing the cells at {target_cell_labels[0]} and {target_cell_labels[1]}, what is their absolute difference in {heatmap_category['singular']}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read their {heatmap_category['plural']}:\n- {target_cell_labels[0]}: {target_cell_values[0]}\n- {target_cell_labels[1]}: {target_cell_values[1]}",
                        "step_2": f"Second, I need to calculate their absolute difference in {heatmap_category['singular']}:\n|{target_cell_values[0]} - {target_cell_values[1]}| = {gt_answer_value_diff}",
                    },
                ],
                "constraint": target_cell_positions,
                "answer": gt_answer_value_diff,
                "mask": {
                    "step_1": target_cell_positions,
                    "step_2": target_cell_positions,
                    "answer": target_cell_positions,
                },
            },
        }

        return medium_qa_pool

    def _two_step_sort(self, chart_metadata: Dict, target_row_indices: List, constraint: str):
        """
        Sort: ascending and descending
        """
        x_axis_title = chart_metadata['x_label'].lower()
        y_axis_title = chart_metadata['y_label'].lower()
        heatmap_category = copy.deepcopy(chart_metadata["heatmap_category"])
        target_row_data = [chart_metadata["heatmap_data"][kk] for kk in target_row_indices]  # matrix
        target_column_data = [list(column_list) for column_list in zip(*target_row_data)]
        target_x_labels = copy.deepcopy(chart_metadata["x_labels"])
        target_y_labels = [chart_metadata["y_labels"][kk] for kk in target_row_indices]

        # Calculate row sums and column sums for sorting
        row_sum = self._compute_matrix_row_sum(target_row_data)
        column_sum = self._compute_matrix_column_sum(target_row_data)

        # GT sort - rows by their sum
        sort_rows_ascending = self._sort_y_order_for_x(row_sum, target_y_labels, "ascending")
        sort_rows_descending = self._sort_y_order_for_x(row_sum, target_y_labels, "descending")

        # GT sort - columns by their sum
        sort_columns_ascending = self._sort_y_order_for_x(column_sum, target_x_labels, "ascending")
        sort_columns_descending = self._sort_y_order_for_x(column_sum, target_x_labels, "descending")

        # Target cell indices for masking
        target_cell_indices = []
        for i, row_idx in enumerate(target_row_indices):
            for col_idx in range(len(target_x_labels)):
                target_cell_indices.append((row_idx, col_idx))

        # Reasoning
        read_rows, read_columns = "", ""
        for i, row_sum_val in enumerate(row_sum):
            read_rows += f"\n- {target_y_labels[i]}: {row_sum_val}"
        for i, col_sum_val in enumerate(column_sum):
            read_columns += f"\n- {target_x_labels[i]}: {col_sum_val}"

        # Chart QA Pool
        medium_qa_pool = {
            "two_step__sort__rows__ascending": {
                "question": [
                    f"If sorting the {y_axis_title} {constraint} in ascending order according to their total {heatmap_category['singular']}, can you help provide their sorted sequence separated with commas?",
                    f"If sorting the rows {constraint} in ascending order according to their sum of {heatmap_category['plural']}, can you help provide the sorted sequence of {y_axis_title} separated with commas?",
                    f"Please sort the {y_axis_title} {constraint} in ascending order according to their total {heatmap_category['singular']}, and provide their sorted sequence separated with commas.",
                    f"Can you help sort the {y_axis_title} {constraint} according to their sum of {heatmap_category['plural']} from low to high, and provide their sorted sequence separated with commas?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to identify the {y_axis_title} {constraint}.",
                        "step_2": f"Second, I need to calculate the sum of {heatmap_category['plural']} for each of these {y_axis_title}:{read_rows}",
                        "step_3": f"Third, I need to sort them in ascending order according to their sums.",
                    },
                ],
                "constraint": constraint,
                "answer": sort_rows_ascending,
                "mask": {
                    "step_1": target_cell_indices,
                    "step_2": target_cell_indices,
                    "step_3": target_cell_indices,
                    "answer": target_cell_indices,
                },
            },
            "two_step__sort__columns__ascending": {
                "question": [
                    f"If sorting the {x_axis_title} for cells {constraint} in ascending order according to their total {heatmap_category['singular']}, can you help provide their sorted sequence separated with commas?",
                    f"If sorting the columns for cells {constraint} in ascending order according to their sum of {heatmap_category['plural']}, can you help provide the sorted sequence of {x_axis_title} separated with commas?",
                    f"Please sort the {x_axis_title} for cells {constraint} in ascending order according to their total {heatmap_category['singular']}, and provide their sorted sequence separated with commas.",
                    f"Can you help sort the {x_axis_title} for cells {constraint} according to their sum of {heatmap_category['plural']} from low to high, and provide their sorted sequence separated with commas?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to identify the cells {constraint}.",
                        "step_2": f"Second, I need to calculate the sum of {heatmap_category['plural']} for each {x_axis_title} within these cells:{read_columns}",
                        "step_3": f"Third, I need to sort the {x_axis_title} in ascending order according to their sums.",
                    },
                ],
                "constraint": constraint,
                "answer": sort_columns_ascending,
                "mask": {
                    "step_1": target_cell_indices,
                    "step_2": target_cell_indices,
                    "step_3": target_cell_indices,
                    "answer": target_cell_indices,
                },
            },
            "two_step__sort__columns__descending": {
                "question": [
                    f"If sorting the {x_axis_title} for cells {constraint} in descending order according to their total {heatmap_category['singular']}, can you help provide their sorted sequence separated with commas?",
                    f"If sorting the columns for cells {constraint} in descending order according to their sum of {heatmap_category['plural']}, can you help provide the sorted sequence of {x_axis_title} separated with commas?",
                    f"Please sort the {x_axis_title} for cells {constraint} in descending order according to their total {heatmap_category['singular']}, and provide their sorted sequence separated with commas.",
                    f"Can you help sort the {x_axis_title} for cells {constraint} according to their sum of {heatmap_category['plural']} from high to low, and provide their sorted sequence separated with commas?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to identify the cells {constraint}.",
                        "step_2": f"Second, I need to calculate the sum of {heatmap_category['plural']} for each {x_axis_title} within these cells:{read_columns}",
                        "step_3": f"Third, I need to sort the {x_axis_title} in descending order according to their sums.",
                    },
                ],
                "constraint": constraint,
                "answer": sort_columns_descending,
                "mask": {
                    "step_1": target_cell_indices,
                    "step_2": target_cell_indices,
                    "step_3": target_cell_indices,
                    "answer": target_cell_indices,
                },
            },
        }

        return medium_qa_pool

    def _two_step_filter(self, chart_metadata: Dict, condition: List = [2, 5]):
        """
        Filter condition: above or below a specific heatmap cell's value
        condition: the condition-th highest/lowest heatmap cell
        """
        x_axis_title = chart_metadata['x_label'].lower()
        y_axis_title = chart_metadata['y_label'].lower()
        heatmap_category = copy.deepcopy(chart_metadata["heatmap_category"])
        target_row_data = copy.deepcopy(chart_metadata["heatmap_data"])  # matrix
        target_column_data = [list(column_list) for column_list in zip(*target_row_data)]
        target_x_labels = copy.deepcopy(chart_metadata["x_labels"])
        target_y_labels = copy.deepcopy(chart_metadata["y_labels"])
        
        # Create a flat list of all values with their positions
        all_values_with_pos = []
        for row_idx in range(len(target_y_labels)):
            for col_idx in range(len(target_x_labels)):
                all_values_with_pos.append({
                    'value': target_row_data[row_idx][col_idx],
                    'position': (row_idx, col_idx),
                    'label': f"{target_y_labels[row_idx]}, {target_x_labels[col_idx]}"
                })
        
        # All cell indices for reference
        all_cell_indices = [(row_idx, col_idx) for row_idx in range(len(target_y_labels)) for col_idx in range(len(target_x_labels))]
        
        # Reasoning
        read_all = ""
        for row_idx in range(len(target_y_labels)):
            for col_idx in range(len(target_x_labels)):
                read_all += f"\n- {target_y_labels[row_idx]}, {target_x_labels[col_idx]}: {target_row_data[row_idx][col_idx]}"

        # Filter
        medium_qa_pool = {}
        for kth in range(condition[0], condition[1]):
            # kth highest
            kth_highest_values = sorted(set([item['value'] for item in all_values_with_pos]), reverse=True)
            if kth <= len(kth_highest_values):
                kth_highest_value = kth_highest_values[kth-1]
                kth_highest_cells = [item for item in all_values_with_pos if item['value'] == kth_highest_value]
                kth_highest_positions = [item['position'] for item in kth_highest_cells]
                kth_highest_labels = [item['label'] for item in kth_highest_cells]
                kth_highest_answer = ", ".join(kth_highest_labels)

                # kth highest - label
                medium_qa_pool[f"two_step__filter__{self._convert_idx_to_pos(kth)}_highest__label"] = {
                    "question": [
                        f"What is the position of the cell that has the {self._convert_idx_to_pos(kth)} highest {heatmap_category['singular']}?",
                        f"Which cell has the {self._convert_idx_to_pos(kth)} highest {heatmap_category['singular']}? Please provide the {y_axis_title} and {x_axis_title}.",
                        f"What is the location of the {self._convert_idx_to_pos(kth)} highest {heatmap_category['singular']} in this heatmap?",
                        f"Which {y_axis_title} and {x_axis_title} correspond to the {self._convert_idx_to_pos(kth)} highest {heatmap_category['singular']}?",
                    ],
                    "reasoning": [
                        {
                            "step_1": f"First, I need to read the {heatmap_category['singular']} of each cell in this heatmap:{read_all}",
                            "step_2": f"Second, I need to compare them to identify the cell with the {self._convert_idx_to_pos(kth)} highest {heatmap_category['singular']}.",
                            "step_3": f"Third, I need to read its position.",
                        },
                    ],
                    "constraint": f"{self._convert_idx_to_pos(kth)} highest",
                    "answer": kth_highest_answer,
                    "mask": {
                        "step_1": all_cell_indices,
                        "step_2": kth_highest_positions,
                        "step_3": kth_highest_positions,
                        "answer": kth_highest_positions,
                    },
                }

                # kth highest - value
                medium_qa_pool[f"two_step__filter__{self._convert_idx_to_pos(kth)}_highest__value"] = {
                    "question": [
                        f"What is the {self._convert_idx_to_pos(kth)} highest {heatmap_category['singular']} in this heatmap?",
                        f"What is the value of the cell with the {self._convert_idx_to_pos(kth)} highest {heatmap_category['singular']}?",
                        f"What is the {self._convert_idx_to_pos(kth)} largest {heatmap_category['singular']} shown in this heatmap?",
                    ],
                    "reasoning": [
                        {
                            "step_1": f"First, I need to read the {heatmap_category['singular']} of each cell in this heatmap:{read_all}",
                            "step_2": f"Second, I need to compare them to identify the {self._convert_idx_to_pos(kth)} highest {heatmap_category['singular']}.",
                        },
                    ],
                    "constraint": f"{self._convert_idx_to_pos(kth)} highest",
                    "answer": kth_highest_value,
                    "mask": {
                        "step_1": all_cell_indices,
                        "step_2": kth_highest_positions,
                        "answer": kth_highest_positions,
                    },
                }

            # kth lowest
            kth_lowest_values = sorted(set([item['value'] for item in all_values_with_pos]))
            if kth <= len(kth_lowest_values):
                kth_lowest_value = kth_lowest_values[kth-1]
                kth_lowest_cells = [item for item in all_values_with_pos if item['value'] == kth_lowest_value]
                kth_lowest_positions = [item['position'] for item in kth_lowest_cells]
                kth_lowest_labels = [item['label'] for item in kth_lowest_cells]
                kth_lowest_answer = ", ".join(kth_lowest_labels)

                # kth lowest - label
                medium_qa_pool[f"two_step__filter__{self._convert_idx_to_pos(kth)}_lowest__label"] = {
                    "question": [
                        f"What is the position of the cell that has the {self._convert_idx_to_pos(kth)} lowest {heatmap_category['singular']}?",
                        f"Which cell has the {self._convert_idx_to_pos(kth)} lowest {heatmap_category['singular']}? Please provide the {y_axis_title} and {x_axis_title}.",
                        f"What is the location of the {self._convert_idx_to_pos(kth)} lowest {heatmap_category['singular']} in this heatmap?",
                        f"Which {y_axis_title} and {x_axis_title} correspond to the {self._convert_idx_to_pos(kth)} lowest {heatmap_category['singular']}?",
                    ],
                    "reasoning": [
                        {
                            "step_1": f"First, I need to read the {heatmap_category['singular']} of each cell in this heatmap:{read_all}",
                            "step_2": f"Second, I need to compare them to identify the cell with the {self._convert_idx_to_pos(kth)} lowest {heatmap_category['singular']}.",
                            "step_3": f"Third, I need to read its position.",
                        },
                    ],
                    "constraint": f"{self._convert_idx_to_pos(kth)} lowest",
                    "answer": kth_lowest_answer,
                    "mask": {
                        "step_1": all_cell_indices,
                        "step_2": kth_lowest_positions,
                        "step_3": kth_lowest_positions,
                        "answer": kth_lowest_positions,
                    },
                }

                # kth lowest - value
                medium_qa_pool[f"two_step__filter__{self._convert_idx_to_pos(kth)}_lowest__value"] = {
                    "question": [
                        f"What is the {self._convert_idx_to_pos(kth)} lowest {heatmap_category['singular']} in this heatmap?",
                        f"What is the value of the cell with the {self._convert_idx_to_pos(kth)} lowest {heatmap_category['singular']}?",
                        f"What is the {self._convert_idx_to_pos(kth)} smallest {heatmap_category['singular']} shown in this heatmap?",
                    ],
                    "reasoning": [
                        {
                            "step_1": f"First, I need to read the {heatmap_category['singular']} of each cell in this heatmap:{read_all}",
                            "step_2": f"Second, I need to compare them to identify the {self._convert_idx_to_pos(kth)} lowest {heatmap_category['singular']}.",
                        },
                    ],
                    "constraint": f"{self._convert_idx_to_pos(kth)} lowest",
                    "answer": kth_lowest_value,
                    "mask": {
                        "step_1": all_cell_indices,
                        "step_2": kth_lowest_positions,
                        "answer": kth_lowest_positions,
                    },
                }
                
        return medium_qa_pool

    def _two_step_threshold(self, chart_metadata: Dict):
        """
        Threshold: above / below mean
        """
        x_axis_title = chart_metadata['x_label'].lower()
        y_axis_title = chart_metadata['y_label'].lower()
        heatmap_category = copy.deepcopy(chart_metadata["heatmap_category"])
        target_row_data = copy.deepcopy(chart_metadata["heatmap_data"])  # matrix
        target_column_data = [list(column_list) for column_list in zip(*target_row_data)]
        target_x_labels = copy.deepcopy(chart_metadata["x_labels"])
        target_y_labels = copy.deepcopy(chart_metadata["y_labels"])
        
        # Sum
        total_sum = sum([sum(row) for row in target_row_data])

        # Mean
        total_cells = len(target_y_labels) * len(target_x_labels)
        overall_mean = total_sum / total_cells

        # Reason
        read_all = ""
        for row_idx in range(len(target_y_labels)):
            for col_idx in range(len(target_x_labels)):
                read_all += f"\n- {target_y_labels[row_idx]}, {target_x_labels[col_idx]}: {target_row_data[row_idx][col_idx]}"
        
        reason_sum = f"Sum of all {heatmap_category['plural']} = {total_sum}"
        reason_avg = f"Mean = {total_sum}/{total_cells} = {overall_mean}"

        # Above & below count
        above_mean_num, below_mean_num = 0, 0
        above_mean_positions, below_mean_positions = [], []
        
        for row_idx in range(len(target_y_labels)):
            for col_idx in range(len(target_x_labels)):
                cell_value = target_row_data[row_idx][col_idx]
                if cell_value > overall_mean:
                    above_mean_num += 1
                    above_mean_positions.append((row_idx, col_idx))
                elif cell_value < overall_mean:
                    below_mean_num += 1
                    below_mean_positions.append((row_idx, col_idx))

        # All cell indices for reference
        all_cell_indices = [(row_idx, col_idx) for row_idx in range(len(target_y_labels)) for col_idx in range(len(target_x_labels))]
        
        # Chart QA Pool
        medium_qa_pool = {
            "two_step__threshold__above_mean": {
                "question": [
                    f"How many cells have their {heatmap_category['singular']} above the average {heatmap_category['singular']} of all cells?",
                    f"Please help count the number of cells whose {heatmap_category['plural']} are above the average {heatmap_category['singular']} of all cells?",
                    f"How many cells have their {heatmap_category['singular']} above the mean {heatmap_category['singular']} of all cells?",
                    f"Please help count the number of cells whose {heatmap_category['plural']} are above the mean {heatmap_category['singular']} of all cells?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {heatmap_category['singular']} of each cell in this heatmap:{read_all}",
                        "step_2": f"Second, I need to compute the average {heatmap_category['singular']} of all cells:\n{reason_avg}",
                        "step_3": f"Third, I need to count the number of cells whose {heatmap_category['singular']} is higher than {overall_mean}.",
                    },
                ],
                "constraint": "above mean",
                "answer": above_mean_num,
                "mask": {
                    "step_1": all_cell_indices,
                    "step_2": all_cell_indices,
                    "step_3": above_mean_positions,
                    "answer": above_mean_positions,
                },
            },
            "two_step__threshold__below_mean": {
                "question": [
                    f"How many cells have their {heatmap_category['singular']} below the average {heatmap_category['singular']} of all cells?",
                    f"Please help count the number of cells whose {heatmap_category['plural']} are below the average {heatmap_category['singular']} of all cells?",
                    f"How many cells have their {heatmap_category['singular']} below the mean {heatmap_category['singular']} of all cells?",
                    f"Please help count the number of cells whose {heatmap_category['plural']} are below the mean {heatmap_category['singular']} of all cells?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {heatmap_category['singular']} of each cell in this heatmap:{read_all}",
                        "step_2": f"Second, I need to compute the average {heatmap_category['singular']} of all cells:\n{reason_avg}",
                        "step_3": f"Third, I need to count the number of cells whose {heatmap_category['singular']} is lower than {overall_mean}.",
                    },
                ],
                "constraint": "below mean",
                "answer": below_mean_num,
                "mask": {
                    "step_1": all_cell_indices,
                    "step_2": all_cell_indices,
                    "step_3": below_mean_positions,
                    "answer": below_mean_positions,
                },
            },
        }

        return medium_qa_pool


    ############################################################
    #                     Multi-step Operator
    ############################################################

    def _multi_step_threshold(self, chart_metadata: Dict):
        """
        Threshold: above / below mean, differences
        """
        x_axis_title = chart_metadata['x_label'].lower()
        y_axis_title = chart_metadata['y_label'].lower()
        heatmap_category = copy.deepcopy(chart_metadata["heatmap_category"])
        target_row_data = copy.deepcopy(chart_metadata["heatmap_data"])  # matrix
        target_column_data = [list(column_list) for column_list in zip(*target_row_data)]
        target_x_labels = copy.deepcopy(chart_metadata["x_labels"])
        target_y_labels = copy.deepcopy(chart_metadata["y_labels"])

        # Sum
        total_sum = sum([sum(row) for row in target_row_data])

        # Mean
        total_cells = len(target_y_labels) * len(target_x_labels)
        overall_mean = total_sum / total_cells

        # Above & below count and values
        above_mean_num, below_mean_num = 0, 0
        above_mean_positions, below_mean_positions = [], []
        above_mean_values, below_mean_values = [], []
        
        for row_idx in range(len(target_y_labels)):
            for col_idx in range(len(target_x_labels)):
                cell_value = target_row_data[row_idx][col_idx]
                if cell_value > overall_mean:
                    above_mean_num += 1
                    above_mean_positions.append((row_idx, col_idx))
                    above_mean_values.append(cell_value)
                elif cell_value < overall_mean:
                    below_mean_num += 1
                    below_mean_positions.append((row_idx, col_idx))
                    below_mean_values.append(cell_value)

        # Sum sublist
        above_mean_value_sum = sum(above_mean_values)
        below_mean_value_sum = sum(below_mean_values)

        # Mean sublist
        above_mean_value_avg = above_mean_value_sum / above_mean_num if above_mean_num > 0 else 0
        below_mean_value_avg = below_mean_value_sum / below_mean_num if below_mean_num > 0 else 0
        
        # Max/min among above-mean sublist
        max_above_mean_value = max(above_mean_values) if above_mean_values else 0
        min_above_mean_value = min(above_mean_values) if above_mean_values else 0
        max_above_mean_positions = []
        min_above_mean_positions = []
        
        for row_idx in range(len(target_y_labels)):
            for col_idx in range(len(target_x_labels)):
                cell_value = target_row_data[row_idx][col_idx]
                if cell_value == max_above_mean_value and cell_value > overall_mean:
                    max_above_mean_positions.append((row_idx, col_idx))
                if cell_value == min_above_mean_value and cell_value > overall_mean:
                    min_above_mean_positions.append((row_idx, col_idx))

        max_above_mean_labels = [f"{target_y_labels[pos[0]]}, {target_x_labels[pos[1]]}" for pos in max_above_mean_positions]
        min_above_mean_labels = [f"{target_y_labels[pos[0]]}, {target_x_labels[pos[1]]}" for pos in min_above_mean_positions]
        max_above_mean_answer = ", ".join(max_above_mean_labels)
        min_above_mean_answer = ", ".join(min_above_mean_labels)

        # Max/min among below-mean sublist
        max_below_mean_value = max(below_mean_values) if below_mean_values else 0
        min_below_mean_value = min(below_mean_values) if below_mean_values else 0
        max_below_mean_positions = []
        min_below_mean_positions = []
        
        for row_idx in range(len(target_y_labels)):
            for col_idx in range(len(target_x_labels)):
                cell_value = target_row_data[row_idx][col_idx]
                if cell_value == max_below_mean_value and cell_value < overall_mean:
                    max_below_mean_positions.append((row_idx, col_idx))
                if cell_value == min_below_mean_value and cell_value < overall_mean:
                    min_below_mean_positions.append((row_idx, col_idx))

        max_below_mean_labels = [f"{target_y_labels[pos[0]]}, {target_x_labels[pos[1]]}" for pos in max_below_mean_positions]
        min_below_mean_labels = [f"{target_y_labels[pos[0]]}, {target_x_labels[pos[1]]}" for pos in min_below_mean_positions]
        max_below_mean_answer = ", ".join(max_below_mean_labels)
        min_below_mean_answer = ", ".join(min_below_mean_labels)

        # Difference between the sum of above-mean cells and the sum of below-mean cells
        sum_diff = abs(above_mean_value_sum - below_mean_value_sum)
        mean_diff = abs(above_mean_value_avg - below_mean_value_avg)
        
        # All cell indices for reference
        all_cell_indices = [(row_idx, col_idx) for row_idx in range(len(target_y_labels)) for col_idx in range(len(target_x_labels))]
        
        # Reason
        read_all = ""
        for row_idx in range(len(target_y_labels)):
            for col_idx in range(len(target_x_labels)):
                read_all += f"\n- {target_y_labels[row_idx]}, {target_x_labels[col_idx]}: {target_row_data[row_idx][col_idx]}"

        reason_avg = f"Mean = {total_sum}/{total_cells} = {overall_mean}"
        reason_above_mean_value_sum = f"Sum of above-mean cells = {above_mean_value_sum}"
        reason_above_mean_value_avg = f"Mean of above-mean cells = {above_mean_value_sum}/{above_mean_num} = {above_mean_value_avg}"
        reason_below_mean_value_sum = f"Sum of below-mean cells = {below_mean_value_sum}"
        reason_below_mean_value_avg = f"Mean of below-mean cells = {below_mean_value_sum}/{below_mean_num} = {below_mean_value_avg}"

        # Chart QA Pool
        hard_qa_pool = {
            "multi_step__threshold__above_mean__max__value": {
                "question": [
                    f"What is the highest {heatmap_category['singular']} among cells that have their {heatmap_category['singular']} above the average {heatmap_category['singular']} of all cells?",
                    f"Among cells whose {heatmap_category['plural']} are above the average {heatmap_category['singular']} of all cells, what is the highest {heatmap_category['singular']}?",
                    f"What is the highest {heatmap_category['singular']} among cells that have their {heatmap_category['singular']} above the mean {heatmap_category['singular']} of all cells?",
                    f"Among cells whose {heatmap_category['plural']} are above the mean {heatmap_category['singular']} of all cells, what is the highest {heatmap_category['singular']}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {heatmap_category['singular']} of each cell in this heatmap:{read_all}",
                        "step_2": f"Second, I need to compute the average {heatmap_category['singular']} of all cells:\n{reason_avg}",
                        "step_3": f"Third, I need to find all the cells whose {heatmap_category['singular']} is higher than {overall_mean}.",
                        "step_4": f"Fourth, I need to identify the cell with the highest {heatmap_category['singular']} among these cells.",
                    },
                ],
                "constraint": "max value among cells above mean",
                "answer": max_above_mean_value,
                "mask": {
                    "step_1": all_cell_indices,
                    "step_2": all_cell_indices,
                    "step_3": above_mean_positions,
                    "step_4": max_above_mean_positions,
                    "answer": max_above_mean_positions,
                },
            },
            "multi_step__threshold__above_mean__min__value": {
                "question": [
                    f"What is the lowest {heatmap_category['singular']} among cells that have their {heatmap_category['singular']} above the average {heatmap_category['singular']} of all cells?",
                    f"Among cells whose {heatmap_category['plural']} are above the average {heatmap_category['singular']} of all cells, what is the lowest {heatmap_category['singular']}?",
                    f"What is the lowest {heatmap_category['singular']} among cells that have their {heatmap_category['singular']} above the mean {heatmap_category['singular']} of all cells?",
                    f"Among cells whose {heatmap_category['plural']} are above the mean {heatmap_category['singular']} of all cells, what is the lowest {heatmap_category['singular']}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {heatmap_category['singular']} of each cell in this heatmap:{read_all}",
                        "step_2": f"Second, I need to compute the average {heatmap_category['singular']} of all cells:\n{reason_avg}",
                        "step_3": f"Third, I need to find all the cells whose {heatmap_category['singular']} is higher than {overall_mean}.",
                        "step_4": f"Fourth, I need to identify the cell with the lowest {heatmap_category['singular']} among these cells.",
                    },
                ],
                "constraint": "min value among cells above mean",
                "answer": min_above_mean_value,
                "mask": {
                    "step_1": all_cell_indices,
                    "step_2": all_cell_indices,
                    "step_3": above_mean_positions,
                    "step_4": min_above_mean_positions,
                    "answer": min_above_mean_positions,
                },
            },
            "multi_step__threshold__below_mean__max__value": {
                "question": [
                    f"What is the highest {heatmap_category['singular']} among cells that have their {heatmap_category['singular']} below the average {heatmap_category['singular']} of all cells?",
                    f"Among cells whose {heatmap_category['plural']} are below the average {heatmap_category['singular']} of all cells, what is the highest {heatmap_category['singular']}?",
                    f"What is the highest {heatmap_category['singular']} among cells that have their {heatmap_category['singular']} below the mean {heatmap_category['singular']} of all cells?",
                    f"Among cells whose {heatmap_category['plural']} are below the mean {heatmap_category['singular']} of all cells, what is the highest {heatmap_category['singular']}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {heatmap_category['singular']} of each cell in this heatmap:{read_all}",
                        "step_2": f"Second, I need to compute the average {heatmap_category['singular']} of all cells:\n{reason_avg}",
                        "step_3": f"Third, I need to find all the cells whose {heatmap_category['singular']} is lower than {overall_mean}.",
                        "step_4": f"Fourth, I need to identify the cell with the highest {heatmap_category['singular']} among these cells.",
                    },
                ],
                "constraint": "max value among cells below mean",
                "answer": max_below_mean_value,
                "mask": {
                    "step_1": all_cell_indices,
                    "step_2": all_cell_indices,
                    "step_3": below_mean_positions,
                    "step_4": max_below_mean_positions,
                    "answer": max_below_mean_positions,
                },
            },
            "multi_step__threshold__below_mean__min__value": {
                "question": [
                    f"What is the lowest {heatmap_category['singular']} among cells that have their {heatmap_category['singular']} below the average {heatmap_category['singular']} of all cells?",
                    f"Among cells whose {heatmap_category['plural']} are below the average {heatmap_category['singular']} of all cells, what is the lowest {heatmap_category['singular']}?",
                    f"What is the lowest {heatmap_category['singular']} among cells that have their {heatmap_category['singular']} below the mean {heatmap_category['singular']} of all cells?",
                    f"Among cells whose {heatmap_category['plural']} are below the mean {heatmap_category['singular']} of all cells, what is the lowest {heatmap_category['singular']}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {heatmap_category['singular']} of each cell in this heatmap:{read_all}",
                        "step_2": f"Second, I need to compute the average {heatmap_category['singular']} of all cells:\n{reason_avg}",
                        "step_3": f"Third, I need to find all the cells whose {heatmap_category['singular']} is lower than {overall_mean}.",
                        "step_4": f"Fourth, I need to identify the cell with the lowest {heatmap_category['singular']} among these cells.",
                    },
                ],
                "constraint": "min value among cells below mean",
                "answer": min_below_mean_value,
                "mask": {
                    "step_1": all_cell_indices,
                    "step_2": all_cell_indices,
                    "step_3": below_mean_positions,
                    "step_4": min_below_mean_positions,
                    "answer": min_below_mean_positions,
                },
            },
            "multi_step__threshold__above_mean__max__position": {
                "question": [
                    f"What is the position of the cell that has the highest {heatmap_category['singular']} among cells that have their {heatmap_category['singular']} above the average {heatmap_category['singular']} of all cells?",
                    f"Among cells whose {heatmap_category['plural']} are above the average {heatmap_category['singular']} of all cells, what is the position of the cell that has the highest {heatmap_category['singular']}?",
                    f"What is the position of the cell that has the highest {heatmap_category['singular']} among cells that have their {heatmap_category['singular']} above the mean {heatmap_category['singular']} of all cells?",
                    f"Among cells whose {heatmap_category['plural']} are above the mean {heatmap_category['singular']} of all cells, what is the position of the cell that has the highest {heatmap_category['singular']}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {heatmap_category['singular']} of each cell in this heatmap:{read_all}",
                        "step_2": f"Second, I need to compute the average {heatmap_category['singular']} of all cells:\n{reason_avg}",
                        "step_3": f"Third, I need to find all the cells whose {heatmap_category['singular']} is higher than {overall_mean}.",
                        "step_4": f"Fourth, I need to identify the cell with the highest {heatmap_category['singular']} among these cells.",
                    },
                ],
                "constraint": "position of max value among cells above mean",
                "answer": max_above_mean_answer,
                "mask": {
                    "step_1": all_cell_indices,
                    "step_2": all_cell_indices,
                    "step_3": above_mean_positions,
                    "step_4": max_above_mean_positions,
                    "answer": max_above_mean_positions,
                },
            },
            "multi_step__threshold__above_mean__sum": {
                "question": [
                    f"What is the sum of {heatmap_category['plural']} for cells that have their {heatmap_category['singular']} above the average {heatmap_category['singular']} of all cells?",
                    f"Among cells whose {heatmap_category['plural']} are above the average {heatmap_category['singular']} of all cells, what is the sum of their {heatmap_category['plural']}?",
                    f"What is the sum of {heatmap_category['plural']} for cells that have their {heatmap_category['singular']} above the mean {heatmap_category['singular']} of all cells?",
                    f"Among cells whose {heatmap_category['plural']} are above the mean {heatmap_category['singular']} of all cells, what is the sum of their {heatmap_category['plural']}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {heatmap_category['singular']} of each cell in this heatmap:{read_all}",
                        "step_2": f"Second, I need to compute the average {heatmap_category['singular']} of all cells:\n{reason_avg}",
                        "step_3": f"Third, I need to find all the cells whose {heatmap_category['singular']} is higher than {overall_mean}.",
                        "step_4": f"Fourth, I need to calculate the total {heatmap_category['singular']} of these cells:\n{reason_above_mean_value_sum}",
                    },
                ],
                "constraint": "sum of cells above mean",
                "answer": above_mean_value_sum,
                "mask": {
                    "step_1": all_cell_indices,
                    "step_2": all_cell_indices,
                    "step_3": above_mean_positions,
                    "step_4": above_mean_positions,
                    "answer": above_mean_positions,
                },
            },
            "multi_step__threshold__below_mean__sum": {
                "question": [
                    f"What is the sum of {heatmap_category['plural']} for cells that have their {heatmap_category['singular']} below the average {heatmap_category['singular']} of all cells?",
                    f"Among cells whose {heatmap_category['plural']} are below the average {heatmap_category['singular']} of all cells, what is the sum of their {heatmap_category['plural']}?",
                    f"What is the sum of {heatmap_category['plural']} for cells that have their {heatmap_category['singular']} below the mean {heatmap_category['singular']} of all cells?",
                    f"Among cells whose {heatmap_category['plural']} are below the mean {heatmap_category['singular']} of all cells, what is the sum of their {heatmap_category['plural']}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {heatmap_category['singular']} of each cell in this heatmap:{read_all}",
                        "step_2": f"Second, I need to compute the average {heatmap_category['singular']} of all cells:\n{reason_avg}",
                        "step_3": f"Third, I need to find all the cells whose {heatmap_category['singular']} is lower than {overall_mean}.",
                        "step_4": f"Fourth, I need to calculate the total {heatmap_category['singular']} of these cells:\n{reason_below_mean_value_sum}",
                    },
                ],
                "constraint": "sum of cells below mean",
                "answer": below_mean_value_sum,
                "mask": {
                    "step_1": all_cell_indices,
                    "step_2": all_cell_indices,
                    "step_3": below_mean_positions,
                    "step_4": below_mean_positions,
                    "answer": below_mean_positions,
                },
            },
            "multi_step__threshold__mean__sum_diff": {
                "question": [
                    f"What is the absolute difference between the total {heatmap_category['singular']} of cells above the average {heatmap_category['singular']} and those below it?",
                    f"What is the absolute value of the difference between the total {heatmap_category['singular']} for cells above the average and those below the average {heatmap_category['singular']}?",
                    f"What is the absolute difference between the total {heatmap_category['singular']} of cells above the mean {heatmap_category['singular']} and those below it?",
                    f"What is the absolute value of the difference between the total {heatmap_category['singular']} for cells above the mean {heatmap_category['singular']} and those below the mean {heatmap_category['singular']}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {heatmap_category['singular']} of each cell in this heatmap:{read_all}",
                        "step_2": f"Second, I need to compute the average {heatmap_category['singular']} of all cells:\n{reason_avg}",
                        "step_3": f"Third, I need to find the first group of cells whose {heatmap_category['singular']} is higher than {overall_mean} and the second group of cells whose {heatmap_category['singular']} is lower than {overall_mean}.",
                        "step_4": f"Fourth, I need to calculate the total {heatmap_category['singular']} of these two groups of cells respectively:\n- Group 1 (above overall mean): {reason_above_mean_value_sum}\n- Group 2 (below overall mean): {reason_below_mean_value_sum}",
                        "step_5": f"Fifth, I need to calculate the absolute difference between these two groups of cells:\n|{above_mean_value_sum} - {below_mean_value_sum}| = {sum_diff}.",
                    },
                ],
                "constraint": "sum difference between cells above and below mean",
                "answer": sum_diff,
                "mask": {
                    "step_1": all_cell_indices,
                    "step_2": all_cell_indices,
                    "step_3": above_mean_positions + below_mean_positions,
                    "step_4": above_mean_positions + below_mean_positions,
                    "step_5": above_mean_positions + below_mean_positions,
                    "answer": above_mean_positions + below_mean_positions,
                },
            },
        }

        return hard_qa_pool


    ############################################################
    #                  Chart QA Data Generator
    ############################################################

    def chart_qa_generator(self, chart_metadata: Dict):
        """Generate only one reasoning step."""
        # Constraints
        x_axis_title = chart_metadata['x_label'].lower()
        y_axis_title = chart_metadata['y_label'].lower()
        heatmap_category = chart_metadata["heatmap_category"]

        # Constraint - Value
        extrema_dict = self._find_matrix_extrema_with_pos(chart_metadata["heatmap_data"])
        min_value, min_pos = extrema_dict["min_value"], extrema_dict["min_pos"]
        max_value, max_pos = extrema_dict["max_value"], extrema_dict["max_pos"]
        min_label_answer = f"{chart_metadata['y_labels'][min_pos[0]]}, {chart_metadata['x_labels'][min_pos[1]]}"
        max_label_answer = f"{chart_metadata['y_labels'][max_pos[0]]}, {chart_metadata['x_labels'][max_pos[1]]}"

        # Constraint - Label (select some rows for filtering)
        selected_row_indices = [0, 2, 3]  # TODO: convert fixed indices to soft lists (currently disabled to avoid oversize generated data)
        selected_y_labels = self._convert_answer_idx_to_str(chart_metadata["y_labels"], selected_row_indices)

        # Key: constraint, Value: row_list
        constraint_meta = {
            # Selected value - filter by rows that have cells with values in middle range
            f"in rows that have their {heatmap_category['singular']} above the lowest while below the highest": self._get_middle_value_rows(chart_metadata["heatmap_data"]),
            f"in rows that have their {heatmap_category['singular']} higher than {min_value} but lower than {max_value}": self._get_middle_value_rows(chart_metadata["heatmap_data"]),
            f"in rows whose {heatmap_category['plural']} are above the lowest while below the highest": self._get_middle_value_rows(chart_metadata["heatmap_data"]),
            f"in rows whose {heatmap_category['plural']} are higher than {min_value} but lower than {max_value}": self._get_middle_value_rows(chart_metadata["heatmap_data"]),
            f"in rows with their {heatmap_category['plural']} higher than {min_value} but lower than {max_value}": self._get_middle_value_rows(chart_metadata["heatmap_data"]),
            f"in rows with their {heatmap_category['plural']} higher than the lowest but lower than the highest": self._get_middle_value_rows(chart_metadata["heatmap_data"]),

            # Selected label
            f"in rows that have their labels among '{selected_y_labels}'": selected_row_indices,
            f"in rows whose labels are one of '{selected_y_labels}'": selected_row_indices,
            f"in rows among the labels '{selected_y_labels}'": selected_row_indices,
        }

        # (1) Statistics
        # (1.1) Easy: one-step
        aggregation_easy_qa_pool = self._one_step_statistics(chart_metadata)
        self._qa_pool_converter(qa_pool=aggregation_easy_qa_pool, curriculum_level=1)
        # (1.2) Medium: two-step
        for qa_constraint in constraint_meta:
            qa_row_list = constraint_meta[qa_constraint]
            aggregation_medium_qa_pool = self._two_step_statistics(chart_metadata, qa_row_list, qa_constraint)
            self._qa_pool_converter(qa_pool=aggregation_medium_qa_pool, curriculum_level=2)

        # (2) Extrema
        # (2.1) Easy: one-step
        extrema_easy_qa_pool = self._one_step_extrema(chart_metadata)
        self._qa_pool_converter(qa_pool=extrema_easy_qa_pool, curriculum_level=1)
        # (2.2) Medium: two-step
        for qa_constraint in constraint_meta:
            qa_row_list = constraint_meta[qa_constraint]
            extrema_medium_qa_pool = self._two_step_extrema(chart_metadata, qa_row_list, qa_constraint)
            self._qa_pool_converter(qa_pool=extrema_medium_qa_pool, curriculum_level=2)

        # (3) Compare
        # (3.1) Medium: two-step
        compare_cell_positions = [(2, 1), (0, 3)]  # TODO: convert fixed positions to soft lists (currently disabled to avoid oversize generated data)
        compare_medium_qa_pool = self._two_step_compare_two_heatmap_cells(chart_metadata, compare_cell_positions)
        self._qa_pool_converter(qa_pool=compare_medium_qa_pool, curriculum_level=2)

        # (4) Sort
        # (4.1) Easy: one-step
        sort_easy_qa_pool = self._one_step_sort(chart_metadata)
        self._qa_pool_converter(qa_pool=sort_easy_qa_pool, curriculum_level=1)
        # (4.2) Medium: two-step
        for qa_constraint in constraint_meta:
            qa_row_list = constraint_meta[qa_constraint]
            sort_medium_qa_pool = self._two_step_sort(chart_metadata, qa_row_list, qa_constraint)
            self._qa_pool_converter(qa_pool=sort_medium_qa_pool, curriculum_level=2)

        # (5) Get value or label
        # (5.1) Easy: one-step
        read_easy_qa_pool = self._one_step_read(chart_metadata)
        self._qa_pool_converter(qa_pool=read_easy_qa_pool, curriculum_level=1)

        # (6) Filter & Select
        filter_condition = [2, 5]    # TODO: change condition range
        filter_medium_qa_pool = self._two_step_filter(chart_metadata, filter_condition)
        self._qa_pool_converter(qa_pool=filter_medium_qa_pool, curriculum_level=2)

        # (7) Threshold
        threshold_medium_qa_pool = self._two_step_threshold(chart_metadata)
        self._qa_pool_converter(qa_pool=threshold_medium_qa_pool, curriculum_level=2)

        # (8) Multi-step operator
        multi_threshold_hard_qa_pool = self._multi_step_threshold(chart_metadata)
        self._qa_pool_converter(qa_pool=multi_threshold_hard_qa_pool, curriculum_level=3)

        return self.all_qa_data_list