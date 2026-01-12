import os
import json
import copy
from typing import List, Dict, Union, Tuple


class LineChartGenerator:
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

    
    def _find_matrix_extrema_with_pos(matrix):
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

    def _convert_answer_idx_to_str(self, line_labels: List, ans_indices: List) -> str:
        """Convert to answer string"""
        ans_list = [line_labels[ans_idx] for ans_idx in ans_indices]
        return ", ".join(ans_list)

    def _convert_idx_to_pos(self, line_idx):
        """Convert line index to line position"""
        pos = [
            "1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th",
            "11th", "12th", "13th", "14th", "15th", "16th", "17th", "18th", "19th", "20th",
            "21st", "22nd", "23rd", "24th", "25th", "26th", "27th", "28th", "29th", "30th",
        ]
        return pos[line_idx]

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
        """Statistics: sum, mean, median, count"""
        x_axis_title = chart_metadata['x_label'].lower()
        y_axis_title = chart_metadata['y_label'].lower()
        line_category = copy.deepcopy(chart_metadata["line_category"])
        target_line_data = copy.deepcopy(chart_metadata["line_data"])
        target_x_data = [list(column_list) for column_list in zip(*target_line_data)]
        target_line_labels = copy.deepcopy(chart_metadata["line_labels"])
        target_x_labels = [str(new_label) for new_label in chart_metadata["x_labels"]]
        target_line_indices = [l_idx for l_idx in range(len(target_line_data))]
        target_x_indices = [x_idx for x_idx in range(len(target_x_labels))]

        # Sum
        line_sum = self._compute_matrix_row_sum(target_line_data)
        x_sum = self._compute_matrix_column_sum(target_line_data)
        
        # Mean
        line_mean = [curr_sum / len(target_x_labels) for curr_sum in line_sum]
        x_mean = [curr_sum / len(target_line_labels) for curr_sum in x_sum]

        # Median
        line_median_value, line_median_indices = [], []
        for kth_line_data_list in target_line_data:
            kth_line_median_value, kth_line_median_indices = self._compute_data_median(kth_line_data_list)
            line_median_value.append(kth_line_median_value)
            line_median_indices.append(kth_line_median_indices)

        x_median_value, x_median_indices = [], []
        for kth_x_data_list in target_x_data:
            kth_x_median_value, kth_x_median_indices = self._compute_data_median(kth_x_data_list)
            x_median_value.append(kth_x_median_value)
            x_median_indices.append(kth_x_median_indices)

        # Count
        count_line_num = len(target_line_labels)
        count_marker_num = len(target_x_labels)

        # Chart QA Pool
        easy_qa_pool = {
            "one_step__statistics__sum_lines": {
                "question": [
                    f"What is the total {y_axis_title} for all the {line_category['plural']} in this chart?",
                    f"For all the {line_category['plural']} in this chart, what is the sum of their {y_axis_title}?",
                    f"Can you help calculate the sum of {y_axis_title} for all the {line_category['plural']} in this chart?",
                    f"Please compute the sum of {y_axis_title} for all the {line_category['plural']} in this chart.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of each {line_category['singular']} across all {x_axis_title} points in this chart.",
                        "step_2": f"Second, I need to sum them up to calculate the total {y_axis_title} of all the {line_category['plural']}, which should be: {'+'.join([str(s) for s in line_sum])} = {sum(line_sum)}.",
                    },
                ],
                "constraint": None,
                "answer": sum(line_sum),
                "mask": {
                    "step_1": target_line_indices,
                    "step_2": target_line_indices,
                    "answer": target_line_indices,
                },
            },
            "one_step__statistics__mean_lines": {
                "question": [
                    f"What is the mean {y_axis_title} of all the {line_category['plural']} in this chart? Please round to two decimal places.",
                    f"For all the {line_category['plural']} in this chart, what is their mean {y_axis_title}? Please round to two decimal places.",
                    f"Can you help calculate the mean {y_axis_title} of all the {line_category['plural']} in this chart? Please round to two decimal places.",
                    f"Please compute the mean {y_axis_title} of all the {line_category['plural']} in this chart. Please round to two decimal places.",
                    f"What is the average {y_axis_title} of all the {line_category['plural']} in this chart? Please round to two decimal places.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of each {line_category['singular']} across all {x_axis_title} points in this chart.",
                        "step_2": f"Second, I need to calculate the mean {y_axis_title} of all the {line_category['plural']}, which should be: {sum(line_sum)}/{len(target_line_data) * len(target_x_labels)} = {sum(line_sum) / (len(target_line_data) * len(target_x_labels))}.",
                    },
                ],
                "constraint": None,
                "answer": sum(line_sum) / (len(target_line_data) * len(target_x_labels)),
                "mask": {
                    "step_1": target_line_indices,
                    "step_2": target_line_indices,
                    "answer": target_line_indices,
                },
            },
            "one_step__statistics__count_lines": {
                "question": [
                    f"How many {line_category['plural']} are included in this chart?",
                    f"What is the number of {line_category['plural']} shown in this chart?",
                    f"Please help count the total number of {line_category['plural']} plotted in this chart.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to count the number of {line_category['plural']} in this chart.",
                    },
                ],
                "constraint": None,
                "answer": count_line_num,
                "mask": {
                    "step_1": target_line_indices,
                    "answer": target_line_indices,
                },
            },
            "one_step__statistics__count_points": {
                "question": [
                    f"How many {x_axis_title} points are included in this chart?",
                    f"What is the number of {x_axis_title} points shown in this chart?",
                    f"Please help count the total number of {x_axis_title} points plotted in this chart.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to count the number of {x_axis_title} points in this chart.",
                    },
                ],
                "constraint": None,
                "answer": count_marker_num,
                "mask": {
                    "step_1": target_x_indices,
                    "answer": target_x_indices,
                },
            },
        }

        return easy_qa_pool
        


    def _one_step_extrema(self, chart_metadata: Dict):
        """Extrema: value (min, max), pos (left, right, top, bottom)"""
        x_axis_title = chart_metadata['x_label'].lower()
        y_axis_title = chart_metadata['y_label'].lower()
        line_category = copy.deepcopy(chart_metadata["line_category"])
        target_line_data = copy.deepcopy(chart_metadata["line_data"])
        target_line_labels = copy.deepcopy(chart_metadata["line_labels"])
        target_x_labels = [str(new_label) for new_label in chart_metadata["x_labels"]]
        target_line_indices = [l_idx for l_idx in range(len(target_line_data))]

        # Value: Min & Max
        extrema_dict = self._find_matrix_extrema_with_pos(target_line_data)
        min_value, min_pos = extrema_dict["min_value"], extrema_dict["min_pos"]
        min_label_answer = f"{target_line_labels[min_pos[0]]}"
        min_x_label_answer = f"{target_x_labels[min_pos[1]]}"
        max_value, max_pos = extrema_dict["max_value"], extrema_dict["max_pos"]
        max_label_answer = f"{target_line_labels[max_pos[0]]}"
        max_x_label_answer = f"{target_x_labels[max_pos[1]]}"

        # Chart QA Pool
        easy_qa_pool = {
            "one_step__extrema__value__min__value": {
                "question": [
                    f"What is the lowest {y_axis_title} among all data points in this chart?",
                    f"What is the smallest {y_axis_title} among all data points in this chart?",
                    f"Among all the data points shown in this chart, what is the lowest {y_axis_title}?",
                    f"Among all the data points shown in this chart, what is the smallest {y_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of all data points across all {line_category['plural']} in this chart.",
                        "step_2": f"Second, I need to compare them to find the lowest {y_axis_title}.",
                    },
                ],
                "constraint": None,
                "answer": min_value,
                "mask": {
                    "step_1": target_line_indices,
                    "step_2": [min_pos[0]],
                    "answer": [min_pos[0]],
                },
            },
            "one_step__extrema__value__max__value": {
                "question": [
                    f"What is the highest {y_axis_title} among all data points in this chart?",
                    f"What is the largest {y_axis_title} among all data points in this chart?",
                    f"Among all the data points shown in this chart, what is the highest {y_axis_title}?",
                    f"Among all the data points shown in this chart, what is the largest {y_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of all data points across all {line_category['plural']} in this chart.",
                        "step_2": f"Second, I need to compare them to find the highest {y_axis_title}.",
                    },
                ],
                "constraint": None,
                "answer": max_value,
                "mask": {
                    "step_1": target_line_indices,
                    "step_2": [max_pos[0]],
                    "answer": [max_pos[0]],
                },
            },
            "one_step__extrema__value__min__line_label": {
                "question": [
                    f"What is the name of the {line_category['singular']} that has the lowest {y_axis_title} among all data points in this chart?",
                    f"Which {line_category['singular']} has the lowest {y_axis_title} among all data points in this chart?",
                    f"What is the name of the {line_category['singular']} that has the smallest {y_axis_title} among all data points in this chart?",
                    f"Which {line_category['singular']} has the smallest {y_axis_title} among all data points in this chart?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of all data points across all {line_category['plural']} in this chart.",
                        "step_2": f"Second, I need to compare them to find the data point with the lowest {y_axis_title}.",
                        "step_3": f"Third, I need to identify which {line_category['singular']} this data point belongs to.",
                    },
                ],
                "constraint": None,
                "answer": min_label_answer,
                "mask": {
                    "step_1": target_line_indices,
                    "step_2": [min_pos[0]],
                    "step_3": [min_pos[0]],
                    "answer": [min_pos[0]],
                },
            },
            "one_step__extrema__value__max__line_label": {
                "question": [
                    f"What is the name of the {line_category['singular']} that has the highest {y_axis_title} among all data points in this chart?",
                    f"Which {line_category['singular']} has the highest {y_axis_title} among all data points in this chart?",
                    f"What is the name of the {line_category['singular']} that has the largest {y_axis_title} among all data points in this chart?",
                    f"Which {line_category['singular']} has the largest {y_axis_title} among all data points in this chart?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of all data points across all {line_category['plural']} in this chart.",
                        "step_2": f"Second, I need to compare them to find the data point with the highest {y_axis_title}.",
                        "step_3": f"Third, I need to identify which {line_category['singular']} this data point belongs to.",
                    },
                ],
                "constraint": None,
                "answer": max_label_answer,
                "mask": {
                    "step_1": target_line_indices,
                    "step_2": [max_pos[0]],
                    "step_3": [max_pos[0]],
                    "answer": [max_pos[0]],
                },
            },
        }

        return easy_qa_pool
        

    def _one_step_sort(self, chart_metadata: Dict):
        """Sort: ascending and descending"""
        x_axis_title = chart_metadata['x_label'].lower()
        y_axis_title = chart_metadata['y_label'].lower()
        line_category = copy.deepcopy(chart_metadata["line_category"])
        target_line_data = copy.deepcopy(chart_metadata["line_data"])
        target_line_labels = copy.deepcopy(chart_metadata["line_labels"])
        target_line_indices = [l_idx for l_idx in range(len(target_line_data))]

        # Calculate total values for each line for sorting
        line_totals = self._compute_matrix_row_sum(target_line_data)
        line_averages = [total / len(target_line_data[0]) for total in line_totals]

        # GT sort
        sort_total_ascending = self._sort_y_order_for_x(line_totals, target_line_labels, "ascending")
        sort_total_descending = self._sort_y_order_for_x(line_totals, target_line_labels, "descending")
        sort_avg_ascending = self._sort_y_order_for_x(line_averages, target_line_labels, "ascending")
        sort_avg_descending = self._sort_y_order_for_x(line_averages, target_line_labels, "descending")

        # Chart QA Pool
        easy_qa_pool = {
            "one_step__sort__total__ascending": {
                "question": [
                    f"If sorting all the {line_category['plural']} in ascending order according to their total {y_axis_title}, can you help provide their label sequence in order separated with commas?",
                    f"Please sort all the given {line_category['plural']} in ascending order according to their total {y_axis_title}, and provide their sorted label sequence separated with commas.",
                    f"Can you help sort all the given {line_category['plural']} according to their total {y_axis_title} from low to high, and provide their sorted label sequence separated with commas?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of all the {line_category['plural']} across all {x_axis_title} points in this chart.",
                        "step_2": f"Second, I need to calculate the total {y_axis_title} for each {line_category['singular']}.",
                        "step_3": f"Third, I need to sort these {line_category['plural']} according to their total {y_axis_title} from low to high, and respond with the sorted sequence of their labels.",
                    },
                ],
                "constraint": None,
                "answer": sort_total_ascending,
                "mask": {
                    "step_1": target_line_indices,
                    "step_2": target_line_indices,
                    "step_3": target_line_indices,
                    "answer": target_line_indices,
                },
            },
            "one_step__sort__total__descending": {
                "question": [
                    f"If sorting all the {line_category['plural']} in descending order according to their total {y_axis_title}, can you help provide their label sequence in order separated with commas?",
                    f"Please sort all the given {line_category['plural']} in descending order according to their total {y_axis_title}, and provide their sorted label sequence separated with commas.",
                    f"Can you help sort all the given {line_category['plural']} according to their total {y_axis_title} from high to low, and provide their sorted label sequence separated with commas?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of all the {line_category['plural']} across all {x_axis_title} points in this chart.",
                        "step_2": f"Second, I need to calculate the total {y_axis_title} for each {line_category['singular']}.",
                        "step_3": f"Third, I need to sort these {line_category['plural']} according to their total {y_axis_title} from high to low, and respond with the sorted sequence of their labels.",
                    },
                ],
                "constraint": None,
                "answer": sort_total_descending,
                "mask": {
                    "step_1": target_line_indices,
                    "step_2": target_line_indices,
                    "step_3": target_line_indices,
                    "answer": target_line_indices,
                },
            },
            "one_step__sort__average__ascending": {
                "question": [
                    f"If sorting all the {line_category['plural']} in ascending order according to their average {y_axis_title}, can you help provide their label sequence in order separated with commas?",
                    f"Please sort all the given {line_category['plural']} in ascending order according to their average {y_axis_title}, and provide their sorted label sequence separated with commas.",
                    f"Can you help sort all the given {line_category['plural']} according to their average {y_axis_title} from low to high, and provide their sorted label sequence separated with commas?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of all the {line_category['plural']} across all {x_axis_title} points in this chart.",
                        "step_2": f"Second, I need to calculate the average {y_axis_title} for each {line_category['singular']}.",
                        "step_3": f"Third, I need to sort these {line_category['plural']} according to their average {y_axis_title} from low to high, and respond with the sorted sequence of their labels.",
                    },
                ],
                "constraint": None,
                "answer": sort_avg_ascending,
                "mask": {
                    "step_1": target_line_indices,
                    "step_2": target_line_indices,
                    "step_3": target_line_indices,
                    "answer": target_line_indices,
                },
            },
            "one_step__sort__average__descending": {
                "question": [
                    f"If sorting all the {line_category['plural']} in descending order according to their average {y_axis_title}, can you help provide their label sequence in order separated with commas?",
                    f"Please sort all the given {line_category['plural']} in descending order according to their average {y_axis_title}, and provide their sorted label sequence separated with commas.",
                    f"Can you help sort all the given {line_category['plural']} according to their average {y_axis_title} from high to low, and provide their sorted label sequence separated with commas?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of all the {line_category['plural']} across all {x_axis_title} points in this chart.",
                        "step_2": f"Second, I need to calculate the average {y_axis_title} for each {line_category['singular']}.",
                        "step_3": f"Third, I need to sort these {line_category['plural']} according to their average {y_axis_title} from high to low, and respond with the sorted sequence of their labels.",
                    },
                ],
                "constraint": None,
                "answer": sort_avg_descending,
                "mask": {
                    "step_1": target_line_indices,
                    "step_2": target_line_indices,
                    "step_3": target_line_indices,
                    "answer": target_line_indices,
                },
            },
        }

        return easy_qa_pool
    
    def _one_step_read(self, chart_metadata: Dict):
        """Read: value, label"""
        x_axis_title = chart_metadata['x_label'].lower()
        y_axis_title = chart_metadata['y_label'].lower()
        line_category = copy.deepcopy(chart_metadata["line_category"])
        target_line_data = copy.deepcopy(chart_metadata["line_data"])
        target_line_labels = copy.deepcopy(chart_metadata["line_labels"])
        target_x_labels = [str(new_label) for new_label in chart_metadata["x_labels"]]

        # Chart QA Pool
        easy_qa_pool = {}

        # Generate read questions for specific data points
        for line_idx, line_data in enumerate(target_line_data):
            line_label = target_line_labels[line_idx]
            
            for x_idx, value in enumerate(line_data):
                x_label = target_x_labels[x_idx]
                
                # Read value questions
                easy_qa_pool[f"one_step__read__value__line_{line_idx+1}_point_{x_idx+1}"] = {
                    "question": [
                        f"What is the {y_axis_title} of {line_label} at {x_label}?",
                        f"What is the {y_axis_title} of {line_label} in {x_label}?",
                        f"What is the {y_axis_title} value for {line_label} at {x_label}?",
                    ],
                    "reasoning": [
                        {
                            "step_1": f"First, I need to find the line representing '{line_label}'.",
                            "step_2": f"Second, I need to read its {y_axis_title} at {x_label}.",
                        },
                    ],
                    "constraint": None,
                    "answer": value,
                    "mask": {
                        "step_1": [line_idx],
                        "step_2": [line_idx],
                        "answer": [line_idx],
                    },
                }

        return easy_qa_pool
        

    ############################################################
    #                     Two-step Operator
    ############################################################

    def _two_step_statistics(self, chart_metadata: Dict, target_line_indices: List, constraint: str):
        """Statistics: sum, mean, median, count"""
        x_axis_title = chart_metadata['x_label'].lower()
        y_axis_title = chart_metadata['y_label'].lower()
        line_category = copy.deepcopy(chart_metadata["line_category"])
        target_line_data = [chart_metadata["line_data"][kk] for kk in target_line_indices]
        target_line_labels = [chart_metadata["line_labels"][kk] for kk in target_line_indices]
        target_x_labels = [str(new_label) for new_label in chart_metadata["x_labels"]]

        # Sum
        line_sum = self._compute_matrix_row_sum(target_line_data)
        x_sum = self._compute_matrix_column_sum(target_line_data)
        
        # Mean
        line_mean = [curr_sum / len(target_x_labels) for curr_sum in line_sum]
        x_mean = [curr_sum / len(target_line_labels) for curr_sum in x_sum]

        # Count
        count_line_num = len(target_line_labels)
        count_marker_num = len(target_x_labels)

        # Chart QA Pool
        medium_qa_pool = {
            "two_step__statistics__sum": {
                "question": [
                    f"What is the total {y_axis_title} for {line_category['plural']} {constraint}?",
                    f"For the {line_category['plural']} {constraint}, what is the sum of their {y_axis_title}?",
                    f"Can you help calculate the sum of {y_axis_title} for {line_category['plural']} {constraint}?",
                    f"Please compute the sum of {y_axis_title} for {line_category['plural']} {constraint}.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to identify the {line_category['plural']} {constraint}.",
                        "step_2": f"Second, I need to calculate their total {y_axis_title}: {'+'.join([str(s) for s in line_sum])} = {sum(line_sum)}",
                    },
                ],
                "constraint": constraint,
                "answer": sum(line_sum),
                "mask": {
                    "step_1": target_line_indices,
                    "step_2": target_line_indices,
                    "answer": target_line_indices,
                },
            },
            "two_step__statistics__mean": {
                "question": [
                    f"What is the mean {y_axis_title} for {line_category['plural']} {constraint}? Please round to two decimal places.",
                    f"For {line_category['plural']} {constraint}, what is their mean {y_axis_title}? Please round to two decimal places.",
                    f"Can you help calculate the mean {y_axis_title} for {line_category['plural']} {constraint}? Please round to two decimal places.",
                    f"Please compute the mean {y_axis_title} for {line_category['plural']} {constraint}. Please round to two decimal places.",
                    f"What is the average {y_axis_title} for {line_category['plural']} {constraint}? Please round to two decimal places.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to identify the {line_category['plural']} {constraint}.",
                        "step_2": f"Second, I need to calculate their average {y_axis_title}: {sum(line_sum)}/{len(target_line_data) * len(target_x_labels)} = {sum(line_sum) / (len(target_line_data) * len(target_x_labels))}",
                    },
                ],
                "constraint": constraint,
                "answer": sum(line_sum) / (len(target_line_data) * len(target_x_labels)),
                "mask": {
                    "step_1": target_line_indices,
                    "step_2": target_line_indices,
                    "answer": target_line_indices,
                },
            },
            "two_step__statistics__count": {
                "question": [
                    f"How many {line_category['plural']} {constraint} are shown in this chart?",
                    f"What is the number of {line_category['plural']} {constraint}?",
                    f"Please help count the number of {line_category['plural']} {constraint}.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to find all the {line_category['plural']} {constraint}.",
                        "step_2": f"Second, I need to count the total number of these {line_category['plural']}.",
                    },
                ],
                "constraint": constraint,
                "answer": count_line_num,
                "mask": {
                    "step_1": target_line_indices,
                    "step_2": target_line_indices,
                    "answer": target_line_indices,
                },
            },
        }

        return medium_qa_pool

    def _two_step_extrema(self, chart_metadata: Dict, target_line_indices: List, constraint: str):
        """Extrema: value (min, max), pos (left, right, top, bottom)"""
        x_axis_title = chart_metadata['x_label'].lower()
        y_axis_title = chart_metadata['y_label'].lower()
        line_category = copy.deepcopy(chart_metadata["line_category"])
        target_line_data = [chart_metadata["line_data"][kk] for kk in target_line_indices]
        target_line_labels = [chart_metadata["line_labels"][kk] for kk in target_line_indices]
        target_x_labels = [str(new_label) for new_label in chart_metadata["x_labels"]]

        # Value: Min & Max
        extrema_dict = self._find_matrix_extrema_with_pos(target_line_data)
        min_value, min_pos = extrema_dict["min_value"], extrema_dict["min_pos"]
        min_label_answer = f"{target_line_labels[min_pos[0]]}"
        max_value, max_pos = extrema_dict["max_value"], extrema_dict["max_pos"]
        max_label_answer = f"{target_line_labels[max_pos[0]]}"

        # Chart QA Pool
        medium_qa_pool = {
            "two_step__extrema__value__min__value": {
                "question": [
                    f"What is the lowest {y_axis_title} among {line_category['plural']} {constraint}?",
                    f"What is the smallest {y_axis_title} among {line_category['plural']} {constraint}?",
                    f"Among {line_category['plural']} {constraint}, what is the lowest {y_axis_title}?",
                    f"Among {line_category['plural']} {constraint}, what is the smallest {y_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to find all the {line_category['plural']} {constraint}.",
                        "step_2": f"Second, I need to compare their {y_axis_title} values to find the one with the lowest {y_axis_title}.",
                    },
                ],
                "constraint": constraint,
                "answer": min_value,
                "mask": {
                    "step_1": target_line_indices,
                    "step_2": [target_line_indices[min_pos[0]]],
                    "answer": [target_line_indices[min_pos[0]]],
                },
            },
            "two_step__extrema__value__max__value": {
                "question": [
                    f"What is the highest {y_axis_title} among {line_category['plural']} {constraint}?",
                    f"What is the largest {y_axis_title} among {line_category['plural']} {constraint}?",
                    f"Among {line_category['plural']} {constraint}, what is the highest {y_axis_title}?",
                    f"Among {line_category['plural']} {constraint}, what is the largest {y_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to find all the {line_category['plural']} {constraint}.",
                        "step_2": f"Second, I need to compare their {y_axis_title} values to find the one with the highest {y_axis_title}.",
                    },
                ],
                "constraint": constraint,
                "answer": max_value,
                "mask": {
                    "step_1": target_line_indices,
                    "step_2": [target_line_indices[max_pos[0]]],
                    "answer": [target_line_indices[max_pos[0]]],
                },
            },
            "two_step__extrema__value__min__label": {
                "question": [
                    f"What is the name of the {line_category['singular']} that has the lowest {y_axis_title} among {line_category['plural']} {constraint}?",
                    f"Which {line_category['singular']} has the lowest {y_axis_title} among {line_category['plural']} {constraint}?",
                    f"What is the name of the {line_category['singular']} that has the smallest {y_axis_title} among {line_category['plural']} {constraint}?",
                    f"Which {line_category['singular']} has the smallest {y_axis_title} among {line_category['plural']} {constraint}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to find all the {line_category['plural']} {constraint}.",
                        "step_2": f"Second, I need to compare their {y_axis_title} values to find the one with the lowest {y_axis_title}.",
                        "step_3": f"Third, I need to identify the name of this {line_category['singular']}.",
                    },
                ],
                "constraint": constraint,
                "answer": min_label_answer,
                "mask": {
                    "step_1": target_line_indices,
                    "step_2": [target_line_indices[min_pos[0]]],
                    "step_3": [target_line_indices[min_pos[0]]],
                    "answer": [target_line_indices[min_pos[0]]],
                },
            },
            "two_step__extrema__value__max__label": {
                "question": [
                    f"What is the name of the {line_category['singular']} that has the highest {y_axis_title} among {line_category['plural']} {constraint}?",
                    f"Which {line_category['singular']} has the highest {y_axis_title} among {line_category['plural']} {constraint}?",
                    f"What is the name of the {line_category['singular']} that has the largest {y_axis_title} among {line_category['plural']} {constraint}?",
                    f"Which {line_category['singular']} has the largest {y_axis_title} among {line_category['plural']} {constraint}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to find all the {line_category['plural']} {constraint}.",
                        "step_2": f"Second, I need to compare their {y_axis_title} values to find the one with the highest {y_axis_title}.",
                        "step_3": f"Third, I need to identify the name of this {line_category['singular']}.",
                    },
                ],
                "constraint": constraint,
                "answer": max_label_answer,
                "mask": {
                    "step_1": target_line_indices,
                    "step_2": [target_line_indices[max_pos[0]]],
                    "step_3": [target_line_indices[max_pos[0]]],
                    "answer": [target_line_indices[max_pos[0]]],
                },
            },
        }

        return medium_qa_pool


    def _two_step_compare_two_lines(self, chart_metadata: Dict, target_line_indices: List):
        """Compare: value, pos"""
        assert len(target_line_indices) == 2 and target_line_indices[0] != target_line_indices[1]

        x_axis_title = chart_metadata['x_label'].lower()
        y_axis_title = chart_metadata['y_label'].lower()
        line_category = copy.deepcopy(chart_metadata["line_category"])
        target_line_data = [chart_metadata["line_data"][kk] for kk in target_line_indices]
        target_line_labels = [chart_metadata["line_labels"][kk] for kk in target_line_indices]

        # Calculate totals and averages for comparison
        line_totals = [sum(line_data) for line_data in target_line_data]
        line_averages = [total / len(target_line_data[0]) for total in line_totals]

        # GT answer & mask for total comparison
        if line_totals[0] > line_totals[1]:
            gt_answer_total_higher = target_line_labels[0]
            gt_mask_total_higher = [target_line_indices[0]]
            gt_symbol_total_higher = ">"
        elif line_totals[0] < line_totals[1]:
            gt_answer_total_higher = target_line_labels[1]
            gt_mask_total_higher = [target_line_indices[1]]
            gt_symbol_total_higher = "<"
        else:
            gt_answer_total_higher = f"They have the same total {y_axis_title}."
            gt_mask_total_higher = copy.deepcopy(target_line_indices)
            gt_symbol_total_higher = "="

        # GT answer & mask for average comparison
        if line_averages[0] > line_averages[1]:
            gt_answer_avg_higher = target_line_labels[0]
            gt_mask_avg_higher = [target_line_indices[0]]
            gt_symbol_avg_higher = ">"
        elif line_averages[0] < line_averages[1]:
            gt_answer_avg_higher = target_line_labels[1]
            gt_mask_avg_higher = [target_line_indices[1]]
            gt_symbol_avg_higher = "<"
        else:
            gt_answer_avg_higher = f"They have the same average {y_axis_title}."
            gt_mask_avg_higher = copy.deepcopy(target_line_indices)
            gt_symbol_avg_higher = "="

        # Differences
        gt_answer_total_diff = abs(line_totals[0] - line_totals[1])
        gt_answer_avg_diff = abs(line_averages[0] - line_averages[1])

        # Chart QA Pool
        medium_qa_pool = {
            f"two_step__compare__total__line{target_line_indices[0]+1}_vs_line{target_line_indices[1]+1}__higher": {
                "question": [
                    f"Comparing between {target_line_labels[0]} and {target_line_labels[1]}, which has a higher total {y_axis_title}?",
                    f"Comparing between {target_line_labels[0]} and {target_line_labels[1]}, which has a larger total {y_axis_title}?",
                    f"Between {target_line_labels[0]} and {target_line_labels[1]}, which {line_category['singular']} has a higher total {y_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to calculate the total {y_axis_title} for each {line_category['singular']}:\n- {target_line_labels[0]}: {line_totals[0]}\n- {target_line_labels[1]}: {line_totals[1]}",
                        "step_2": f"Second, I need to compare their totals to find the one with higher total {y_axis_title}:\n{target_line_labels[0]}: {line_totals[0]} {gt_symbol_total_higher} {target_line_labels[1]}: {line_totals[1]}",
                    },
                ],
                "constraint": target_line_indices,
                "answer": gt_answer_total_higher,
                "mask": {
                    "step_1": target_line_indices,
                    "step_2": gt_mask_total_higher,
                    "answer": gt_mask_total_higher,
                },
            },
            f"two_step__compare__average__line{target_line_indices[0]+1}_vs_line{target_line_indices[1]+1}__higher": {
                "question": [
                    f"Comparing between {target_line_labels[0]} and {target_line_labels[1]}, which has a higher average {y_axis_title}?",
                    f"Comparing between {target_line_labels[0]} and {target_line_labels[1]}, which has a larger average {y_axis_title}?",
                    f"Between {target_line_labels[0]} and {target_line_labels[1]}, which {line_category['singular']} has a higher average {y_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to calculate the average {y_axis_title} for each {line_category['singular']}:\n- {target_line_labels[0]}: {line_averages[0]}\n- {target_line_labels[1]}: {line_averages[1]}",
                        "step_2": f"Second, I need to compare their averages to find the one with higher average {y_axis_title}:\n{target_line_labels[0]}: {line_averages[0]} {gt_symbol_avg_higher} {target_line_labels[1]}: {line_averages[1]}",
                    },
                ],
                "constraint": target_line_indices,
                "answer": gt_answer_avg_higher,
                "mask": {
                    "step_1": target_line_indices,
                    "step_2": gt_mask_avg_higher,
                    "answer": gt_mask_avg_higher,
                },
            },
            f"two_step__compare__total__line{target_line_indices[0]+1}_vs_line{target_line_indices[1]+1}__diff": {
                "question": [
                    f"Comparing between {target_line_labels[0]} and {target_line_labels[1]}, what is their absolute difference in total {y_axis_title}?",
                    f"What is the absolute difference in total {y_axis_title} between {target_line_labels[0]} and {target_line_labels[1]}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to calculate the total {y_axis_title} for each {line_category['singular']}:\n- {target_line_labels[0]}: {line_totals[0]}\n- {target_line_labels[1]}: {line_totals[1]}",
                        "step_2": f"Second, I need to calculate their absolute difference in total {y_axis_title}:\n|{line_totals[0]} - {line_totals[1]}| = {gt_answer_total_diff}",
                    },
                ],
                "constraint": target_line_indices,
                "answer": gt_answer_total_diff,
                "mask": {
                    "step_1": target_line_indices,
                    "step_2": target_line_indices,
                    "answer": target_line_indices,
                },
            },
        }

        return medium_qa_pool

    def _two_step_sort(self, chart_metadata: Dict, target_line_indices: List, constraint: str):
        """Sort: ascending and descending"""
        x_axis_title = chart_metadata['x_label'].lower()
        y_axis_title = chart_metadata['y_label'].lower()
        line_category = copy.deepcopy(chart_metadata["line_category"])
        target_line_data = [chart_metadata["line_data"][kk] for kk in target_line_indices]
        target_line_labels = [chart_metadata["line_labels"][kk] for kk in target_line_indices]

        # Calculate totals and averages for sorting
        line_totals = [sum(line_data) for line_data in target_line_data]
        line_averages = [total / len(target_line_data[0]) for total in line_totals]

        # GT sort
        sort_total_ascending = self._sort_y_order_for_x(line_totals, target_line_labels, "ascending")
        sort_total_descending = self._sort_y_order_for_x(line_totals, target_line_labels, "descending")
        sort_avg_ascending = self._sort_y_order_for_x(line_averages, target_line_labels, "ascending")
        sort_avg_descending = self._sort_y_order_for_x(line_averages, target_line_labels, "descending")

        # Chart QA Pool
        medium_qa_pool = {
            "two_step__sort__total__ascending": {
                "question": [
                    f"If sorting all the {line_category['plural']} {constraint} in ascending order according to their total {y_axis_title}, can you help provide their label sequence in order separated with commas?",
                    f"Please sort all the {line_category['plural']} {constraint} in ascending order according to their total {y_axis_title}, and provide their sorted label sequence separated with commas.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to identify all the {line_category['plural']} {constraint}.",
                        "step_2": f"Second, I need to calculate the total {y_axis_title} for each of these {line_category['plural']}.",
                        "step_3": f"Third, I need to sort them in ascending order according to their total {y_axis_title}.",
                    },
                ],
                "constraint": constraint,
                "answer": sort_total_ascending,
                "mask": {
                    "step_1": target_line_indices,
                    "step_2": target_line_indices,
                    "step_3": target_line_indices,
                    "answer": target_line_indices,
                },
            },
            "two_step__sort__total__descending": {
                "question": [
                    f"If sorting all the {line_category['plural']} {constraint} in descending order according to their total {y_axis_title}, can you help provide their label sequence in order separated with commas?",
                    f"Please sort all the {line_category['plural']} {constraint} in descending order according to their total {y_axis_title}, and provide their sorted label sequence separated with commas.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to identify all the {line_category['plural']} {constraint}.",
                        "step_2": f"Second, I need to calculate the total {y_axis_title} for each of these {line_category['plural']}.",
                        "step_3": f"Third, I need to sort them in descending order according to their total {y_axis_title}.",
                    },
                ],
                "constraint": constraint,
                "answer": sort_total_descending,
                "mask": {
                    "step_1": target_line_indices,
                    "step_2": target_line_indices,
                    "step_3": target_line_indices,
                    "answer": target_line_indices,
                },
            },
            "two_step__sort__average__ascending": {
                "question": [
                    f"If sorting all the {line_category['plural']} {constraint} in ascending order according to their average {y_axis_title}, can you help provide their label sequence in order separated with commas?",
                    f"Please sort all the {line_category['plural']} {constraint} in ascending order according to their average {y_axis_title}, and provide their sorted label sequence separated with commas.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to identify all the {line_category['plural']} {constraint}.",
                        "step_2": f"Second, I need to calculate the average {y_axis_title} for each of these {line_category['plural']}.",
                        "step_3": f"Third, I need to sort them in ascending order according to their average {y_axis_title}.",
                    },
                ],
                "constraint": constraint,
                "answer": sort_avg_ascending,
                "mask": {
                    "step_1": target_line_indices,
                    "step_2": target_line_indices,
                    "step_3": target_line_indices,
                    "answer": target_line_indices,
                },
            },
            "two_step__sort__average__descending": {
                "question": [
                    f"If sorting all the {line_category['plural']} {constraint} in descending order according to their average {y_axis_title}, can you help provide their label sequence in order separated with commas?",
                    f"Please sort all the {line_category['plural']} {constraint} in descending order according to their average {y_axis_title}, and provide their sorted label sequence separated with commas.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to identify all the {line_category['plural']} {constraint}.",
                        "step_2": f"Second, I need to calculate the average {y_axis_title} for each of these {line_category['plural']}.",
                        "step_3": f"Third, I need to sort them in descending order according to their average {y_axis_title}.",
                    },
                ],
                "constraint": constraint,
                "answer": sort_avg_descending,
                "mask": {
                    "step_1": target_line_indices,
                    "step_2": target_line_indices,
                    "step_3": target_line_indices,
                    "answer": target_line_indices,
                },
            },
        }

        return medium_qa_pool

    def _two_step_filter(self, chart_metadata: Dict, condition: List = [2, 5]):
        """Filter condition: above or below specific ranking"""
        x_axis_title = chart_metadata['x_label'].lower()
        y_axis_title = chart_metadata['y_label'].lower()
        line_category = copy.deepcopy(chart_metadata["line_category"])
        target_line_data = copy.deepcopy(chart_metadata["line_data"])
        target_line_labels = copy.deepcopy(chart_metadata["line_labels"])
        target_line_indices = [l_idx for l_idx in range(len(target_line_data))]

        # Calculate totals for ranking
        line_totals = self._compute_matrix_row_sum(target_line_data)

        # Filter
        medium_qa_pool = {}
        for line_idx in range(condition[0], min(condition[1], len(target_line_data))):
            # kth highest
            kth_highest_indices = self._find_kth_highest_index(line_totals, line_idx)
            kth_highest_value = line_totals[kth_highest_indices[0]]
            kth_highest_label = self._convert_answer_idx_to_str(target_line_labels, kth_highest_indices)

            # kth lowest
            kth_lowest_indices = self._find_kth_lowest_index(line_totals, line_idx)
            kth_lowest_value = line_totals[kth_lowest_indices[0]]
            kth_lowest_label = self._convert_answer_idx_to_str(target_line_labels, kth_lowest_indices)

            # Questions for kth highest/lowest
            medium_qa_pool[f"two_step__filter__{self._convert_idx_to_pos(line_idx)}_highest__label"] = {
                "question": [
                    f"What is the name of the {line_category['singular']} that has the {self._convert_idx_to_pos(line_idx)} highest total {y_axis_title}?",
                    f"Which {line_category['singular']} has the {self._convert_idx_to_pos(line_idx)} highest total {y_axis_title}?",
                    f"What is the name of the {line_category['singular']} with the {self._convert_idx_to_pos(line_idx)} largest total {y_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to calculate the total {y_axis_title} for each {line_category['singular']} in this chart.",
                        "step_2": f"Second, I need to compare them to identify the {line_category['singular']} with the {self._convert_idx_to_pos(line_idx)} highest total {y_axis_title}.",
                        "step_3": f"Third, I need to read its name.",
                    },
                ],
                "constraint": f"{self._convert_idx_to_pos(line_idx)} highest",
                "answer": kth_highest_label,
                "mask": {
                    "step_1": target_line_indices,
                    "step_2": kth_highest_indices,
                    "step_3": kth_highest_indices,
                    "answer": kth_highest_indices,
                },
            }

            medium_qa_pool[f"two_step__filter__{self._convert_idx_to_pos(line_idx)}_highest__value"] = {
                "question": [
                    f"What is the {self._convert_idx_to_pos(line_idx)} highest total {y_axis_title} among all {line_category['plural']} in this chart?",
                    f"What is the {self._convert_idx_to_pos(line_idx)} largest total {y_axis_title} among all {line_category['plural']} in this chart?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to calculate the total {y_axis_title} for each {line_category['singular']} in this chart.",
                        "step_2": f"Second, I need to compare them to identify the {self._convert_idx_to_pos(line_idx)} highest total {y_axis_title}.",
                    },
                ],
                "constraint": f"{self._convert_idx_to_pos(line_idx)} highest",
                "answer": kth_highest_value,
                "mask": {
                    "step_1": target_line_indices,
                    "step_2": kth_highest_indices,
                    "answer": kth_highest_indices,
                },
            }

            medium_qa_pool[f"two_step__filter__{self._convert_idx_to_pos(line_idx)}_lowest__label"] = {
                "question": [
                    f"What is the name of the {line_category['singular']} that has the {self._convert_idx_to_pos(line_idx)} lowest total {y_axis_title}?",
                    f"Which {line_category['singular']} has the {self._convert_idx_to_pos(line_idx)} lowest total {y_axis_title}?",
                    f"What is the name of the {line_category['singular']} with the {self._convert_idx_to_pos(line_idx)} smallest total {y_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to calculate the total {y_axis_title} for each {line_category['singular']} in this chart.",
                        "step_2": f"Second, I need to compare them to identify the {line_category['singular']} with the {self._convert_idx_to_pos(line_idx)} lowest total {y_axis_title}.",
                        "step_3": f"Third, I need to read its name.",
                    },
                ],
                "constraint": f"{self._convert_idx_to_pos(line_idx)} lowest",
                "answer": kth_lowest_label,
                "mask": {
                    "step_1": target_line_indices,
                    "step_2": kth_lowest_indices,
                    "step_3": kth_lowest_indices,
                    "answer": kth_lowest_indices,
                },
            }

            medium_qa_pool[f"two_step__filter__{self._convert_idx_to_pos(line_idx)}_lowest__value"] = {
                "question": [
                    f"What is the {self._convert_idx_to_pos(line_idx)} lowest total {y_axis_title} among all {line_category['plural']} in this chart?",
                    f"What is the {self._convert_idx_to_pos(line_idx)} smallest total {y_axis_title} among all {line_category['plural']} in this chart?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to calculate the total {y_axis_title} for each {line_category['singular']} in this chart.",
                        "step_2": f"Second, I need to compare them to identify the {self._convert_idx_to_pos(line_idx)} lowest total {y_axis_title}.",
                    },
                ],
                "constraint": f"{self._convert_idx_to_pos(line_idx)} lowest",
                "answer": kth_lowest_value,
                "mask": {
                    "step_1": target_line_indices,
                    "step_2": kth_lowest_indices,
                    "answer": kth_lowest_indices,
                },
            }

        return medium_qa_pool

    def _two_step_threshold(self, chart_metadata: Dict):
        """Threshold: above / below mean"""
        x_axis_title = chart_metadata['x_label'].lower()
        y_axis_title = chart_metadata['y_label'].lower()
        line_category = copy.deepcopy(chart_metadata["line_category"])
        target_line_data = copy.deepcopy(chart_metadata["line_data"])
        target_line_labels = copy.deepcopy(chart_metadata["line_labels"])
        target_line_indices = [l_idx for l_idx in range(len(target_line_data))]

        # Calculate totals and overall mean
        line_totals = self._compute_matrix_row_sum(target_line_data)
        overall_mean = sum(line_totals) / len(line_totals)

        # Above & below count
        above_mean_num, below_mean_num = 0, 0
        above_mean_indices, below_mean_indices = [], []
        
        for idx, total in enumerate(line_totals):
            if total > overall_mean:
                above_mean_num += 1
                above_mean_indices.append(idx)
            elif total < overall_mean:
                below_mean_num += 1
                below_mean_indices.append(idx)

        # Chart QA Pool
        medium_qa_pool = {
            "two_step__threshold__above_mean": {
                "question": [
                    f"How many {line_category['plural']} have their total {y_axis_title} above the average total {y_axis_title} of all {line_category['plural']}?",
                    f"Please help count the number of {line_category['plural']} whose total {y_axis_title} are above the average total {y_axis_title} of all {line_category['plural']}?",
                    f"How many {line_category['plural']} have their total {y_axis_title} above the mean total {y_axis_title} of all {line_category['plural']}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to calculate the total {y_axis_title} for each {line_category['singular']} in this chart.",
                        "step_2": f"Second, I need to compute the average total {y_axis_title} of all {line_category['plural']}: {overall_mean}",
                        "step_3": f"Third, I need to count the number of {line_category['plural']} whose total {y_axis_title} is higher than {overall_mean}.",
                    },
                ],
                "constraint": "above mean",
                "answer": above_mean_num,
                "mask": {
                    "step_1": target_line_indices,
                    "step_2": target_line_indices,
                    "step_3": above_mean_indices,
                    "answer": above_mean_indices,
                },
            },
            "two_step__threshold__below_mean": {
                "question": [
                    f"How many {line_category['plural']} have their total {y_axis_title} below the average total {y_axis_title} of all {line_category['plural']}?",
                    f"Please help count the number of {line_category['plural']} whose total {y_axis_title} are below the average total {y_axis_title} of all {line_category['plural']}?",
                    f"How many {line_category['plural']} have their total {y_axis_title} below the mean total {y_axis_title} of all {line_category['plural']}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to calculate the total {y_axis_title} for each {line_category['singular']} in this chart.",
                        "step_2": f"Second, I need to compute the average total {y_axis_title} of all {line_category['plural']}: {overall_mean}",
                        "step_3": f"Third, I need to count the number of {line_category['plural']} whose total {y_axis_title} is lower than {overall_mean}.",
                    },
                ],
                "constraint": "below mean",
                "answer": below_mean_num,
                "mask": {
                    "step_1": target_line_indices,
                    "step_2": target_line_indices,
                    "step_3": below_mean_indices,
                    "answer": below_mean_indices,
                },
            },
        }

        return medium_qa_pool


    ############################################################
    #                     Multi-step Operator
    ############################################################

    def _multi_step_threshold(self, chart_metadata: Dict):
        """Threshold: above / below mean, differences"""
        x_axis_title = chart_metadata['x_label'].lower()
        y_axis_title = chart_metadata['y_label'].lower()
        line_category = copy.deepcopy(chart_metadata["line_category"])
        target_line_data = copy.deepcopy(chart_metadata["line_data"])
        target_line_labels = copy.deepcopy(chart_metadata["line_labels"])
        target_line_indices = [l_idx for l_idx in range(len(target_line_data))]

        # Calculate totals and overall mean
        line_totals = self._compute_matrix_row_sum(target_line_data)
        overall_mean = sum(line_totals) / len(line_totals)

        # Above & below analysis
        above_mean_indices, below_mean_indices = [], []
        above_mean_totals, below_mean_totals = [], []
        
        for idx, total in enumerate(line_totals):
            if total > overall_mean:
                above_mean_indices.append(idx)
                above_mean_totals.append(total)
            elif total < overall_mean:
                below_mean_indices.append(idx)
                below_mean_totals.append(total)

        # Calculate statistics for subgroups
        above_mean_sum = sum(above_mean_totals) if above_mean_totals else 0
        below_mean_sum = sum(below_mean_totals) if below_mean_totals else 0
        above_mean_avg = above_mean_sum / len(above_mean_totals) if above_mean_totals else 0
        below_mean_avg = below_mean_sum / len(below_mean_totals) if below_mean_totals else 0

        # Find extrema within subgroups
        if above_mean_totals:
            max_above_mean_value = max(above_mean_totals)
            min_above_mean_value = min(above_mean_totals)
            max_above_mean_idx = above_mean_indices[above_mean_totals.index(max_above_mean_value)]
            min_above_mean_idx = above_mean_indices[above_mean_totals.index(min_above_mean_value)]
            max_above_mean_label = target_line_labels[max_above_mean_idx]
            min_above_mean_label = target_line_labels[min_above_mean_idx]
        
        if below_mean_totals:
            max_below_mean_value = max(below_mean_totals)
            min_below_mean_value = min(below_mean_totals)
            max_below_mean_idx = below_mean_indices[below_mean_totals.index(max_below_mean_value)]
            min_below_mean_idx = below_mean_indices[below_mean_totals.index(min_below_mean_value)]
            max_below_mean_label = target_line_labels[max_below_mean_idx]
            min_below_mean_label = target_line_labels[min_below_mean_idx]

        # Differences
        sum_diff = abs(above_mean_sum - below_mean_sum)
        mean_diff = abs(above_mean_avg - below_mean_avg)

        # Chart QA Pool
        hard_qa_pool = {}
        
        if above_mean_totals:
            hard_qa_pool["multi_step__threshold__above_mean__max__value"] = {
                "question": [
                    f"What is the highest total {y_axis_title} among {line_category['plural']} that have their total {y_axis_title} above the average total {y_axis_title} of all {line_category['plural']}?",
                    f"Among {line_category['plural']} whose total {y_axis_title} are above the average total {y_axis_title} of all {line_category['plural']}, what is the highest total {y_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to calculate the total {y_axis_title} for each {line_category['singular']} in this chart.",
                        "step_2": f"Second, I need to compute the average total {y_axis_title} of all {line_category['plural']}: {overall_mean}",
                        "step_3": f"Third, I need to find all the {line_category['plural']} whose total {y_axis_title} is higher than {overall_mean}.",
                        "step_4": f"Fourth, I need to identify the {line_category['singular']} with the highest total {y_axis_title} among these {line_category['plural']}.",
                    },
                ],
                "constraint": "max value among lines above mean",
                "answer": max_above_mean_value,
                "mask": {
                    "step_1": target_line_indices,
                    "step_2": target_line_indices,
                    "step_3": above_mean_indices,
                    "step_4": [max_above_mean_idx],
                    "answer": [max_above_mean_idx],
                },
            }

            hard_qa_pool["multi_step__threshold__above_mean__max__label"] = {
                "question": [
                    f"What is the name of the {line_category['singular']} that has the highest total {y_axis_title} among {line_category['plural']} that have their total {y_axis_title} above the average total {y_axis_title} of all {line_category['plural']}?",
                    f"Among {line_category['plural']} whose total {y_axis_title} are above the average total {y_axis_title} of all {line_category['plural']}, what is the name of the {line_category['singular']} that has the highest total {y_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to calculate the total {y_axis_title} for each {line_category['singular']} in this chart.",
                        "step_2": f"Second, I need to compute the average total {y_axis_title} of all {line_category['plural']}: {overall_mean}",
                        "step_3": f"Third, I need to find all the {line_category['plural']} whose total {y_axis_title} is higher than {overall_mean}.",
                        "step_4": f"Fourth, I need to identify the {line_category['singular']} with the highest total {y_axis_title} among these {line_category['plural']}.",
                        "step_5": f"Fifth, I need to read its name.",
                    },
                ],
                "constraint": "label of max value among lines above mean",
                "answer": max_above_mean_label,
                "mask": {
                    "step_1": target_line_indices,
                    "step_2": target_line_indices,
                    "step_3": above_mean_indices,
                    "step_4": [max_above_mean_idx],
                    "step_5": [max_above_mean_idx],
                    "answer": [max_above_mean_idx],
                },
            }

        if below_mean_totals:
            hard_qa_pool["multi_step__threshold__below_mean__max__value"] = {
                "question": [
                    f"What is the highest total {y_axis_title} among {line_category['plural']} that have their total {y_axis_title} below the average total {y_axis_title} of all {line_category['plural']}?",
                    f"Among {line_category['plural']} whose total {y_axis_title} are below the average total {y_axis_title} of all {line_category['plural']}, what is the highest total {y_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to calculate the total {y_axis_title} for each {line_category['singular']} in this chart.",
                        "step_2": f"Second, I need to compute the average total {y_axis_title} of all {line_category['plural']}: {overall_mean}",
                        "step_3": f"Third, I need to find all the {line_category['plural']} whose total {y_axis_title} is lower than {overall_mean}.",
                        "step_4": f"Fourth, I need to identify the {line_category['singular']} with the highest total {y_axis_title} among these {line_category['plural']}.",
                    },
                ],
                "constraint": "max value among lines below mean",
                "answer": max_below_mean_value,
                "mask": {
                    "step_1": target_line_indices,
                    "step_2": target_line_indices,
                    "step_3": below_mean_indices,
                    "step_4": [max_below_mean_idx],
                    "answer": [max_below_mean_idx],
                },
            }

        if above_mean_totals and below_mean_totals:
            hard_qa_pool["multi_step__threshold__mean__sum_diff"] = {
                "question": [
                    f"What is the absolute difference between the total {y_axis_title} of {line_category['plural']} above the average and those below it?",
                    f"What is the absolute value of the difference between the total {y_axis_title} for {line_category['plural']} above the average and those below the average?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to calculate the total {y_axis_title} for each {line_category['singular']} in this chart.",
                        "step_2": f"Second, I need to compute the average total {y_axis_title} of all {line_category['plural']}: {overall_mean}",
                        "step_3": f"Third, I need to find the first group of {line_category['plural']} whose total {y_axis_title} is higher than {overall_mean} and the second group of {line_category['plural']} whose total {y_axis_title} is lower than {overall_mean}.",
                        "step_4": f"Fourth, I need to calculate the total {y_axis_title} of these two groups respectively.",
                        "step_5": f"Fifth, I need to calculate the absolute difference between these two groups: |{above_mean_sum} - {below_mean_sum}| = {sum_diff}.",
                    },
                ],
                "constraint": "sum difference between lines above and below mean",
                "answer": sum_diff,
                "mask": {
                    "step_1": target_line_indices,
                    "step_2": target_line_indices,
                    "step_3": above_mean_indices + below_mean_indices,
                    "step_4": above_mean_indices + below_mean_indices,
                    "step_5": above_mean_indices + below_mean_indices,
                    "answer": above_mean_indices + below_mean_indices,
                },
            }

        return hard_qa_pool


    ############################################################
    #                  Chart QA Data Generator
    ############################################################

    def chart_qa_generator(self, chart_metadata: Dict):
        """Generate Chart QA data for line charts."""
        # Extract metadata
        x_axis_title = chart_metadata['x_label'].lower()
        y_axis_title = chart_metadata['y_label'].lower()
        line_category = chart_metadata["line_category"]

        # Calculate extrema for constraints
        extrema_dict = self._find_matrix_extrema_with_pos(chart_metadata["line_data"])
        min_value, max_value = extrema_dict["min_value"], extrema_dict["max_value"]

        # Calculate totals for constraints
        line_totals = self._compute_matrix_row_sum(chart_metadata["line_data"])

        # Constraint - Label
        selected_indices = [0, 2] if len(chart_metadata["line_labels"]) > 2 else [0]
        selected_line_labels = self._convert_answer_idx_to_str(chart_metadata["line_labels"], selected_indices)

        # Key: constraint, Value: line_list
        constraint_meta = {
            # Selected value constraints
            f"that have their total {y_axis_title} above the lowest while below the highest": self._filter_middle_indices(line_totals),
            f"that have their total {y_axis_title} higher than {min(line_totals)} but lower than {max(line_totals)}": self._filter_middle_indices(line_totals),
            f"whose total {y_axis_title} are above the lowest while below the highest": self._filter_middle_indices(line_totals),
            f"whose total {y_axis_title} are higher than {min(line_totals)} but lower than {max(line_totals)}": self._filter_middle_indices(line_totals),

            # Selected label constraints
            f"that have their labels among '{selected_line_labels}'": selected_indices,
            f"whose labels are one of '{selected_line_labels}'": selected_indices,
            f"among the labels '{selected_line_labels}'": selected_indices,
        }

        # (1) Statistics
        # (1.1) Easy: one-step
        aggregation_easy_qa_pool = self._one_step_statistics(chart_metadata)
        self._qa_pool_converter(qa_pool=aggregation_easy_qa_pool, curriculum_level=1)
        # (1.2) Medium: two-step
        for qa_constraint in constraint_meta:
            qa_line_list = constraint_meta[qa_constraint]
            if qa_line_list:  # Only process if there are lines matching the constraint
                aggregation_medium_qa_pool = self._two_step_statistics(chart_metadata, qa_line_list, qa_constraint)
                self._qa_pool_converter(qa_pool=aggregation_medium_qa_pool, curriculum_level=2)

        # (2) Extrema
        # (2.1) Easy: one-step
        extrema_easy_qa_pool = self._one_step_extrema(chart_metadata)
        self._qa_pool_converter(qa_pool=extrema_easy_qa_pool, curriculum_level=1)
        # (2.2) Medium: two-step
        for qa_constraint in constraint_meta:
            qa_line_list = constraint_meta[qa_constraint]
            if qa_line_list:  # Only process if there are lines matching the constraint
                extrema_medium_qa_pool = self._two_step_extrema(chart_metadata, qa_line_list, qa_constraint)
                self._qa_pool_converter(qa_pool=extrema_medium_qa_pool, curriculum_level=2)

        # (3) Compare
        # (3.1) Medium: two-step
        if len(chart_metadata["line_labels"]) >= 2:
            compare_line_list = [0, 1]  # Compare first two lines
            compare_medium_qa_pool = self._two_step_compare_two_lines(chart_metadata, compare_line_list)
            self._qa_pool_converter(qa_pool=compare_medium_qa_pool, curriculum_level=2)

        # (4) Sort
        # (4.1) Easy: one-step
        sort_easy_qa_pool = self._one_step_sort(chart_metadata)
        self._qa_pool_converter(qa_pool=sort_easy_qa_pool, curriculum_level=1)
        # (4.2) Medium: two-step
        for qa_constraint in constraint_meta:
            qa_line_list = constraint_meta[qa_constraint]
            if qa_line_list:  # Only process if there are lines matching the constraint
                sort_medium_qa_pool = self._two_step_sort(chart_metadata, qa_line_list, qa_constraint)
                self._qa_pool_converter(qa_pool=sort_medium_qa_pool, curriculum_level=2)

        # (5) Get value or label
        # (5.1) Easy: one-step
        read_easy_qa_pool = self._one_step_read(chart_metadata)
        self._qa_pool_converter(qa_pool=read_easy_qa_pool, curriculum_level=1)

        # (6) Filter & Select
        filter_condition = [1, min(4, len(chart_metadata["line_labels"]))]  # Adjust based on actual number of lines
        filter_medium_qa_pool = self._two_step_filter(chart_metadata, filter_condition)
        self._qa_pool_converter(qa_pool=filter_medium_qa_pool, curriculum_level=2)

        # (7) Threshold
        threshold_medium_qa_pool = self._two_step_threshold(chart_metadata)
        self._qa_pool_converter(qa_pool=threshold_medium_qa_pool, curriculum_level=2)

        # (8) Multi-step operator
        multi_threshold_hard_qa_pool = self._multi_step_threshold(chart_metadata)
        self._qa_pool_converter(qa_pool=multi_threshold_hard_qa_pool, curriculum_level=3)

        return self.all_qa_data_list