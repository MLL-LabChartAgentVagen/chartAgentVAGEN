import os
import json
import copy
from typing import List, Dict


class ScatterChartGenerator:
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

    def _compute_data_sum(self, data):
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

    def _convert_answer_idx_to_str(self, scatter_labels: List, ans_indices: List) -> str:
        """Convert to answer string"""
        ans_list = [scatter_labels[ans_idx] for ans_idx in ans_indices]
        return ", ".join(ans_list)

    def _convert_idx_to_pos(self, scatter_idx):
        """Convert scatter index to scatter position"""
        pos = [
            "1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th",
            "11th", "12th", "13th", "14th", "15th", "16th", "17th", "18th", "19th", "20th",
            "21st", "22nd", "23rd", "24th", "25th", "26th", "27th", "28th", "29th", "30th",
        ]
        return pos[scatter_idx]

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
        x_data_indices = [scatter_idx for scatter_idx in range(len(chart_metadata["scatter_x_data"]))]
        y_data_indices = [scatter_idx for scatter_idx in range(len(chart_metadata["scatter_y_data"]))]
        target_x_data = copy.deepcopy(chart_metadata["scatter_x_data"])
        target_y_data = copy.deepcopy(chart_metadata["scatter_y_data"])

        # Sum
        sum_x_answer = self._compute_data_sum(target_x_data)
        sum_x_reason = f"{'+'.join([str(ddd) for ddd in target_x_data])} = {sum_x_answer}"
        sum_y_answer = self._compute_data_sum(target_y_data)
        sum_y_reason = f"{'+'.join([str(ddd) for ddd in target_y_data])} = {sum_y_answer}"

        # Mean
        mean_x_answer = sum_x_answer / len(x_data_indices)
        mean_x_reason = f"{'+'.join([str(ddd) for ddd in target_x_data])}/{len(x_data_indices)} = {sum_x_answer}/{len(x_data_indices)} = {mean_x_answer}"
        mean_y_answer = sum_y_answer / len(y_data_indices)
        mean_y_reason = f"{'+'.join([str(ddd) for ddd in target_y_data])}/{len(y_data_indices)} = {sum_y_answer}/{len(y_data_indices)} = {mean_y_answer}"

        # Median
        median_x_value, median_x_indices = self._compute_data_median(target_x_data)
        median_y_value, median_y_indices = self._compute_data_median(target_y_data)

        # Count
        count_answer = len(x_data_indices)
        
        # Chart QA Pool
        easy_qa_pool = {
            "one_step__statistics__sum_x": {
                "question": [
                    f"What is the total {x_axis_title} for all the scatters in this chart?",
                    f"For all the scatters in this chart, what is the sum of their {x_axis_title}?",
                    f"Can you help calculate the sum of {x_axis_title} for all the scatters in this chart?",
                    f"Please compute the sum of {x_axis_title} for all the scatters in this chart.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {x_axis_title} of each scatter point in this chart.",
                        "step_2": f"Second, I need to sum the up to calculate the total {x_axis_title} of all the scatters, which should be: {sum_x_reason}.",
                    },
                ],
                "constraint": None,
                "answer": sum_x_answer,
                "mask": {
                    "step_1": x_data_indices,
                    "step_2": x_data_indices,
                    "answer": x_data_indices,
                },
            },
            "one_step__statistics__sum_y": {
                "question": [
                    f"What is the total {y_axis_title} for all the scatters in this chart?",
                    f"For all the scatters in this chart, what is the sum of their {y_axis_title}?",
                    f"Can you help calculate the sum of {y_axis_title} for all the scatters in this chart?",
                    f"Please compute the sum of {y_axis_title} for all the scatters in this chart.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of each scatter point in this chart.",
                        "step_2": f"Second, I need to sum the up to calculate the total {y_axis_title} of all the scatters, which should be: {sum_y_reason}.",
                    },
                ],
                "constraint": None,
                "answer": sum_y_answer,
                "mask": {
                    "step_1": y_data_indices,
                    "step_2": y_data_indices,
                    "answer": y_data_indices,
                },
            },
            "one_step__statistics__mean_x": {
                "question": [
                    f"What is the mean {x_axis_title} of all the scatters in this chart? Please round to two decimal places.",
                    f"For all the scatters in this chart, what is their mean {x_axis_title}? Please round to two decimal places.",
                    f"Can you help calculate the mean {x_axis_title} of all the scatters in this chart? Please round to two decimal places.",
                    f"Please compute the mean {x_axis_title} of all the scatters in this chart. Please round to two decimal places.",
                    f"What is the average {x_axis_title} of all the scatters in this chart? Please round to two decimal places.",
                    f"For all the scatters in this chart, what is their average {x_axis_title}? Please round to two decimal places.",
                    f"Can you help calculate the average {x_axis_title} of all the scatters in this chart? Please round to two decimal places.",
                    f"Please compute the average {x_axis_title} of all the scatters in this chart. Please round to two decimal places.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {x_axis_title} of each scatters in this chart.",
                        "step_2": f"Second, I need to calculate the mean {x_axis_title} of all the scatters, which should be: {mean_x_reason}.",
                    },
                ],
                "constraint": None,
                "answer": mean_x_answer,
                "mask": {
                    "step_1": x_data_indices,
                    "step_2": x_data_indices,
                    "answer": x_data_indices,
                },
            },
            "one_step__statistics__mean_y": {
                "question": [
                    f"What is the mean {y_axis_title} of all the scatters in this chart? Please round to two decimal places.",
                    f"For all the scatters in this chart, what is their mean {y_axis_title}? Please round to two decimal places.",
                    f"Can you help calculate the mean {y_axis_title} of all the scatters in this chart? Please round to two decimal places.",
                    f"Please compute the mean {y_axis_title} of all the scatters in this chart. Please round to two decimal places.",
                    f"What is the average {y_axis_title} of all the scatters in this chart? Please round to two decimal places.",
                    f"For all the scatters in this chart, what is their average {y_axis_title}? Please round to two decimal places.",
                    f"Can you help calculate the average {y_axis_title} of all the scatters in this chart? Please round to two decimal places.",
                    f"Please compute the average {y_axis_title} of all the scatters in this chart. Please round to two decimal places.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of each scatters in this chart.",
                        "step_2": f"Second, I need to calculate the mean {y_axis_title} of all the scatters, which should be: {mean_y_reason}.",
                    },
                ],
                "constraint": None,
                "answer": mean_y_answer,
                "mask": {
                    "step_1": y_data_indices,
                    "step_2": y_data_indices,
                    "answer": y_data_indices,
                },
            },
            "one_step__statistics__median_x": {
                "question": [
                    f"What is the median value of {x_axis_title} among all the scatters in this chart?",
                    f"For all the scatters in this chart, what is the median value of their {x_axis_title}?",
                    f"Can you help calculate the median value of {x_axis_title} for all the scatters in this chart?",
                    f"Please compute the median value of {x_axis_title} for all the scatters in this chart.",
                    f"What is the median {x_axis_title} among all the scatters in this chart?",
                    f"For all the scatters in this chart, what is the median of their {x_axis_title}?",
                    f"Can you help calculate the median {x_axis_title} for all the scatters in this chart?",
                    f"Please compute the median {x_axis_title} for all the scatters in this chart.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {x_axis_title} of all the scatters in this chart.",
                        "step_2": f"Second, I need to calculate the median {x_axis_title} of all the scatters.",
                    },
                ],
                "constraint": None,
                "answer": median_x_value,
                "mask": {
                    "step_1": x_data_indices,
                    "step_2": median_x_indices,
                    "answer": median_x_indices,
                },
            },
            "one_step__statistics__median_y": {
                "question": [
                    f"What is the median value of {y_axis_title} among all the scatters in this chart?",
                    f"For all the scatters in this chart, what is the median value of their {y_axis_title}?",
                    f"Can you help calculate the median value of {y_axis_title} for all the scatters in this chart?",
                    f"Please compute the median value of {y_axis_title} for all the scatters in this chart.",
                    f"What is the median {y_axis_title} among all the scatters in this chart?",
                    f"For all the scatters in this chart, what is the median of their {y_axis_title}?",
                    f"Can you help calculate the median {y_axis_title} for all the scatters in this chart?",
                    f"Please compute the median {y_axis_title} for all the scatters in this chart.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of all the scatters in this chart.",
                        "step_2": f"Second, I need to calculate the median {y_axis_title} of all the scatters.",
                    },
                ],
                "constraint": None,
                "answer": median_y_value,
                "mask": {
                    "step_1": y_data_indices,
                    "step_2": median_y_indices,
                    "answer": median_y_indices,
                },
            },
            "one_step__statistics__count": {
                "question": [
                    f"How many scatters are included in this chart?",
                    f"What is the number of scatters shown in this chart?",
                    f"Please help count the total number of scatters plotted in this chart.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to count the number of scatters in this chart.",
                    },
                ],
                "constraint": None,
                "answer": count_answer,
                "mask": {
                    "step_1": x_data_indices,
                    "answer": x_data_indices,
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
        x_data_indices = [scatter_idx for scatter_idx in range(len(chart_metadata["scatter_x_data"]))]
        y_data_indices = [scatter_idx for scatter_idx in range(len(chart_metadata["scatter_y_data"]))]
        target_x_data = copy.deepcopy(chart_metadata["scatter_x_data"])
        target_y_data = copy.deepcopy(chart_metadata["scatter_y_data"])
        scatter_labels = copy.deepcopy(chart_metadata["scatter_labels"])
        
        # Value: Min & Max
        ## (1) X value extrema
        min_x_value = min(target_x_data)
        max_x_value = max(target_x_data)
        min_x_value_indices = self._idx_of_the_smallest_data(target_x_data)
        max_x_value_indices = self._idx_of_the_largest_data(target_x_data)
        min_x_labels = self._convert_answer_idx_to_str(scatter_labels, min_x_value_indices)
        max_x_labels = self._convert_answer_idx_to_str(scatter_labels, max_x_value_indices)
        ## (2) Y value extrema
        min_y_value = min(target_y_data)
        max_y_value = max(target_y_data)
        min_y_value_indices = self._idx_of_the_smallest_data(target_y_data)
        max_y_value_indices = self._idx_of_the_largest_data(target_y_data)
        min_y_labels = self._convert_answer_idx_to_str(scatter_labels, min_y_value_indices)
        max_y_labels = self._convert_answer_idx_to_str(scatter_labels, max_y_value_indices)
        
        # Chart QA Pool
        easy_qa_pool = {
            "one_step__extrema__x__value__min__value": {
                "question": [
                    f"What is lowest {x_axis_title} among all scatters in this chart?",
                    f"What is smallest {x_axis_title} among all scatters in this chart?",
                    f"Among all the scatters shown in this chart, what is lowest {x_axis_title}?",
                    f"Among all the scatters shown in this chart, what is smallest {x_axis_title}?",
                    f"Among all the scatters shown in this chart, what is the {x_axis_title} of the scatter point with the lowest {x_axis_title}?",
                    f"Among all the scatters shown in this chart, what is the {x_axis_title} of the scatter point with the smallest {x_axis_title}?",
                    f"What is the {x_axis_title} of the scatter point with the lowest {x_axis_title}?",
                    f"What is the {x_axis_title} of the scatter point with the smallest {x_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {x_axis_title} of all the scatters in this chart.",
                        "step_2": f"Second, I need to compare them to find the lowest {x_axis_title}.",
                    },
                ],
                "constraint": None,
                "answer": min_x_value,
                "mask": {
                    "step_1": x_data_indices,
                    "step_2": min_x_value_indices,
                    "answer": min_x_value_indices,
                },
            },
            "one_step__extrema__y__value__min__value": {
                "question": [
                    f"What is lowest {y_axis_title} among all scatters in this chart?",
                    f"What is smallest {y_axis_title} among all scatters in this chart?",
                    f"Among all the scatters shown in this chart, what is lowest {y_axis_title}?",
                    f"Among all the scatters shown in this chart, what is smallest {y_axis_title}?",
                    f"Among all the scatters shown in this chart, what is the {y_axis_title} of the scatter point with the lowest {y_axis_title}?",
                    f"Among all the scatters shown in this chart, what is the {y_axis_title} of the scatter point with the smallest {y_axis_title}?",
                    f"What is the {y_axis_title} of the scatter point with the lowest {y_axis_title}?",
                    f"What is the {y_axis_title} of the scatter point with the smallest {y_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of all the scatters in this chart.",
                        "step_2": f"Second, I need to compare them to find the lowest {y_axis_title}.",
                    },
                ],
                "constraint": None,
                "answer": min_y_value,
                "mask": {
                    "step_1": y_data_indices,
                    "step_2": min_y_value_indices,
                    "answer": min_y_value_indices,
                },
            },
            "one_step__extrema__x__value__max__value": {
                "question": [
                    f"What is highest {x_axis_title} among all scatters in this chart?",
                    f"What is largest {x_axis_title} among all scatters in this chart?",
                    f"Among all the scatters shown in this chart, what is highest {x_axis_title}?",
                    f"Among all the scatters shown in this chart, what is largest {x_axis_title}?",
                    f"Among all the scatters shown in this chart, what is the {x_axis_title} of the scatter point with the highest {x_axis_title}?",
                    f"Among all the scatters shown in this chart, what is the {x_axis_title} of the scatter point with the largest {x_axis_title}?",
                    f"What is the {x_axis_title} of the scatter point with the highest {x_axis_title}?",
                    f"What is the {x_axis_title} of the scatter point with the largest {x_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {x_axis_title} of all the scatters in this chart.",
                        "step_2": f"Second, I need to compare them to find the highest {x_axis_title}.",
                    },
                ],
                "constraint": None,
                "answer": max_x_value,
                "mask": {
                    "step_1": x_data_indices,
                    "step_2": max_x_value_indices,
                    "answer": max_x_value_indices,
                },
            },
            "one_step__extrema__y__value__max__value": {
                "question": [
                    f"What is highest {y_axis_title} among all scatters in this chart?",
                    f"What is largest {y_axis_title} among all scatters in this chart?",
                    f"Among all the scatters shown in this chart, what is highest {y_axis_title}?",
                    f"Among all the scatters shown in this chart, what is largest {y_axis_title}?",
                    f"Among all the scatters shown in this chart, what is the {y_axis_title} of the scatter point with the highest {y_axis_title}?",
                    f"Among all the scatters shown in this chart, what is the {y_axis_title} of the scatter point with the largest {y_axis_title}?",
                    f"What is the {y_axis_title} of the scatter point with the highest {y_axis_title}?",
                    f"What is the {y_axis_title} of the scatter point with the largest {y_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of all the scatters in this chart.",
                        "step_2": f"Second, I need to compare them to find the highest {y_axis_title}.",
                    },
                ],
                "constraint": None,
                "answer": max_y_value,
                "mask": {
                    "step_1": y_data_indices,
                    "step_2": max_y_value_indices,
                    "answer": max_y_value_indices,
                },
            },
            "one_step__extrema__x__value__min__label": {
                "question": [
                    f"What is the lable of the scatter point that has the lowest {x_axis_title} among all scatters in this chart?",
                    f"What is the lable of the scatter point that has the smallest {x_axis_title} among all scatters in this chart?",
                    f"Among all the scatters shown in this chart, what is the lable of the scatter point that has the lowest {x_axis_title}?",
                    f"Among all the scatters shown in this chart, what is the lable of the scatter point that has the smallest {x_axis_title}?",
                    f"Among all the scatters shown in this chart, what is the lable of the scatter point with the lowest {x_axis_title}?",
                    f"Among all the scatters shown in this chart, what is the lable of the scatter point with the smallest {x_axis_title}?",
                    f"What is the lable of the scatter point with the lowest {x_axis_title}?",
                    f"What is the lable of the scatter point with the smallest {x_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {x_axis_title} of all the scatters in this chart.",
                        "step_2": f"Second, I need to compare them to find the scatter point with the lowest {x_axis_title}.",
                        "step_3": f"Third, I need to identify the label of this scatter point.",
                    },
                ],
                "constraint": None,
                "answer": min_x_labels,
                "mask": {
                    "step_1": x_data_indices,
                    "step_2": min_x_value_indices,
                    "step_3": min_x_value_indices,
                    "answer": min_x_value_indices,
                },
            },
            "one_step__extrema__y__value__min__label": {
                "question": [
                    f"What is the lable of the scatter point that has the lowest {y_axis_title} among all scatters in this chart?",
                    f"What is the lable of the scatter point that has the smallest {y_axis_title} among all scatters in this chart?",
                    f"Among all the scatters shown in this chart, what is the lable of the scatter point that has the lowest {y_axis_title}?",
                    f"Among all the scatters shown in this chart, what is the lable of the scatter point that has the smallest {y_axis_title}?",
                    f"Among all the scatters shown in this chart, what is the lable of the scatter point with the lowest {y_axis_title}?",
                    f"Among all the scatters shown in this chart, what is the lable of the scatter point with the smallest {y_axis_title}?",
                    f"What is the lable of the scatter point with the lowest {y_axis_title}?",
                    f"What is the lable of the scatter point with the smallest {y_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of all the scatters in this chart.",
                        "step_2": f"Second, I need to compare them to find the scatter point with the lowest {y_axis_title}.",
                        "step_3": f"Third, I need to identify the label of this scatter point.",
                    },
                ],
                "constraint": None,
                "answer": min_y_labels,
                "mask": {
                    "step_1": y_data_indices,
                    "step_2": min_y_value_indices,
                    "step_3": min_y_value_indices,
                    "answer": min_y_value_indices,
                },
            },
            "one_step__extrema__x__value__max__label": {
                "question": [
                    f"What is the lable of the scatter point that has the highest {x_axis_title} among all scatters in this chart?",
                    f"What is the lable of the scatter point that has the largest {x_axis_title} among all scatters in this chart?",
                    f"Among all the scatters shown in this chart, what is the lable of the scatter point that has the highest {x_axis_title}?",
                    f"Among all the scatters shown in this chart, what is the lable of the scatter point that has the largest {x_axis_title}?",
                    f"Among all the scatters shown in this chart, what is the lable of the scatter point with the highest {x_axis_title}?",
                    f"Among all the scatters shown in this chart, what is the lable of the scatter point with the largest {x_axis_title}?",
                    f"What is the lable of the scatter point with the highest {x_axis_title}?",
                    f"What is the lable of the scatter point with the largest {x_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {x_axis_title} of all the scatters in this chart.",
                        "step_2": f"Second, I need to compare them to find the scatter point with the highest {x_axis_title}.",
                        "step_3": f"Third, I need to identify the label of this scatter point.",
                    },
                ],
                "constraint": None,
                "answer": max_x_labels,
                "mask": {
                    "step_1": x_data_indices,
                    "step_2": max_x_value_indices,
                    "step_3": max_x_value_indices,
                    "answer": max_x_value_indices,
                },
            },
            "one_step__extrema__y__value__max__label": {
                "question": [
                    f"What is the lable of the scatter point that has the highest {y_axis_title} among all scatters in this chart?",
                    f"What is the lable of the scatter point that has the largest {y_axis_title} among all scatters in this chart?",
                    f"Among all the scatters shown in this chart, what is the lable of the scatter point that has the highest {y_axis_title}?",
                    f"Among all the scatters shown in this chart, what is the lable of the scatter point that has the largest {y_axis_title}?",
                    f"Among all the scatters shown in this chart, what is the lable of the scatter point with the highest {y_axis_title}?",
                    f"Among all the scatters shown in this chart, what is the lable of the scatter point with the largest {y_axis_title}?",
                    f"What is the lable of the scatter point with the highest {y_axis_title}?",
                    f"What is the lable of the scatter point with the largest {y_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of all the scatters in this chart.",
                        "step_2": f"Second, I need to compare them to find the scatter point with the highest {y_axis_title}.",
                        "step_3": f"Third, I need to identify the label of this scatter point.",
                    },
                ],
                "constraint": None,
                "answer": max_y_labels,
                "mask": {
                    "step_1": y_data_indices,
                    "step_2": max_y_value_indices,
                    "step_3": max_y_value_indices,
                    "answer": max_y_value_indices,
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
        x_data_indices = [scatter_idx for scatter_idx in range(len(chart_metadata["scatter_x_data"]))]
        y_data_indices = [scatter_idx for scatter_idx in range(len(chart_metadata["scatter_y_data"]))]
        target_x_data = copy.deepcopy(chart_metadata["scatter_x_data"])
        target_y_data = copy.deepcopy(chart_metadata["scatter_y_data"])
        scatter_labels = copy.deepcopy(chart_metadata["scatter_labels"])

        # GT sort
        sort_x_ascending = self._sort_y_order_for_x(target_x_data, scatter_labels, "ascending")
        sort_x_descending = self._sort_y_order_for_x(target_x_data, scatter_labels, "descending")
        sort_y_ascending = self._sort_y_order_for_x(target_y_data, scatter_labels, "ascending")
        sort_y_descending = self._sort_y_order_for_x(target_y_data, scatter_labels, "descending")

        # Chart QA Pool
        easy_qa_pool = {
            "one_step__sort__x__ascending": {
                "question": [
                    f"If sorting all the scatters in ascending order according to their {x_axis_title}, can you help provide their label sequence in order separated with commas?",
                    f"If sorting all the scatters in ascending order according to their {x_axis_title}, can you help provide their sorted label sequence separated with commas?",
                    f"If sorting all the scatters according to their {x_axis_title} from low to high, can you help provide their label sequence in order separated with commas?",
                    f"Please sort all the given scatters in ascending order according to their {x_axis_title}, and provide their sorted label sequence separated with commas.",
                    f"Can you help sort all the given scatters in ascending order according to their {x_axis_title}, and provide their sorted label sequence separated with commas?",
                    f"Please sort all the given scatters according to their {x_axis_title} from low to high, and provide their sorted label sequence separated with commas.",
                    f"Can you help sort all the given scatters according to their {x_axis_title} from low to high, and provide their sorted label sequence separated with commas?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {x_axis_title} of all the scatters in this chart.",
                        "step_2": f"Second, I need to sort these scatter points according to their {x_axis_title} from low to high, and response the sorted sequence of their labels.",
                    },
                ],
                "constraint": None,
                "answer": sort_x_ascending,
                "mask": {
                    "step_1": x_data_indices,
                    "step_2": x_data_indices,
                    "answer": x_data_indices,
                },
            },
            "one_step__sort__y__ascending": {
                "question": [
                    f"If sorting all the scatters in ascending order according to their {y_axis_title}, can you help provide their label sequence in order separated with commas?",
                    f"If sorting all the scatters in ascending order according to their {y_axis_title}, can you help provide their sorted label sequence separated with commas?",
                    f"If sorting all the scatters according to their {y_axis_title} from low to high, can you help provide their label sequence in order separated with commas?",
                    f"Please sort all the given scatters in ascending order according to their {y_axis_title}, and provide their sorted label sequence separated with commas.",
                    f"Can you help sort all the given scatters in ascending order according to their {y_axis_title}, and provide their sorted label sequence separated with commas?",
                    f"Please sort all the given scatters according to their {y_axis_title} from low to high, and provide their sorted label sequence separated with commas.",
                    f"Can you help sort all the given scatters according to their {y_axis_title} from low to high, and provide their sorted label sequence separated with commas?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of all the scatters in this chart.",
                        "step_2": f"Second, I need to sort these scatter points according to their {y_axis_title} from low to high, and response the sorted sequence of their labels.",
                    },
                ],
                "constraint": None,
                "answer": sort_y_ascending,
                "mask": {
                    "step_1": y_data_indices,
                    "step_2": y_data_indices,
                    "answer": y_data_indices,
                },
            },
            "one_step__sort__x__descending": {
                "question": [
                    f"If sorting all the scatters in descending order according to their {x_axis_title}, can you help provide their label sequence in order separated with commas?",
                    f"If sorting all the scatters in descending order according to their {x_axis_title}, can you help provide their sorted label sequence separated with commas?",
                    f"If sorting all the scatters according to their {x_axis_title} from high to low, can you help provide their label sequence in order separated with commas?",
                    f"Please sort all the given scatters in descending order according to their {x_axis_title}, and provide their sorted label sequence separated with commas.",
                    f"Can you help sort all the given scatters in descending order according to their {x_axis_title}, and provide their sorted label sequence separated with commas?",
                    f"Please sort all the given scatters according to their {x_axis_title} from high to low, and provide their sorted label sequence separated with commas.",
                    f"Can you help sort all the given scatters according to their {x_axis_title} from high to low, and provide their sorted label sequence separated with commas?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {x_axis_title} of all the scatters in this chart.",
                        "step_2": f"Second, I need to sort these scatter points according to their {x_axis_title} from high to low, and response the sorted sequence of their labels.",
                    },
                ],
                "constraint": None,
                "answer": sort_x_descending,
                "mask": {
                    "step_1": x_data_indices,
                    "step_2": x_data_indices,
                    "answer": x_data_indices,
                },
            },
            "one_step__sort__y__descending": {
                "question": [
                    f"If sorting all the scatters in descending order according to their {y_axis_title}, can you help provide their label sequence in order separated with commas?",
                    f"If sorting all the scatters in descending order according to their {y_axis_title}, can you help provide their sorted label sequence separated with commas?",
                    f"If sorting all the scatters according to their {y_axis_title} from high to low, can you help provide their label sequence in order separated with commas?",
                    f"Please sort all the given scatters in descending order according to their {y_axis_title}, and provide their sorted label sequence separated with commas.",
                    f"Can you help sort all the given scatters in descending order according to their {y_axis_title}, and provide their sorted label sequence separated with commas?",
                    f"Please sort all the given scatters according to their {y_axis_title} from high to low, and provide their sorted label sequence separated with commas.",
                    f"Can you help sort all the given scatters according to their {y_axis_title} from high to low, and provide their sorted label sequence separated with commas?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of all the scatters in this chart.",
                        "step_2": f"Second, I need to sort these scatter points according to their {y_axis_title} from high to low, and response the sorted sequence of their labels.",
                    },
                ],
                "constraint": None,
                "answer": sort_y_descending,
                "mask": {
                    "step_1": y_data_indices,
                    "step_2": y_data_indices,
                    "answer": y_data_indices,
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
        x_data_indices = [scatter_idx for scatter_idx in range(len(chart_metadata["scatter_x_data"]))]
        y_data_indices = [scatter_idx for scatter_idx in range(len(chart_metadata["scatter_y_data"]))]
        target_x_data = copy.deepcopy(chart_metadata["scatter_x_data"])
        target_y_data = copy.deepcopy(chart_metadata["scatter_y_data"])
        scatter_labels = copy.deepcopy(chart_metadata["scatter_labels"])

        # Chart QA Pool
        easy_qa_pool = {}

        # X axis
        for data_idx in range(len(target_x_data)):
            gt_scatter_value = target_x_data[data_idx]
            gt_scatter_label = scatter_labels[data_idx]
            
            # (1) Read - Value
            easy_qa_pool[f"one_step__read__value__scatter_{data_idx+1}"] = {
                "question": [
                    f"What is the {x_axis_title} of {gt_scatter_label}?",
                    f"What is the {x_axis_title} of the scatter point representing '{gt_scatter_label}'?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to find the scatter point representing '{gt_scatter_label}'",
                        "step_2": f"Second, I need to read its {x_axis_title}.",
                    },
                ],
                "constraint": None,
                "answer": gt_scatter_value,
                "mask": {
                    "step_1": [data_idx],
                    "step_2": [data_idx],
                    "answer": [data_idx],
                },
            }

            # (2) Read - Label
            easy_qa_pool[f"one_step__read__label__scatter_{data_idx+1}"] = {
                "question": [
                    f"What is the label of the scatter point whose {x_axis_title} is {gt_scatter_value}?",
                    f"What is the label of the scatter point with its {x_axis_title} equal to {gt_scatter_value}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to identify the scatter point whose {x_axis_title} is {gt_scatter_value}.",
                        "step_2": f"Second, I need to read its label.",
                    },
                ],
                "constraint": None,
                "answer": gt_scatter_label,
                "mask": {
                    "step_1": [data_idx],
                    "step_2": [data_idx],
                    "answer": [data_idx],
                },
            }

        return easy_qa_pool

    ############################################################
    #                     Two-step Operator
    ############################################################

    def _two_step_statistics(self, chart_metadata: Dict, target_scatter_indices: List, constraint: str):
        """
        Statistics: sum, mean, median, count
        """
        x_axis_title = chart_metadata['x_label'].lower()
        y_axis_title = chart_metadata['y_label'].lower()
        target_x_data = [chart_metadata["scatter_x_data"][scatter_idx] for scatter_idx in target_scatter_indices]
        target_y_data = [chart_metadata["scatter_y_data"][scatter_idx] for scatter_idx in target_scatter_indices]
        
        # Sum
        sum_x_answer = self._compute_data_sum(target_x_data)
        sum_x_reason = f"{'+'.join([str(ddd) for ddd in target_x_data])} = {sum_x_answer}"
        sum_y_answer = self._compute_data_sum(target_x_data)
        sum_y_reason = f"{'+'.join([str(ddd) for ddd in target_y_data])} = {sum_y_answer}"

        # Mean
        mean_x_answer = sum_x_answer / len(target_scatter_indices)
        mean_x_reason = f"{'+'.join([str(ddd) for ddd in target_x_data])}/{len(target_scatter_indices)} = {sum_x_answer}/{len(target_scatter_indices)} = {mean_x_answer}"
        mean_y_answer = sum_y_answer / len(target_scatter_indices)
        mean_y_reason = f"{'+'.join([str(ddd) for ddd in target_y_data])}/{len(target_scatter_indices)} = {sum_y_answer}/{len(target_scatter_indices)} = {mean_y_answer}"

        # Median
        median_x_value, median_x_indices = self._compute_data_median(target_x_data)
        median_y_value, median_y_indices = self._compute_data_median(target_y_data)

        # Count
        count_answer = len(target_scatter_indices)


        # Chart QA Pool
        medium_qa_pool = {
            "two_step__statistics__sum_x": {
                "question": [
                    f"What is the total {x_axis_title} for scatters {constraint}?",
                    f"For the scatters {constraint}, what is the sum of their {x_axis_title}?",
                    f"Can you help calculate the sum of {x_axis_title} for scatters {constraint}?",
                    f"Please compute the sum of {x_axis_title} for scatters {constraint}.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to identify the scatters {constraint}.",
                        "step_2": f"Second, I need to calculate their total {x_axis_title}:\n{sum_x_reason}",
                    },
                ],
                "constraint": constraint,
                "answer": sum_x_answer,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "answer": target_scatter_indices,
                },
            },
            "two_step__statistics__sum_y": {
                "question": [
                    f"What is the total {y_axis_title} for the scatters {constraint}?",
                    f"For the scatters {constraint}, what is the sum of their {y_axis_title}?",
                    f"Can you help calculate the sum of {y_axis_title} for scatters {constraint}?",
                    f"Please compute the sum of {y_axis_title} for all the scatters {constraint}.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to identify the scatters {constraint}.",
                        "step_2": f"Second, I need to calculate their total {y_axis_title}:\n{sum_y_reason}",
                    },
                ],
                "constraint": constraint,
                "answer": sum_y_answer,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "answer": target_scatter_indices,
                },
            },
            "two_step__statistics__mean_x": {
                "question": [
                    f"What is the mean {x_axis_title} for scatters {constraint}? Please round to two decimal places.",
                    f"For scatters {constraint}, what is their mean {x_axis_title}? Please round to two decimal places.",
                    f"Can you help calculate the mean {x_axis_title} for scatters {constraint}? Please round to two decimal places.",
                    f"Please compute the mean {x_axis_title} for scatters {constraint}. Please round to two decimal places.",
                    f"What is the average {x_axis_title} for scatters {constraint}? Please round to two decimal places.",
                    f"For scatters {constraint}, what is their average {x_axis_title}? Please round to two decimal places.",
                    f"Can you help calculate the average {x_axis_title} for scatters {constraint}? Please round to two decimal places.",
                    f"Please compute the average {x_axis_title} for scatters {constraint}. Please round to two decimal places.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to identify the scatters {constraint}.",
                        "step_2": f"Second, I need to calculate their average {x_axis_title}:\n{mean_x_reason}",
                    },
                ],
                "constraint": constraint,
                "answer": mean_x_answer,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "answer": target_scatter_indices,
                },
            },
            "two_step__statistics__mean_y": {
                "question": [
                    f"What is the mean {y_axis_title} for scatters {constraint}? Please round to two decimal places.",
                    f"For scatters {constraint}, what is their mean {y_axis_title}? Please round to two decimal places.",
                    f"Can you help calculate the mean {y_axis_title} for scatters {constraint}? Please round to two decimal places.",
                    f"Please compute the mean {y_axis_title} for scatters {constraint}. Please round to two decimal places.",
                    f"What is the average {y_axis_title} for scatters {constraint}? Please round to two decimal places.",
                    f"For scatters {constraint}, what is their average {y_axis_title}? Please round to two decimal places.",
                    f"Can you help calculate the average {y_axis_title} for scatters {constraint}? Please round to two decimal places.",
                    f"Please compute the average {y_axis_title} for scatters {constraint}. Please round to two decimal places.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to identify the scatters {constraint}.",
                        "step_2": f"Second, I need to calculate their average {y_axis_title}:\n{mean_y_reason}",
                    },
                ],
                "constraint": constraint,
                "answer": mean_y_answer,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "answer": target_scatter_indices,
                },
            },
            "two_step__statistics__median_x": {
                "question": [
                    f"What is the median value of {x_axis_title} for scatters {constraint}?",
                    f"For scatters {constraint}, what is the median value of their {x_axis_title}?",
                    f"Can you help calculate the median value of {x_axis_title} for scatters {constraint}?",
                    f"Please compute the median value of {x_axis_title} for scatters {constraint}.",
                    f"What is the median of {x_axis_title} for scatters {constraint}?",
                    f"For scatters {constraint}, what is the median of their {x_axis_title}?",
                    f"Can you help calculate the median of {x_axis_title} for scatters {constraint}?",
                    f"Please compute the median of {x_axis_title} for scatters {constraint}.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to identify the scatters {constraint}.",
                        "step_2": f"Second, I need to calculate their median {x_axis_title}.",
                    },
                ],
                "constraint": constraint,
                "answer": median_x_value,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": median_x_indices,
                    "answer": median_x_indices,
                },
            },
            "two_step__statistics__median_y": {
                "question": [
                    f"What is the median value of {y_axis_title} for scatters {constraint}?",
                    f"For scatters {constraint}, what is the median value of their {y_axis_title}?",
                    f"Can you help calculate the median value of {y_axis_title} for scatters {constraint}?",
                    f"Please compute the median value of {y_axis_title} for scatters {constraint}.",
                    f"What is the median of {y_axis_title} for scatters {constraint}?",
                    f"For scatters {constraint}, what is the median of their {y_axis_title}?",
                    f"Can you help calculate the median of {y_axis_title} for scatters {constraint}?",
                    f"Please compute the median of {y_axis_title} for scatters {constraint}.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to identify the scatters {constraint}.",
                        "step_2": f"Second, I need to calculate their median {y_axis_title}.",
                    },
                ],
                "constraint": constraint,
                "answer": median_y_value,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": median_y_indices,
                    "answer": median_y_indices,
                },
            },
            "two_step__statistics__count": {
                "question": [
                    f"How many scatters {constraint} are shown in this chart?",
                    f"What is the number of scatters {constraint}?",
                    f"Please help count the number of scatters {constraint}.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to find all the scatters {constraint}.",
                        "step_2": f"Second, I need to count the total number of these scatters.",
                    },
                ],
                "constraint": constraint,
                "answer": count_answer,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "answer": target_scatter_indices,
                },
            },
        }

        return medium_qa_pool

    def _two_step_extrema(self, chart_metadata: Dict, target_scatter_indices: List, constraint: str):
        """
        Extrema: value (min, max), pos (left, right, top, bottom)
        """
        x_axis_title = chart_metadata['x_label'].lower()
        y_axis_title = chart_metadata['y_label'].lower()
        target_x_data = [chart_metadata["scatter_x_data"][scatter_idx] for scatter_idx in target_scatter_indices]
        target_y_data = [chart_metadata["scatter_y_data"][scatter_idx] for scatter_idx in target_scatter_indices]
        scatter_labels = copy.deepcopy(chart_metadata["scatter_labels"])

        # Value: Min & Max
        ## (1) X value extrema
        min_x_value = min(target_x_data)
        max_x_value = max(target_x_data)
        min_x_value_indices = self._idx_of_the_smallest_data(target_x_data)
        max_x_value_indices = self._idx_of_the_largest_data(target_x_data)
        min_x_labels = self._convert_answer_idx_to_str(scatter_labels, min_x_value_indices)
        max_x_labels = self._convert_answer_idx_to_str(scatter_labels, max_x_value_indices)
        ## (2) Y value extrema
        min_y_value = min(target_y_data)
        max_y_value = max(target_y_data)
        min_y_value_indices = self._idx_of_the_smallest_data(target_y_data)
        max_y_value_indices = self._idx_of_the_largest_data(target_y_data)
        min_y_labels = self._convert_answer_idx_to_str(scatter_labels, min_y_value_indices)
        max_y_labels = self._convert_answer_idx_to_str(scatter_labels, max_y_value_indices)
        
        # Chart QA Pool
        medium_qa_pool = {
            "two_step__extrema__x__value__min__value": {
                "question": [
                    f"What is lowest {x_axis_title} among scatters {constraint}?",
                    f"What is smallest {x_axis_title} among scatters {constraint}?",
                    f"Among scatters {constraint}, what is lowest {x_axis_title}?",
                    f"Among scatters {constraint}, what is smallest {x_axis_title}?",
                    f"Among scatters {constraint}, what is the {x_axis_title} of the scatter point that has the lowest {x_axis_title}?",
                    f"Among scatters {constraint}, what is the {x_axis_title} of the scatter point that has the smallest {x_axis_title}?",
                    f"Among scatters {constraint}, what is the {x_axis_title} of the scatter point with the lowest {x_axis_title}?",
                    f"Among scatters {constraint}, what is the {x_axis_title} of the scatter point with the smallest {x_axis_title}?",
                    f"What is the {x_axis_title} of the scatter point that has the lowest {x_axis_title} among scatters {constraint}?",
                    f"What is the {x_axis_title} of the scatter point that has the smallest {x_axis_title} among scatters {constraint}?",
                    f"What is the {x_axis_title} of the scatter point with the lowest {x_axis_title} among scatters {constraint}?",
                    f"What is the {x_axis_title} of the scatter point with the smallest {x_axis_title} among scatters {constraint}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to find all the scatters {constraint}.",
                        "step_2": f"Second, I need to compare their {x_axis_title} to find the one with the lowest {x_axis_title}.",
                    },
                ],
                "constraint": constraint,
                "answer": min_x_value,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": min_x_value_indices,
                    "answer": min_x_value_indices,
                },
            },
            "two_step__extrema__y__value__min__value": {
                "question": [
                    f"What is lowest {y_axis_title} among scatters {constraint}?",
                    f"What is smallest {y_axis_title} among scatters {constraint}?",
                    f"Among scatters {constraint}, what is lowest {y_axis_title}?",
                    f"Among scatters {constraint}, what is smallest {y_axis_title}?",
                    f"Among scatters {constraint}, what is the {y_axis_title} of the scatter point that has the lowest {y_axis_title}?",
                    f"Among scatters {constraint}, what is the {y_axis_title} of the scatter point that has the smallest {y_axis_title}?",
                    f"Among scatters {constraint}, what is the {y_axis_title} of the scatter point with the lowest {y_axis_title}?",
                    f"Among scatters {constraint}, what is the {y_axis_title} of the scatter point with the smallest {y_axis_title}?",
                    f"What is the {y_axis_title} of the scatter point that has the lowest {y_axis_title} among scatters {constraint}?",
                    f"What is the {y_axis_title} of the scatter point that has the smallest {y_axis_title} among scatters {constraint}?",
                    f"What is the {y_axis_title} of the scatter point with the lowest {y_axis_title} among scatters {constraint}?",
                    f"What is the {y_axis_title} of the scatter point with the smallest {y_axis_title} among scatters {constraint}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to find all the scatters {constraint}.",
                        "step_2": f"Second, I need to compare their {y_axis_title} to find the one with the lowest {y_axis_title}.",
                    },
                ],
                "constraint": constraint,
                "answer": min_y_value,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": min_y_value_indices,
                    "answer": min_y_value_indices,
                },
            },
            "two_step__extrema__x__value__max__value": {
                "question": [
                    f"What is highest {x_axis_title} among scatters {constraint}?",
                    f"What is largest {x_axis_title} among scatters {constraint}?",
                    f"Among scatters {constraint}, what is highest {x_axis_title}?",
                    f"Among scatters {constraint}, what is largest {x_axis_title}?",
                    f"Among scatters {constraint}, what is the {x_axis_title} of the scatter point that has the highest {x_axis_title}?",
                    f"Among scatters {constraint}, what is the {x_axis_title} of the scatter point that has the largest {x_axis_title}?",
                    f"Among scatters {constraint}, what is the {x_axis_title} of the scatter point with the highest {x_axis_title}?",
                    f"Among scatters {constraint}, what is the {x_axis_title} of the scatter point with the largest {x_axis_title}?",
                    f"What is the {x_axis_title} of the scatter point that has the highest {x_axis_title} among scatters {constraint}?",
                    f"What is the {x_axis_title} of the scatter point that has the largest {x_axis_title} among scatters {constraint}?",
                    f"What is the {x_axis_title} of the scatter point with the highest {x_axis_title} among scatters {constraint}?",
                    f"What is the {x_axis_title} of the scatter point with the largest {x_axis_title} among scatters {constraint}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to identify the scatters {constraint}.",
                        "step_2": f"Second, I need to compare their {x_axis_title} to find the one with the highest {x_axis_title}.",
                    },
                ],
                "constraint": constraint,
                "answer": max_x_value,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": max_x_value_indices,
                    "answer": max_x_value_indices,
                },
            },
            "two_step__extrema__y__value__max__value": {
                "question": [
                    f"What is highest {y_axis_title} among scatters {constraint}?",
                    f"What is largest {y_axis_title} among scatters {constraint}?",
                    f"Among scatters {constraint}, what is highest {y_axis_title}?",
                    f"Among scatters {constraint}, what is largest {y_axis_title}?",
                    f"Among scatters {constraint}, what is the {y_axis_title} of the scatter point that has the highest {y_axis_title}?",
                    f"Among scatters {constraint}, what is the {y_axis_title} of the scatter point that has the largest {y_axis_title}?",
                    f"Among scatters {constraint}, what is the {y_axis_title} of the scatter point with the highest {y_axis_title}?",
                    f"Among scatters {constraint}, what is the {y_axis_title} of the scatter point with the largest {y_axis_title}?",
                    f"What is the {y_axis_title} of the scatter point that has the highest {y_axis_title} among scatters {constraint}?",
                    f"What is the {y_axis_title} of the scatter point that has the largest {y_axis_title} among scatters {constraint}?",
                    f"What is the {y_axis_title} of the scatter point with the highest {y_axis_title} among scatters {constraint}?",
                    f"What is the {y_axis_title} of the scatter point with the largest {y_axis_title} among scatters {constraint}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to identify the scatters {constraint}.",
                        "step_2": f"Second, I need to compare their {y_axis_title} to find the one with the highest {y_axis_title}.",
                    },
                ],
                "constraint": constraint,
                "answer": max_y_value,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": max_y_value_indices,
                    "answer": max_y_value_indices,
                },
            },
            "two_step__extrema__x__value__min__label": {
                "question": [
                    f"What is the label of the scatter point that has the lowest {x_axis_title} among scatters {constraint}?",
                    f"What is the label of the scatter point that has the smallest {x_axis_title} among scatters {constraint}?",
                    f"What is the label of the scatter point with the lowest {x_axis_title} among scatters {constraint}?",
                    f"What is the label of the scatter point with the smallest {x_axis_title} among scatters {constraint}?",
                    f"Among scatters {constraint}, what is the label of the scatter point that has the lowest {x_axis_title}?",
                    f"Among scatters {constraint}, what is the label of the scatter point that has the smallest {x_axis_title}?",
                    f"Among scatters {constraint}, what is the label of the scatter point with the lowest {x_axis_title}?",
                    f"Among scatters {constraint}, what is the label of the scatter point with the smallest {x_axis_title}?",
                    f"What is the label of the scatter point that has the lowest {x_axis_title} among scatters {constraint}?",
                    f"What is the label of the scatter point that has the smallest {x_axis_title} among scatters {constraint}?",
                    f"What is the label of the scatter point with the lowest {x_axis_title} among scatters {constraint}?",
                    f"What is the label of the scatter point with the smallest {x_axis_title} among scatters {constraint}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to find all the scatters {constraint}.",
                        "step_2": f"Second, I need to compare their {x_axis_title} to find the one with the lowest {x_axis_title}.",
                        "step_3": f"Third, I need to identify the label of this scatter point.",
                    },
                ],
                "constraint": constraint,
                "answer": min_x_labels,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": min_x_value_indices,
                    "step_3": min_x_value_indices,
                    "answer": min_x_value_indices,
                },
            },
            "two_step__extrema__y__value__min__label": {
                "question": [
                    f"What is the label of the scatter point that has the lowest {y_axis_title} among scatters {constraint}?",
                    f"What is the label of the scatter point that has the smallest {y_axis_title} among scatters {constraint}?",
                    f"What is the label of the scatter point with the lowest {y_axis_title} among scatters {constraint}?",
                    f"What is the label of the scatter point with the smallest {y_axis_title} among scatters {constraint}?",
                    f"Among scatters {constraint}, what is the label of the scatter point that has the lowest {y_axis_title}?",
                    f"Among scatters {constraint}, what is the label of the scatter point that has the smallest {y_axis_title}?",
                    f"Among scatters {constraint}, what is the label of the scatter point with the lowest {y_axis_title}?",
                    f"Among scatters {constraint}, what is the label of the scatter point with the smallest {y_axis_title}?",
                    f"What is the label of the scatter point that has the lowest {y_axis_title} among scatters {constraint}?",
                    f"What is the label of the scatter point that has the smallest {y_axis_title} among scatters {constraint}?",
                    f"What is the label of the scatter point with the lowest {y_axis_title} among scatters {constraint}?",
                    f"What is the label of the scatter point with the smallest {y_axis_title} among scatters {constraint}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to find all the scatters {constraint}.",
                        "step_2": f"Second, I need to compare their {y_axis_title} to find the one with the lowest {y_axis_title}.",
                        "step_3": f"Third, I need to identify the label of this scatter point.",
                    },
                ],
                "constraint": constraint,
                "answer": min_y_labels,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": min_y_value_indices,
                    "step_3": min_y_value_indices,
                    "answer": min_y_value_indices,
                },
            },
            "two_step__extrema__x__value__max__label": {
                "question": [
                    f"What is the label of the scatter point that has the highest {x_axis_title} among scatters {constraint}?",
                    f"What is the label of the scatter point that has the largest {x_axis_title} among scatters {constraint}?",
                    f"What is the label of the scatter point with the highest {x_axis_title} among scatters {constraint}?",
                    f"What is the label of the scatter point with the largest {x_axis_title} among scatters {constraint}?",
                    f"Among scatters {constraint}, what is the label of the scatter point that has the highest {x_axis_title}?",
                    f"Among scatters {constraint}, what is the label of the scatter point that has the largest {x_axis_title}?",
                    f"Among scatters {constraint}, what is the label of the scatter point with the highest {x_axis_title}?",
                    f"Among scatters {constraint}, what is the label of the scatter point with the largest {x_axis_title}?",
                    f"What is the label of the scatter point that has the highest {x_axis_title} among scatters {constraint}?",
                    f"What is the label of the scatter point that has the largest {x_axis_title} among scatters {constraint}?",
                    f"What is the label of the scatter point with the highest {x_axis_title} among scatters {constraint}?",
                    f"What is the label of the scatter point with the largest {x_axis_title} among scatters {constraint}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to find all the scatters {constraint}.",
                        "step_2": f"Second, I need to compare their {x_axis_title} to find the one with the highest {x_axis_title}.",
                        "step_3": f"Third, I need to identify the label of this scatter point.",
                    },
                ],
                "constraint": constraint,
                "answer": max_x_labels,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": max_x_value_indices,
                    "step_3": max_x_value_indices,
                    "answer": max_x_value_indices,
                },
            },
            "two_step__extrema__y__value__max__label": {
                "question": [
                    f"What is the label of the scatter point that has the highest {y_axis_title} among scatters {constraint}?",
                    f"What is the label of the scatter point that has the largest {y_axis_title} among scatters {constraint}?",
                    f"What is the label of the scatter point with the highest {y_axis_title} among scatters {constraint}?",
                    f"What is the label of the scatter point with the largest {y_axis_title} among scatters {constraint}?",
                    f"Among scatters {constraint}, what is the label of the scatter point that has the highest {y_axis_title}?",
                    f"Among scatters {constraint}, what is the label of the scatter point that has the largest {y_axis_title}?",
                    f"Among scatters {constraint}, what is the label of the scatter point with the highest {y_axis_title}?",
                    f"Among scatters {constraint}, what is the label of the scatter point with the largest {y_axis_title}?",
                    f"What is the label of the scatter point that has the highest {y_axis_title} among scatters {constraint}?",
                    f"What is the label of the scatter point that has the largest {y_axis_title} among scatters {constraint}?",
                    f"What is the label of the scatter point with the highest {y_axis_title} among scatters {constraint}?",
                    f"What is the label of the scatter point with the largest {y_axis_title} among scatters {constraint}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to find all the scatters {constraint}.",
                        "step_2": f"Second, I need to compare their {y_axis_title} to find the one with the highest {y_axis_title}.",
                        "step_3": f"Third, I need to identify the label of this scatter point.",
                    },
                ],
                "constraint": constraint,
                "answer": max_y_labels,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": max_y_value_indices,
                    "step_3": max_y_value_indices,
                    "answer": max_y_value_indices,
                },
            },
        }

        return medium_qa_pool

    def _two_step_compare_two_scatters(self, chart_metadata: Dict, target_scatter_indices: List):
        """
        Compare: value, pos
        """
        assert len(target_scatter_indices) == 2 and target_scatter_indices[0] != target_scatter_indices[1]

        x_axis_title = chart_metadata['x_label'].lower()
        y_axis_title = chart_metadata['y_label'].lower()
        target_x_data = [chart_metadata["scatter_x_data"][scatter_idx] for scatter_idx in target_scatter_indices]
        target_y_data = [chart_metadata["scatter_y_data"][scatter_idx] for scatter_idx in target_scatter_indices]
        target_scatter_labels = [chart_metadata["scatter_labels"][scatter_idx] for scatter_idx in target_scatter_indices]

        # GT answer & mask

        # (1) Value - higher
        ## (1.1) X axis
        if target_x_data[0] > target_x_data[1]:
            gt_answer_x_value_higher = target_scatter_labels[0]
            gt_mask_x_value_higher = [target_scatter_indices[0]]
            gt_symbol_x_value_higher = ">"
        elif target_x_data[0] < target_x_data[1]:
            gt_answer_x_value_higher = target_scatter_labels[1]
            gt_mask_x_value_higher = [target_scatter_indices[1]]
            gt_symbol_x_value_higher = "<"
        elif target_x_data[0] == target_x_data[1]:
            gt_answer_x_value_higher = f"They have the same {x_axis_title}."
            gt_mask_x_value_higher = copy.deepcopy(target_scatter_indices)
            gt_symbol_x_value_higher = "="
        ## (1.2) Y axis
        if target_y_data[0] > target_y_data[1]:
            gt_answer_y_value_higher = target_scatter_labels[0]
            gt_mask_y_value_higher = [target_scatter_indices[0]]
            gt_symbol_y_value_higher = ">"
        elif target_y_data[0] < target_y_data[1]:
            gt_answer_y_value_higher = target_scatter_labels[1]
            gt_mask_y_value_higher = [target_scatter_indices[1]]
            gt_symbol_y_value_higher = "<"
        elif target_y_data[0] == target_y_data[1]:
            gt_answer_y_value_higher = f"They have the same {y_axis_title}."
            gt_mask_y_value_higher = copy.deepcopy(target_scatter_indices)
            gt_symbol_y_value_higher = "="

        # (2) Value - lower
        ## (2.1) X axis
        if target_x_data[0] < target_x_data[1]:
            gt_answer_x_value_lower = target_scatter_labels[0]
            gt_mask_x_value_lower = [target_scatter_indices[0]]
            gt_symbol_x_value_lower = "<"
        elif target_x_data[0] > target_x_data[1]:
            gt_answer_x_value_lower = target_scatter_labels[1]
            gt_mask_x_value_lower = [target_scatter_indices[1]]
            gt_symbol_x_value_lower = ">"
        elif target_x_data[0] == target_x_data[1]:
            gt_answer_x_value_lower = f"They have the same {x_axis_title}."
            gt_mask_x_value_lower = copy.deepcopy(target_scatter_indices)
            gt_symbol_x_value_lower = "="
        ## (2.2) Y axis
        if target_y_data[0] < target_y_data[1]:
            gt_answer_y_value_lower = target_scatter_labels[0]
            gt_mask_y_value_lower = [target_scatter_indices[0]]
            gt_symbol_y_value_lower = "<"
        elif target_y_data[0] > target_y_data[1]:
            gt_answer_y_value_lower = target_scatter_labels[1]
            gt_mask_y_value_lower = [target_scatter_indices[1]]
            gt_symbol_y_value_lower = ">"
        elif target_y_data[0] == target_y_data[1]:
            gt_answer_y_value_lower = f"They have the same {y_axis_title}."
            gt_mask_y_value_lower = copy.deepcopy(target_scatter_indices)
            gt_symbol_y_value_lower = "="

        # (3) Value - diff
        gt_answer_x_value_diff = abs(target_x_data[0] - target_x_data[1])
        gt_answer_y_value_diff = abs(target_y_data[0] - target_y_data[1])        
        
        # Chart QA Pool
        medium_qa_pool = {
            f"two_step__compare__x_value__scatter{target_scatter_indices[0]+1}_vs_scatter{target_scatter_indices[1]+1}__higher": {
                "question": [
                    f"Comparing between {target_scatter_labels[0]} and {target_scatter_labels[1]}, which has a higher {x_axis_title}?",
                    f"Comparing between {target_scatter_labels[0]} and {target_scatter_labels[1]}, which has a larger {x_axis_title}?",
                    f"Comparing between {target_scatter_labels[0]} and {target_scatter_labels[1]}, whose {x_axis_title} is higher?",
                    f"Comparing between {target_scatter_labels[0]} and {target_scatter_labels[1]}, wwhose {x_axis_title} is larger?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read their {x_axis_title}:\n- {target_scatter_labels[0]}: {target_x_data[0]}\n- {target_scatter_labels[1]}: {target_x_data[1]}",
                        "step_2": f"Second, I need to compare their {x_axis_title} to find the one with a higher {x_axis_title}:\n{target_scatter_labels[0]}: {target_x_data[0]} {gt_symbol_x_value_higher} {target_scatter_labels[1]}: {target_x_data[1]}",
                    },
                ],
                "constraint": target_scatter_indices,
                "answer": gt_answer_x_value_higher,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": gt_mask_x_value_higher,
                    "answer": gt_mask_x_value_higher,
                },
            },
            f"two_step__compare__y_value__scatter{target_scatter_indices[0]+1}_vs_scatter{target_scatter_indices[1]+1}__higher": {
                "question": [
                    f"Comparing between {target_scatter_labels[0]} and {target_scatter_labels[1]}, which has a higher {y_axis_title}?",
                    f"Comparing between {target_scatter_labels[0]} and {target_scatter_labels[1]}, which has a larger {y_axis_title}?",
                    f"Comparing between {target_scatter_labels[0]} and {target_scatter_labels[1]}, whose {y_axis_title} is higher?",
                    f"Comparing between {target_scatter_labels[0]} and {target_scatter_labels[1]}, wwhose {y_axis_title} is larger?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read their {y_axis_title}:\n- {target_scatter_labels[0]}: {target_y_data[0]}\n- {target_scatter_labels[1]}: {target_y_data[1]}",
                        "step_2": f"Second, I need to compare their {y_axis_title} to find the one with a higher {y_axis_title}:\n{target_scatter_labels[0]}: {target_y_data[0]} {gt_symbol_y_value_higher} {target_scatter_labels[1]}: {target_y_data[1]}",
                    },
                ],
                "constraint": target_scatter_indices,
                "answer": gt_answer_y_value_higher,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": gt_mask_y_value_higher,
                    "answer": gt_mask_y_value_higher,
                },
            },
            f"two_step__compare__x_value__scatter{target_scatter_indices[0]+1}_vs_scatter{target_scatter_indices[1]+1}__lower": {
                "question": [
                    f"Comparing between {target_scatter_labels[0]} and {target_scatter_labels[1]}, which has a lower {x_axis_title}?",
                    f"Comparing between {target_scatter_labels[0]} and {target_scatter_labels[1]}, which has a smaller {x_axis_title}?",
                    f"Comparing between {target_scatter_labels[0]} and {target_scatter_labels[1]}, whose {x_axis_title} is lower?",
                    f"Comparing between {target_scatter_labels[0]} and {target_scatter_labels[1]}, wwhose {x_axis_title} is smaller?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read their {x_axis_title}:\n- {target_scatter_labels[0]}: {target_x_data[0]}\n- {target_scatter_labels[1]}: {target_x_data[1]}",
                        "step_2": f"Second, I need to compare their {x_axis_title} to find the one with a lower {x_axis_title}:\n{target_x_data[0]} {gt_symbol_x_value_lower} {target_scatter_labels[1]}: {target_x_data[1]}",
                    },
                ],
                "constraint": target_scatter_indices,
                "answer": gt_answer_x_value_lower,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": gt_mask_x_value_lower,
                    "answer": gt_mask_x_value_lower,
                },
            },
            f"two_step__compare__y_value__scatter{target_scatter_indices[0]+1}_vs_scatter{target_scatter_indices[1]+1}__lower": {
                "question": [
                    f"Comparing between {target_scatter_labels[0]} and {target_scatter_labels[1]}, which has a lower {y_axis_title}?",
                    f"Comparing between {target_scatter_labels[0]} and {target_scatter_labels[1]}, which has a smaller {y_axis_title}?",
                    f"Comparing between {target_scatter_labels[0]} and {target_scatter_labels[1]}, whose {y_axis_title} is lower?",
                    f"Comparing between {target_scatter_labels[0]} and {target_scatter_labels[1]}, wwhose {y_axis_title} is smaller?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read their {y_axis_title}:\n- {target_scatter_labels[0]}: {target_y_data[0]}\n- {target_scatter_labels[1]}: {target_y_data[1]}",
                        "step_2": f"Second, I need to compare their {y_axis_title} to find the one with a lower {y_axis_title}:\n{target_y_data[0]} {gt_symbol_y_value_lower} {target_scatter_labels[1]}: {target_y_data[1]}",
                    },
                ],
                "constraint": target_scatter_indices,
                "answer": gt_answer_y_value_lower,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": gt_mask_y_value_lower,
                    "answer": gt_mask_y_value_lower,
                },
            },
            f"two_step__compare__x_value__scatter{target_scatter_indices[0]+1}_vs_scatter{target_scatter_indices[1]+1}__diff": {
                "question": [
                    f"Comparing between {target_scatter_labels[0]} and {target_scatter_labels[1]}, what is their absolute difference in {x_axis_title}?",
                    f"What is the absolute difference in {x_axis_title} between {target_scatter_labels[0]} and {target_scatter_labels[1]}?",
                    f"Comparing between {target_scatter_labels[0]} and {target_scatter_labels[1]}, what is their absolute value of the difference in {x_axis_title}?",
                    f"What is the absolute value of the difference in {x_axis_title} between {target_scatter_labels[0]} and {target_scatter_labels[1]}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read their {x_axis_title}:\n- {target_scatter_labels[0]}: {target_x_data[0]}\n- {target_scatter_labels[1]}: {target_x_data[1]}",
                        "step_2": f"Second, I need to calculate their absolute difference in {x_axis_title}:\n|{target_x_data[0]} - {target_x_data[1]}| = {gt_answer_x_value_diff}",
                    },
                ],
                "constraint": target_scatter_indices,
                "answer": gt_answer_x_value_diff,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "answer": target_scatter_indices,
                },
            },
            f"two_step__compare__y_value__scatter{target_scatter_indices[0]+1}_vs_scatter{target_scatter_indices[1]+1}__diff": {
                "question": [
                    f"Comparing between {target_scatter_labels[0]} and {target_scatter_labels[1]}, what is their absolute difference in {y_axis_title}?",
                    f"What is the absolute difference in {y_axis_title} between {target_scatter_labels[0]} and {target_scatter_labels[1]}?",
                    f"Comparing between {target_scatter_labels[0]} and {target_scatter_labels[1]}, what is their absolute value of the difference in {y_axis_title}?",
                    f"What is the absolute value of the difference in {y_axis_title} between {target_scatter_labels[0]} and {target_scatter_labels[1]}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read their {y_axis_title}:\n- {target_scatter_labels[0]}: {target_y_data[0]}\n- {target_scatter_labels[1]}: {target_y_data[1]}",
                        "step_2": f"Second, I need to calculate their absolute difference in {y_axis_title}:\n|{target_y_data[0]} - {target_y_data[1]}| = {gt_answer_y_value_diff}",
                    },
                ],
                "constraint": target_scatter_indices,
                "answer": gt_answer_y_value_diff,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "answer": target_scatter_indices,
                },
            },
        }

        return medium_qa_pool

    def _two_step_sort(self, chart_metadata: Dict, target_scatter_indices: List, constraint: str):
        """
        Sort: ascending and descending
        """
        x_axis_title = chart_metadata['x_label'].lower()
        y_axis_title = chart_metadata['y_label'].lower()
        target_x_data = [chart_metadata["scatter_x_data"][scatter_idx] for scatter_idx in target_scatter_indices]
        target_y_data = [chart_metadata["scatter_y_data"][scatter_idx] for scatter_idx in target_scatter_indices]
        target_scatter_labels = [chart_metadata["scatter_labels"][scatter_idx] for scatter_idx in target_scatter_indices]

        # GT sort
        sort_x_ascending = self._sort_y_order_for_x(target_x_data, target_scatter_labels, "ascending")
        sort_x_descending = self._sort_y_order_for_x(target_x_data, target_scatter_labels, "descending")
        sort_y_ascending = self._sort_y_order_for_x(target_y_data, target_scatter_labels, "ascending")
        sort_y_descending = self._sort_y_order_for_x(target_y_data, target_scatter_labels, "descending")

        # Reasoning
        read_x, read_y = "", ""
        for data_idx in range(len(target_scatter_indices)):
            read_x += f"\n- {target_scatter_labels[data_idx]}: {target_x_data[data_idx]}"
            read_y += f"\n- {target_scatter_labels[data_idx]}: {target_y_data[data_idx]}"

        # Chart QA Pool
        medium_qa_pool = {
            "two_step__sort__x__ascending": {
                "question": [
                    f"If sorting all the scatters {constraint} in ascending order according to their {x_axis_title}, can you help provide their label sequence in order separeted with commas?",
                    f"If sorting all the scatters {constraint} in ascending order according to their {x_axis_title}, can you help provide the sorted sequence of their labels separeted with commas?",
                    f"If sorting all the scatters {constraint} according to their {x_axis_title} from low to high, can you help provide their label sequence in order separeted with commas?",
                    f"If sorting all the scatters {constraint} according to their {x_axis_title} from low to high, can you help provide the sorted sequence of their labels separeted with commas?",
                    f"Please sort all the scatters {constraint} in ascending order according to their {x_axis_title}, and provide their label sequence in order separeted with commas.",
                    f"Please sort all the scatters {constraint} in ascending order according to their {x_axis_title}, and provide the sorted sequence of their labels separeted with commas.",
                    f"Can you help sort all the scatters {constraint} in ascending order according to their {x_axis_title}, and provide their label sequence in order separeted with commas?",
                    f"Can you help sort all the scatters {constraint} in ascending order according to their {x_axis_title}, and provide the sorted sequence of their labels separeted with commas?",
                    f"Please sort all the scatters {constraint} according to their {x_axis_title} from low to high, and provide their label sequence in order separeted with commas.",
                    f"Please sort all the scatters {constraint} according to their {x_axis_title} from low to high, and provide the sorted sequence of their labels separeted with commas.",
                    f"Can you help sort all the scatters {constraint} according to their {x_axis_title} from low to high, and provide their label sequence in order separeted with commas?",
                    f"Can you help sort all the scatters {constraint} according to their {x_axis_title} from low to high, and provide the sorted sequence of their labels separeted with commas?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to identify all the scatters {constraint}.",
                        "step_2": f"Second, I need to read their {x_axis_title}:{read_x}",
                        "step_3": f"Third, I need to sort them in ascending order according to their {x_axis_title}.",
                    },
                ],
                "constraint": constraint,
                "answer": sort_x_ascending,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "step_3": target_scatter_indices,
                    "answer": target_scatter_indices,
                },
            },
            "two_step__sort__y__ascending": {
                "question": [
                    f"If sorting all the scatters {constraint} in ascending order according to their {y_axis_title}, can you help provide their label sequence in order separeted with commas?",
                    f"If sorting all the scatters {constraint} in ascending order according to their {y_axis_title}, can you help provide the sorted sequence of their labels separeted with commas?",
                    f"If sorting all the scatters {constraint} according to their {y_axis_title} from low to high, can you help provide their label sequence in order separeted with commas?",
                    f"If sorting all the scatters {constraint} according to their {y_axis_title} from low to high, can you help provide the sorted sequence of their labels separeted with commas?",
                    f"Please sort all the scatters {constraint} in ascending order according to their {y_axis_title}, and provide their label sequence in order separeted with commas.",
                    f"Please sort all the scatters {constraint} in ascending order according to their {y_axis_title}, and provide the sorted sequence of their labels separeted with commas.",
                    f"Can you help sort all the scatters {constraint} in ascending order according to their {y_axis_title}, and provide their label sequence in order separeted with commas?",
                    f"Can you help sort all the scatters {constraint} in ascending order according to their {y_axis_title}, and provide the sorted sequence of their labels separeted with commas?",
                    f"Please sort all the scatters {constraint} according to their {y_axis_title} from low to high, and provide their label sequence in order separeted with commas.",
                    f"Please sort all the scatters {constraint} according to their {y_axis_title} from low to high, and provide the sorted sequence of their labels separeted with commas.",
                    f"Can you help sort all the scatters {constraint} according to their {y_axis_title} from low to high, and provide their label sequence in order separeted with commas?",
                    f"Can you help sort all the scatters {constraint} according to their {y_axis_title} from low to high, and provide the sorted sequence of their labels separeted with commas?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to identify all the scatters {constraint}.",
                        "step_2": f"Second, I need to read their {y_axis_title}:{read_y}",
                        "step_3": f"Third, I need to sort them in ascending order according to their {y_axis_title}.",
                    },
                ],
                "constraint": constraint,
                "answer": sort_y_ascending,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "step_3": target_scatter_indices,
                    "answer": target_scatter_indices,
                },
            },
            "two_step__sort__x__descending": {
                "question": [
                    f"If sorting all the scatters {constraint} in descending order according to their {x_axis_title}, can you help provide their label sequence in order separeted with commas?",
                    f"If sorting all the scatters {constraint} in descending order according to their {x_axis_title}, can you help provide the sorted sequence of their labels separeted with commas?",
                    f"If sorting all the scatters {constraint} according to their {x_axis_title} from high to low, can you help provide their label sequence in order separeted with commas?",
                    f"If sorting all the scatters {constraint} according to their {x_axis_title} from high to low, can you help provide the sorted sequence of their labels separeted with commas?",
                    f"Please sort all the scatters {constraint} in descending order according to their {x_axis_title}, and provide their label sequence in order separeted with commas.",
                    f"Please sort all the scatters {constraint} in descending order according to their {x_axis_title}, and provide the sorted sequence of their labels separeted with commas.",
                    f"Can you help sort all the scatters {constraint} in descending order according to their {x_axis_title}, and provide their label sequence in order separeted with commas?",
                    f"Can you help sort all the scatters {constraint} in descending order according to their {x_axis_title}, and provide the sorted sequence of their labels separeted with commas?",
                    f"Please sort all the scatters {constraint} according to their {x_axis_title} from high to low, and provide their label sequence in order separeted with commas.",
                    f"Please sort all the scatters {constraint} according to their {x_axis_title} from high to low, and provide the sorted sequence of their labels separeted with commas.",
                    f"Can you help sort all the scatters {constraint} according to their {x_axis_title} from high to low, and provide their label sequence in order separeted with commas?",
                    f"Can you help sort all the scatters {constraint} according to their {x_axis_title} from high to low, and provide the sorted sequence of their labels separeted with commas?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to identify all the scatters {constraint}.",
                        "step_2": f"Second, I need to read their {x_axis_title}:{read_x}",
                        "step_3": f"Third, I need to sort them in descending order according to their {x_axis_title}.",
                    },
                ],
                "constraint": constraint,
                "answer": sort_x_descending,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "step_3": target_scatter_indices,
                    "answer": target_scatter_indices,
                },
            },
            "two_step__sort__y__descending": {
                "question": [
                    f"If sorting all the scatters {constraint} in descending order according to their {y_axis_title}, can you help provide their label sequence in order separeted with commas?",
                    f"If sorting all the scatters {constraint} in descending order according to their {y_axis_title}, can you help provide the sorted sequence of their labels separeted with commas?",
                    f"If sorting all the scatters {constraint} according to their {y_axis_title} from high to low, can you help provide their label sequence in order separeted with commas?",
                    f"If sorting all the scatters {constraint} according to their {y_axis_title} from high to low, can you help provide the sorted sequence of their labels separeted with commas?",
                    f"Please sort all the scatters {constraint} in descending order according to their {y_axis_title}, and provide their label sequence in order separeted with commas.",
                    f"Please sort all the scatters {constraint} in descending order according to their {y_axis_title}, and provide the sorted sequence of their labels separeted with commas.",
                    f"Can you help sort all the scatters {constraint} in descending order according to their {y_axis_title}, and provide their label sequence in order separeted with commas?",
                    f"Can you help sort all the scatters {constraint} in descending order according to their {y_axis_title}, and provide the sorted sequence of their labels separeted with commas?",
                    f"Please sort all the scatters {constraint} according to their {y_axis_title} from high to low, and provide their label sequence in order separeted with commas.",
                    f"Please sort all the scatters {constraint} according to their {y_axis_title} from high to low, and provide the sorted sequence of their labels separeted with commas.",
                    f"Can you help sort all the scatters {constraint} according to their {y_axis_title} from high to low, and provide their label sequence in order separeted with commas?",
                    f"Can you help sort all the scatters {constraint} according to their {y_axis_title} from high to low, and provide the sorted sequence of their labels separeted with commas?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to identify all the scatters {constraint}.",
                        "step_2": f"Second, I need to read their {y_axis_title}:{read_y}",
                        "step_3": f"Third, I need to sort them in descending order according to their {y_axis_title}.",
                    },
                ],
                "constraint": constraint,
                "answer": sort_y_descending,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "step_3": target_scatter_indices,
                    "answer": target_scatter_indices,
                },
            },
        }

        return medium_qa_pool

    def _two_step_filter(self, chart_metadata: Dict, condition: List = [2, 5]):
        """
        Filter condition: above or below a specific scatter's X/Y value
        condition: the condition-th highest/lowest scatter
        """
        x_axis_title = chart_metadata['x_label'].lower()
        y_axis_title = chart_metadata['y_label'].lower()
        target_x_data = copy.deepcopy(chart_metadata["scatter_x_data"])
        target_y_data = copy.deepcopy(chart_metadata["scatter_y_data"])
        target_scatter_labels = copy.deepcopy(chart_metadata["scatter_labels"])
        target_scatter_indices = [iii for iii in range(len(target_scatter_labels))]
        
        # Reasoning
        read_x, read_y = "", ""
        for data_idx in range(len(target_scatter_labels)):
            read_x += f"\n- {target_scatter_labels[data_idx]}: {target_x_data[data_idx]}"
            read_y += f"\n- {target_scatter_labels[data_idx]}: {target_y_data[data_idx]}"

        # Filter
        medium_qa_pool = {}
        for scatter_idx in range(condition[0], condition[1]):
            # kth highest
            ## (1) X
            x_kth_highest_scatter_indices = self._find_kth_highest_index(target_x_data, scatter_idx)
            x_kth_highest_scatter_value = target_x_data[x_kth_highest_scatter_indices[0]]
            x_kth_highest_scatter_label = self._convert_answer_idx_to_str(target_scatter_labels, x_kth_highest_scatter_indices)
            ## (2) Y
            y_kth_highest_scatter_indices = self._find_kth_highest_index(target_y_data, scatter_idx)
            y_kth_highest_scatter_value = target_y_data[y_kth_highest_scatter_indices[0]]
            y_kth_highest_scatter_label = self._convert_answer_idx_to_str(target_scatter_labels, y_kth_highest_scatter_indices)

            # kth lowest
            ## (1) X
            x_kth_lowest_scatter_indices = self._find_kth_lowest_index(target_x_data, scatter_idx)
            x_kth_lowest_scatter_value = target_x_data[x_kth_lowest_scatter_indices[0]]
            x_kth_lowest_scatter_label = self._convert_answer_idx_to_str(target_scatter_labels, x_kth_lowest_scatter_indices)
            ## (2) Y
            y_kth_lowest_scatter_indices = self._find_kth_lowest_index(target_y_data, scatter_idx)
            y_kth_lowest_scatter_value = target_y_data[y_kth_lowest_scatter_indices[0]]
            y_kth_lowest_scatter_label = self._convert_answer_idx_to_str(target_scatter_labels, y_kth_lowest_scatter_indices)


            # kth highest - label
            medium_qa_pool[f"two_step__filter__x__{self._convert_idx_to_pos(scatter_idx)}_highest__label"] = {
                "question": [
                    f"What is the label of the scatter point that has the {self._convert_idx_to_pos(scatter_idx)} highest {x_axis_title}?",
                    f"What is the label of the scatter point that has the {self._convert_idx_to_pos(scatter_idx)} largest {x_axis_title}?",
                    f"What is the label of the scatter point with the {self._convert_idx_to_pos(scatter_idx)} highest {x_axis_title}?",
                    f"What is the label of the scatter point with the {self._convert_idx_to_pos(scatter_idx)} largest {x_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {x_axis_title} of each scatter point:{read_x}",
                        "step_2": f"Second, I need to compare them to identify the scatter point with the {self._convert_idx_to_pos(scatter_idx)} highest {x_axis_title}.",
                        "step_3": f"Third, I need to read its label.",
                    },
                ],
                "constraint": f"{self._convert_idx_to_pos(scatter_idx)} highest",
                "answer": x_kth_highest_scatter_label,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": x_kth_highest_scatter_indices,
                    "step_3": x_kth_highest_scatter_indices,
                    "answer": x_kth_highest_scatter_indices,
                },
            }
            medium_qa_pool[f"two_step__filter__y__{self._convert_idx_to_pos(scatter_idx)}_highest__label"] = {
                "question": [
                    f"What is the label of the scatter point that has the {self._convert_idx_to_pos(scatter_idx)} highest {y_axis_title}?",
                    f"What is the label of the scatter point that has the {self._convert_idx_to_pos(scatter_idx)} largest {y_axis_title}?",
                    f"What is the label of the scatter point with the {self._convert_idx_to_pos(scatter_idx)} highest {y_axis_title}?",
                    f"What is the label of the scatter point with the {self._convert_idx_to_pos(scatter_idx)} largest {y_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of each scatter point:{read_y}",
                        "step_2": f"Second, I need to compare them to identify the scatter point with the {self._convert_idx_to_pos(scatter_idx)} highest {y_axis_title}.",
                        "step_3": f"Third, I need to read its label.",
                    },
                ],
                "constraint": f"{self._convert_idx_to_pos(scatter_idx)} highest",
                "answer": y_kth_highest_scatter_label,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": y_kth_highest_scatter_indices,
                    "step_3": y_kth_highest_scatter_indices,
                    "answer": y_kth_highest_scatter_indices,
                },
            }

            # kth highest - value
            medium_qa_pool[f"two_step__filter__x__{self._convert_idx_to_pos(scatter_idx)}_highest__value"] = {
                "question": [
                    f"What is the {x_axis_title} of the scatter point that has the {self._convert_idx_to_pos(scatter_idx)} highest {x_axis_title}?",
                    f"What is the {x_axis_title} of the scatter point that has the {self._convert_idx_to_pos(scatter_idx)} largest {x_axis_title}?",
                    f"What is the {x_axis_title} of the scatter point with the {self._convert_idx_to_pos(scatter_idx)} highest {x_axis_title}?",
                    f"What is the {x_axis_title} of the scatter point with the {self._convert_idx_to_pos(scatter_idx)} largest {x_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {x_axis_title} of each scatter point:{read_x}",
                        "step_2": f"Second, I need to compare them to identify the {self._convert_idx_to_pos(scatter_idx)} highest {x_axis_title}.",
                    },
                ],
                "constraint": f"{self._convert_idx_to_pos(scatter_idx)} highest",
                "answer": x_kth_highest_scatter_value,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": x_kth_highest_scatter_indices,
                    "answer": x_kth_highest_scatter_indices,
                },
            }
            medium_qa_pool[f"two_step__filter__y__{self._convert_idx_to_pos(scatter_idx)}_highest__value"] = {
                "question": [
                    f"What is the {y_axis_title} of the scatter point that has the {self._convert_idx_to_pos(scatter_idx)} highest {y_axis_title}?",
                    f"What is the {y_axis_title} of the scatter point that has the {self._convert_idx_to_pos(scatter_idx)} largest {y_axis_title}?",
                    f"What is the {y_axis_title} of the scatter point with the {self._convert_idx_to_pos(scatter_idx)} highest {y_axis_title}?",
                    f"What is the {y_axis_title} of the scatter point with the {self._convert_idx_to_pos(scatter_idx)} largest {y_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of each scatter point:{read_y}",
                        "step_2": f"Second, I need to compare them to identify the {self._convert_idx_to_pos(scatter_idx)} highest {y_axis_title}.",
                    },
                ],
                "constraint": f"{self._convert_idx_to_pos(scatter_idx)} highest",
                "answer": y_kth_highest_scatter_value,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": y_kth_highest_scatter_indices,
                    "answer": y_kth_highest_scatter_indices,
                },
            }

            # kth lowest - label
            medium_qa_pool[f"two_step__filter__x__{self._convert_idx_to_pos(scatter_idx)}_lowest__label"] = {
                "question": [
                    f"What is the label of the scatter point that has the {self._convert_idx_to_pos(scatter_idx)} lowest {x_axis_title}?",
                    f"What is the label of the scatter point that has the {self._convert_idx_to_pos(scatter_idx)} smallest {x_axis_title}?",
                    f"What is the label of the scatter point with the {self._convert_idx_to_pos(scatter_idx)} lowest {x_axis_title}?",
                    f"What is the label of the scatter point with the {self._convert_idx_to_pos(scatter_idx)} smallest {x_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {x_axis_title} of each scatter point:{read_x}",
                        "step_2": f"Second, I need to compare them to identify the scatter point with the {self._convert_idx_to_pos(scatter_idx)} lowest {x_axis_title}.",
                        "step_3": f"Third, I need to read its label.",
                    },
                ],
                "constraint": f"{self._convert_idx_to_pos(scatter_idx)} lowest",
                "answer": x_kth_lowest_scatter_label,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": x_kth_lowest_scatter_indices,
                    "step_3": x_kth_lowest_scatter_indices,
                    "answer": x_kth_lowest_scatter_indices,
                },
            }
            medium_qa_pool[f"two_step__filter__y__{self._convert_idx_to_pos(scatter_idx)}_lowest__label"] = {
                "question": [
                    f"What is the label of the scatter point that has the {self._convert_idx_to_pos(scatter_idx)} lowest {y_axis_title}?",
                    f"What is the label of the scatter point that has the {self._convert_idx_to_pos(scatter_idx)} smallest {y_axis_title}?",
                    f"What is the label of the scatter point with the {self._convert_idx_to_pos(scatter_idx)} lowest {y_axis_title}?",
                    f"What is the label of the scatter point with the {self._convert_idx_to_pos(scatter_idx)} smallest {y_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of each scatter point:{read_y}",
                        "step_2": f"Second, I need to compare them to identify the scatter point with the {self._convert_idx_to_pos(scatter_idx)} lowest {y_axis_title}.",
                        "step_3": f"Third, I need to read its label.",
                    },
                ],
                "constraint": f"{self._convert_idx_to_pos(scatter_idx)} lowest",
                "answer": y_kth_lowest_scatter_label,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": y_kth_lowest_scatter_indices,
                    "step_3": y_kth_lowest_scatter_indices,
                    "answer": y_kth_lowest_scatter_indices,
                },
            }
            

            # kth lowest - value
            medium_qa_pool[f"two_step__filter__x__{self._convert_idx_to_pos(scatter_idx)}_lowest__value"] = {
                "question": [
                    f"What is the {x_axis_title} of the scatter point that has the {self._convert_idx_to_pos(scatter_idx)} lowest {x_axis_title}?",
                    f"What is the {x_axis_title} of the scatter point that has the {self._convert_idx_to_pos(scatter_idx)} smallest {x_axis_title}?",
                    f"What is the {x_axis_title} of the scatter point with the {self._convert_idx_to_pos(scatter_idx)} lowest {x_axis_title}?",
                    f"What is the {x_axis_title} of the scatter point with the {self._convert_idx_to_pos(scatter_idx)} smallest {x_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {x_axis_title} of each scatter point:{read_x}",
                        "step_2": f"Second, I need to compare them to identify the {self._convert_idx_to_pos(scatter_idx)} lowest {x_axis_title}.",
                    },
                ],
                "constraint": f"{self._convert_idx_to_pos(scatter_idx)} lowest",
                "answer": x_kth_lowest_scatter_value,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": x_kth_lowest_scatter_indices,
                    "answer": x_kth_lowest_scatter_indices,
                },
            }
            medium_qa_pool[f"two_step__filter__y__{self._convert_idx_to_pos(scatter_idx)}_lowest__value"] = {
                "question": [
                    f"What is the {y_axis_title} of the scatter point that has the {self._convert_idx_to_pos(scatter_idx)} lowest {y_axis_title}?",
                    f"What is the {y_axis_title} of the scatter point that has the {self._convert_idx_to_pos(scatter_idx)} smallest {y_axis_title}?",
                    f"What is the {y_axis_title} of the scatter point with the {self._convert_idx_to_pos(scatter_idx)} lowest {y_axis_title}?",
                    f"What is the {y_axis_title} of the scatter point with the {self._convert_idx_to_pos(scatter_idx)} smallest {y_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of each scatter point:{read_y}",
                        "step_2": f"Second, I need to compare them to identify the {self._convert_idx_to_pos(scatter_idx)} lowest {y_axis_title}.",
                    },
                ],
                "constraint": f"{self._convert_idx_to_pos(scatter_idx)} lowest",
                "answer": y_kth_lowest_scatter_value,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": y_kth_lowest_scatter_indices,
                    "answer": y_kth_lowest_scatter_indices,
                },
            }
            
        return medium_qa_pool

    def _two_step_threshold(self, chart_metadata: Dict):
        """
        Threshold: above / below mean
        """
        x_axis_title = chart_metadata['x_label'].lower()
        y_axis_title = chart_metadata['y_label'].lower()
        target_x_data = copy.deepcopy(chart_metadata["scatter_x_data"])
        target_y_data = copy.deepcopy(chart_metadata["scatter_y_data"])
        target_scatter_labels = copy.deepcopy(chart_metadata["scatter_labels"])
        target_scatter_indices = [iii for iii in range(len(target_scatter_labels))]
        
        # Sum
        x_value_sum = self._compute_data_sum(target_x_data)
        y_value_sum = self._compute_data_sum(target_y_data)

        # Mean
        x_value_mean = self._compute_data_mean(target_x_data)
        y_value_mean = self._compute_data_mean(target_y_data)

        # Reason
        read_x, read_y = "", ""
        for data_idx in range(len(target_scatter_labels)):
            read_x += f"\n- {target_scatter_labels[data_idx]}: {target_x_data[data_idx]}"
            read_y += f"\n- {target_scatter_labels[data_idx]}: {target_y_data[data_idx]}"
        reason_x_sum = f"{'+'.join([str(nn) for nn in target_x_data])} = {x_value_sum}"
        reason_y_sum = f"{'+'.join([str(nn) for nn in target_y_data])} = {y_value_sum}"
        reason_x_avg = f"{'+'.join([str(nn) for nn in target_x_data])}/{len(target_scatter_labels)} = {x_value_sum}/{len(target_scatter_labels)} = {x_value_mean}"
        reason_y_avg = f"{'+'.join([str(nn) for nn in target_y_data])}/{len(target_scatter_labels)} = {y_value_sum}/{len(target_scatter_labels)} = {y_value_mean}"

        # Above & below count
        ###### X
        x_above_mean_num, x_below_mean_num, x_scatter_idx = 0, 0, 0
        x_above_mean_indices, x_below_mean_indices = [], []
        for vv in target_x_data:
            if vv > x_value_mean:
                x_above_mean_num += 1
                x_above_mean_indices.append(x_scatter_idx)
            elif vv < x_value_mean:
                x_below_mean_num += 1
                x_below_mean_indices.append(x_scatter_idx)
            x_scatter_idx += 1
        ###### Y
        y_above_mean_num, y_below_mean_num, y_scatter_idx = 0, 0, 0
        y_above_mean_indices, y_below_mean_indices = [], []
        for vv in target_y_data:
            if vv > y_value_mean:
                y_above_mean_num += 1
                y_above_mean_indices.append(y_scatter_idx)
            elif vv < y_value_mean:
                y_below_mean_num += 1
                y_below_mean_indices.append(y_scatter_idx)
            y_scatter_idx += 1
        
        
        # Chart QA Pool
        medium_qa_pool = {
            "two_step__threshold__x__above_mean": {
                "question": [
                    f"How many scatters have their {x_axis_title} above the average {x_axis_title} of all scatters?",
                    f"Please help count the number of scatters whose {x_axis_title} are above the average {x_axis_title} of all scatters?"
                    f"How many scatters have their {x_axis_title} above the mean {x_axis_title} of all scatters?",
                    f"Please help count the number of scatters whose {x_axis_title} are above the mean {x_axis_title} of all scatters?"
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {x_axis_title} of each scatter point in this chart:{read_x}",
                        "step_2": f"Second, I need to compute the average {x_axis_title} of all scatters:\n{reason_x_avg}",
                        "step_3": f"Third, I need to count the number of scatters whose {x_axis_title} is higher than {x_value_mean}.",
                    },
                ],
                "constraint": "X - above mean",
                "answer": x_above_mean_num,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "step_3": x_above_mean_indices,
                    "answer": x_above_mean_indices,
                },
            },
            "two_step__threshold__y__above_mean": {
                "question": [
                    f"How many scatters have their {y_axis_title} above the average {y_axis_title} of all scatters?",
                    f"Please help count the number of scatters whose {y_axis_title} are above the average {y_axis_title} of all scatters?"
                    f"How many scatters have their {y_axis_title} above the mean {y_axis_title} of all scatters?",
                    f"Please help count the number of scatters whose {y_axis_title} are above the mean {y_axis_title} of all scatters?"
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of each scatter point in this chart:{read_y}",
                        "step_2": f"Second, I need to compute the average {y_axis_title} of all scatters:\n{reason_y_avg}",
                        "step_3": f"Third, I need to count the number of scatters whose {y_axis_title} is higher than {y_value_mean}.",
                    },
                ],
                "constraint": "Y - above mean",
                "answer": y_above_mean_num,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "step_3": y_above_mean_indices,
                    "answer": y_above_mean_indices,
                },
            },
            "two_step__threshold__x__below_mean": {
                "question": [
                    f"How many scatters have their {x_axis_title} below the average {x_axis_title} of all scatters?",
                    f"Please help count the number of scatters whose {x_axis_title} are below the average {x_axis_title} of all scatters?"
                    f"How many scatters have their {x_axis_title} below the mean {x_axis_title} of all scatters?",
                    f"Please help count the number of scatters whose {x_axis_title} are below the mean {x_axis_title} of all scatters?"
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {x_axis_title} of each scatter point in this chart:{read_y}",
                        "step_2": f"Second, I need to compute the average {x_axis_title} of all scatters:\n{reason_x_avg}",
                        "step_3": f"Third, I need to count the number of scatters whose {x_axis_title} is lower than {x_value_mean}.",
                    },
                ],
                "constraint": "X - below mean",
                "answer": x_below_mean_num,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "step_3": x_below_mean_indices,
                    "answer": x_below_mean_indices,
                },
            },"two_step__threshold__y__below_mean": {
                "question": [
                    f"How many scatters have their {y_axis_title} below the average {y_axis_title} of all scatters?",
                    f"Please help count the number of scatters whose {y_axis_title} are below the average {y_axis_title} of all scatters?"
                    f"How many scatters have their {y_axis_title} below the mean {y_axis_title} of all scatters?",
                    f"Please help count the number of scatters whose {y_axis_title} are below the mean {y_axis_title} of all scatters?"
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of each scatter point in this chart:{read_y}",
                        "step_2": f"Second, I need to compute the average {y_axis_title} of all scatters:\n{reason_y_avg}",
                        "step_3": f"Third, I need to count the number of scatters whose {y_axis_title} is lower than {y_value_mean}.",
                    },
                ],
                "constraint": "Y - below mean",
                "answer": y_below_mean_num,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "step_3": y_below_mean_indices,
                    "answer": y_below_mean_indices,
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
        target_x_data = copy.deepcopy(chart_metadata["scatter_x_data"])
        target_y_data = copy.deepcopy(chart_metadata["scatter_y_data"])
        target_scatter_labels = copy.deepcopy(chart_metadata["scatter_labels"])
        target_scatter_indices = [iii for iii in range(len(target_scatter_labels))]

        # Sum
        x_value_sum = self._compute_data_sum(target_x_data)
        y_value_sum = self._compute_data_sum(target_y_data)

        # Mean
        x_value_mean = self._compute_data_mean(target_x_data)
        y_value_mean = self._compute_data_mean(target_y_data)

        # Above & below count
        ###### X
        x_above_mean_num, x_below_mean_num, x_scatter_idx = 0, 0, 0
        x_above_mean_indices, x_below_mean_indices = [], []
        x_above_mean_values, x_below_mean_values = [], []
        for vv in target_x_data:
            if vv > x_value_mean:
                x_above_mean_num += 1
                x_above_mean_indices.append(x_scatter_idx)
                x_above_mean_values.append(vv)
            elif vv < x_value_mean:
                x_below_mean_num += 1
                x_below_mean_indices.append(x_scatter_idx)
                x_below_mean_values.append(vv)
            x_scatter_idx += 1
        ###### Y
        y_above_mean_num, y_below_mean_num, y_scatter_idx = 0, 0, 0
        y_above_mean_indices, y_below_mean_indices = [], []
        y_above_mean_values, y_below_mean_values = [], []
        for vv in target_y_data:
            if vv > y_value_mean:
                y_above_mean_num += 1
                y_above_mean_indices.append(y_scatter_idx)
                y_above_mean_values.append(vv)
            elif vv < y_value_mean:
                y_below_mean_num += 1
                y_below_mean_indices.append(y_scatter_idx)
                y_below_mean_values.append(vv)
            y_scatter_idx += 1
        
        # Sum sublist
        x_above_mean_value_sum = self._compute_data_sum(x_above_mean_values)
        x_below_mean_value_sum = self._compute_data_sum(x_below_mean_values)
        y_above_mean_value_sum = self._compute_data_sum(y_above_mean_values)
        y_below_mean_value_sum = self._compute_data_sum(y_below_mean_values)

        # Mean sublist
        x_above_mean_value_avg = x_above_mean_value_sum/x_above_mean_num
        x_below_mean_value_avg = x_below_mean_value_sum/x_below_mean_num
        y_above_mean_value_avg = y_above_mean_value_sum/y_above_mean_num
        y_below_mean_value_avg = y_below_mean_value_sum/y_below_mean_num
        
        # Max/min among above-mean sublist
        x_max_above_mean_value = max(x_above_mean_values)
        x_min_above_mean_value = min(x_above_mean_values)
        x_max_above_mean_value_indices = self._find_indices_in_list(target_x_data, x_max_above_mean_value)
        x_min_above_mean_value_indices = self._find_indices_in_list(target_x_data, x_min_above_mean_value)
        x_max_above_mean_label = self._convert_answer_idx_to_str(target_scatter_labels, x_max_above_mean_value_indices)
        x_min_above_mean_label = self._convert_answer_idx_to_str(target_scatter_labels, x_min_above_mean_value_indices)

        y_max_above_mean_value = max(y_above_mean_values)
        y_min_above_mean_value = min(y_above_mean_values)
        y_max_above_mean_value_indices = self._find_indices_in_list(target_y_data, y_max_above_mean_value)
        y_min_above_mean_value_indices = self._find_indices_in_list(target_y_data, y_min_above_mean_value)
        y_max_above_mean_label = self._convert_answer_idx_to_str(target_scatter_labels, y_max_above_mean_value_indices)
        y_min_above_mean_label = self._convert_answer_idx_to_str(target_scatter_labels, y_min_above_mean_value_indices)

        # Max/min among below-mean sublist
        x_max_below_mean_value = max(x_below_mean_values)
        x_min_below_mean_value = min(x_below_mean_values)
        x_max_below_mean_value_indices = self._find_indices_in_list(target_x_data, x_max_below_mean_value)
        x_min_below_mean_value_indices = self._find_indices_in_list(target_x_data, x_min_below_mean_value)
        x_max_below_mean_label = self._convert_answer_idx_to_str(target_scatter_labels, x_max_below_mean_value_indices)
        x_min_below_mean_label = self._convert_answer_idx_to_str(target_scatter_labels, x_min_below_mean_value_indices)

        y_max_below_mean_value = max(y_below_mean_values)
        y_min_below_mean_value = min(y_below_mean_values)
        y_max_below_mean_value_indices = self._find_indices_in_list(target_y_data, y_max_below_mean_value)
        y_min_below_mean_value_indices = self._find_indices_in_list(target_y_data, y_min_below_mean_value)
        y_max_below_mean_label = self._convert_answer_idx_to_str(target_scatter_labels, y_max_below_mean_value_indices)
        y_min_below_mean_label = self._convert_answer_idx_to_str(target_scatter_labels, y_min_below_mean_value_indices)

        # Difference between the sum of above-mean scatters and the sum of below-mean scatters
        x_sum_diff = x_above_mean_value_sum - x_below_mean_value_sum
        x_mean_diff = x_above_mean_value_avg - x_below_mean_value_avg
        y_sum_diff = y_above_mean_value_sum - y_below_mean_value_sum
        y_mean_diff = y_above_mean_value_avg - y_below_mean_value_avg
        
        # Reason
        read_x, read_y = "", ""
        for data_idx in range(len(target_scatter_labels)):
            read_x += f"\n- {target_scatter_labels[data_idx]}: {target_x_data[data_idx]}"
            read_y += f"\n- {target_scatter_labels[data_idx]}: {target_y_data[data_idx]}"

        reason_x_sum = f"{'+'.join([str(nn) for nn in target_x_data])} = {x_value_sum}"
        reason_x_avg = f"{'+'.join([str(nn) for nn in target_x_data])}/{len(target_scatter_labels)} = {x_value_sum}/{len(target_scatter_labels)} = {x_value_mean}"
        reason_x_above_mean_value_sum = f"{'+'.join([str(nn) for nn in x_above_mean_values])} = {x_above_mean_value_sum}"
        reason_x_above_mean_value_avg = f"({'+'.join([str(nn) for nn in x_above_mean_values])})/{x_above_mean_num} = {x_above_mean_value_sum}/{x_above_mean_num} = {x_above_mean_value_avg}"
        reason_x_below_mean_value_sum = f"{'+'.join([str(nn) for nn in x_below_mean_values])} = {x_below_mean_value_sum}"
        reason_x_below_mean_value_avg = f"({'+'.join([str(nn) for nn in x_below_mean_values])})/{x_below_mean_num} = {x_below_mean_value_sum}/{x_below_mean_num} = {x_below_mean_value_avg}"        
        
        reason_y_sum = f"{'+'.join([str(nn) for nn in target_y_data])} = {y_value_sum}"
        reason_y_avg = f"{'+'.join([str(nn) for nn in target_y_data])}/{len(target_scatter_labels)} = {y_value_sum}/{len(target_scatter_labels)} = {y_value_mean}"
        reason_y_above_mean_value_sum = f"{'+'.join([str(nn) for nn in y_above_mean_values])} = {y_above_mean_value_sum}"
        reason_y_above_mean_value_avg = f"({'+'.join([str(nn) for nn in y_above_mean_values])})/{y_above_mean_num} = {y_above_mean_value_sum}/{y_above_mean_num} = {y_above_mean_value_avg}"
        reason_y_below_mean_value_sum = f"{'+'.join([str(nn) for nn in y_below_mean_values])} = {y_below_mean_value_sum}"
        reason_y_below_mean_value_avg = f"({'+'.join([str(nn) for nn in y_below_mean_values])})/{y_below_mean_num} = {y_below_mean_value_sum}/{y_below_mean_num} = {y_below_mean_value_avg}"
        
        

        # Chart QA Pool
        hard_qa_pool = {
            "multi_step__threshold__x__above_mean__max__value": {
                "question": [
                    f"What is the highest {x_axis_title} among scatters that have their {x_axis_title} above the average {x_axis_title} of all scatters?",
                    f"Among scatters whose {x_axis_title} are above the average {x_axis_title} of all scatters, what is the highest {x_axis_title}?",
                    f"What is the highest {x_axis_title} among scatters that have their {x_axis_title} above the mean {x_axis_title} of all scatters?",
                    f"Among scatters whose {x_axis_title} are above the mean {x_axis_title} of all scatters, what is the highest {x_axis_title}?",
                    f"What is the largest {x_axis_title} among scatters that have their {x_axis_title} above the average {x_axis_title} of all scatters?",
                    f"Among scatters whose {x_axis_title} are above the average {x_axis_title} of all scatters, what is the largest {x_axis_title}?",
                    f"What is the largest {x_axis_title} among scatters that have their {x_axis_title} above the mean {x_axis_title} of all scatters?",
                    f"Among scatters whose {x_axis_title} are above the mean {x_axis_title} of all scatters, what is the largest {x_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {x_axis_title} of each scatter point in this chart:{read_x}",
                        "step_2": f"Second, I need to compute the average {x_axis_title} of all scatters:\n{reason_x_avg}",
                        "step_3": f"Third, I need to find all the scatters whose {x_axis_title} is higher than {x_value_mean}:\n{', '.join(target_scatter_labels[iii] for iii in x_above_mean_indices)}",
                        "step_4": f"Fourth, I need to identify the scatter point with the highest {x_axis_title} among these scatters.",
                    },
                ],
                "constraint": "X - max value among scatters above mean",
                "answer": x_max_above_mean_value,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "step_3": x_above_mean_indices,
                    "step_4": x_max_above_mean_value_indices,
                    "answer": x_max_above_mean_value_indices,
                },
            },
            "multi_step__threshold__y__above_mean__max__value": {
                "question": [
                    f"What is the highest {y_axis_title} among scatters that have their {y_axis_title} above the average {y_axis_title} of all scatters?",
                    f"Among scatters whose {y_axis_title} are above the average {y_axis_title} of all scatters, what is the highest {y_axis_title}?",
                    f"What is the highest {y_axis_title} among scatters that have their {y_axis_title} above the mean {y_axis_title} of all scatters?",
                    f"Among scatters whose {y_axis_title} are above the mean {y_axis_title} of all scatters, what is the highest {y_axis_title}?",
                    f"What is the largest {y_axis_title} among scatters that have their {y_axis_title} above the average {y_axis_title} of all scatters?",
                    f"Among scatters whose {y_axis_title} are above the average {y_axis_title} of all scatters, what is the largest {y_axis_title}?",
                    f"What is the largest {y_axis_title} among scatters that have their {y_axis_title} above the mean {y_axis_title} of all scatters?",
                    f"Among scatters whose {y_axis_title} are above the mean {y_axis_title} of all scatters, what is the largest {y_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of each scatter point in this chart:{read_y}",
                        "step_2": f"Second, I need to compute the average {y_axis_title} of all scatters:\n{reason_y_avg}",
                        "step_3": f"Third, I need to find all the scatters whose {y_axis_title} is higher than {y_value_mean}:\n{', '.join(target_scatter_labels[iii] for iii in y_above_mean_indices)}",
                        "step_4": f"Fourth, I need to identify the scatter point with the highest {y_axis_title} among these scatters.",
                    },
                ],
                "constraint": "Y - max value among scatters above mean",
                "answer": y_max_above_mean_value,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "step_3": y_above_mean_indices,
                    "step_4": y_max_above_mean_value_indices,
                    "answer": y_max_above_mean_value_indices,
                },
            },
            "multi_step__threshold__x__above_mean__min__value": {
                "question": [
                    f"What is the lowest {x_axis_title} among scatters that have their {x_axis_title} above the average {x_axis_title} of all scatters?",
                    f"Among scatters whose {x_axis_title} are above the average {x_axis_title} of all scatters, what is the lowest {x_axis_title}?",
                    f"What is the lowest {x_axis_title} among scatters that have their {x_axis_title} above the mean {x_axis_title} of all scatters?",
                    f"Among scatters whose {x_axis_title} are above the mean {x_axis_title} of all scatters, what is the lowest {x_axis_title}?",
                    f"What is the smallest {x_axis_title} among scatters that have their {x_axis_title} above the average {x_axis_title} of all scatters?",
                    f"Among scatters whose {x_axis_title} are above the average {x_axis_title} of all scatters, what is the smallest {x_axis_title}?",
                    f"What is the smallest {x_axis_title} among scatters that have their {x_axis_title} above the mean {x_axis_title} of all scatters?",
                    f"Among scatters whose {x_axis_title} are above the mean {x_axis_title} of all scatters, what is the smallest {x_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {x_axis_title} of each scatter point in this chart:{read_x}",
                        "step_2": f"Second, I need to compute the average {x_axis_title} of all scatters:\n{reason_x_avg}",
                        "step_3": f"Third, I need to find all the scatters whose {x_axis_title} is higher than {x_value_mean}:\n{', '.join(target_scatter_labels[iii] for iii in x_above_mean_indices)}",
                        "step_4": f"Fourth, I need to identify the scatter point with the lowest {x_axis_title} among these scatters.",
                    },
                ],
                "constraint": "X - min value among scatters above mean",
                "answer": x_min_above_mean_value,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "step_3": x_above_mean_indices,
                    "step_4": x_min_above_mean_value_indices,
                    "answer": x_min_above_mean_value_indices,
                },
            },
            "multi_step__threshold__y__above_mean__min__value": {
                "question": [
                    f"What is the lowest {y_axis_title} among scatters that have their {y_axis_title} above the average {y_axis_title} of all scatters?",
                    f"Among scatters whose {y_axis_title} are above the average {y_axis_title} of all scatters, what is the lowest {y_axis_title}?",
                    f"What is the lowest {y_axis_title} among scatters that have their {y_axis_title} above the mean {y_axis_title} of all scatters?",
                    f"Among scatters whose {y_axis_title} are above the mean {y_axis_title} of all scatters, what is the lowest {y_axis_title}?",
                    f"What is the smallest {y_axis_title} among scatters that have their {y_axis_title} above the average {y_axis_title} of all scatters?",
                    f"Among scatters whose {y_axis_title} are above the average {y_axis_title} of all scatters, what is the smallest {y_axis_title}?",
                    f"What is the smallest {y_axis_title} among scatters that have their {y_axis_title} above the mean {y_axis_title} of all scatters?",
                    f"Among scatters whose {y_axis_title} are above the mean {y_axis_title} of all scatters, what is the smallest {y_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of each scatter point in this chart:{read_y}",
                        "step_2": f"Second, I need to compute the average {y_axis_title} of all scatters:\n{reason_y_avg}",
                        "step_3": f"Third, I need to find all the scatters whose {y_axis_title} is higher than {y_value_mean}:\n{', '.join(target_scatter_labels[iii] for iii in y_above_mean_indices)}",
                        "step_4": f"Fourth, I need to identify the scatter point with the lowest {y_axis_title} among these scatters.",
                    },
                ],
                "constraint": "Y - min value among scatters above mean",
                "answer": y_min_above_mean_value,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "step_3": y_above_mean_indices,
                    "step_4": y_min_above_mean_value_indices,
                    "answer": y_min_above_mean_value_indices,
                },
            },
            "multi_step__threshold__x__below_mean__max__value": {
                "question": [
                    f"What is the highest {x_axis_title} among scatters that have their {x_axis_title} below the average {x_axis_title} of all scatters?",
                    f"Among scatters whose {x_axis_title} are below the average {x_axis_title} of all scatters, what is the highest {x_axis_title}?",
                    f"What is the highest {x_axis_title} among scatters that have their {x_axis_title} below the mean {x_axis_title} of all scatters?",
                    f"Among scatters whose {x_axis_title} are below the mean {x_axis_title} of all scatters, what is the highest {x_axis_title}?",
                    f"What is the largest {x_axis_title} among scatters that have their {x_axis_title} below the average {x_axis_title} of all scatters?",
                    f"Among scatters whose {x_axis_title} are below the average {x_axis_title} of all scatters, what is the largest {x_axis_title}?",
                    f"What is the largest {x_axis_title} among scatters that have their {x_axis_title} below the mean {x_axis_title} of all scatters?",
                    f"Among scatters whose {x_axis_title} are below the mean {x_axis_title} of all scatters, what is the largest {x_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {x_axis_title} of each scatter point in this chart:{read_x}",
                        "step_2": f"Second, I need to compute the average {x_axis_title} of all scatters:\n{reason_x_avg}",
                        "step_3": f"Third, I need to find all the scatters whose {x_axis_title} is lower than {x_value_mean}:\n{', '.join(target_scatter_labels[iii] for iii in x_below_mean_indices)}",
                        "step_4": f"Fourth, I need to identify the scatter point with the highest {x_axis_title} among these scatters.",
                    },
                ],
                "constraint": "X - max value among scatters below mean",
                "answer": x_max_below_mean_value,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "step_3": x_below_mean_indices,
                    "step_4": x_max_below_mean_value_indices,
                    "answer": x_max_below_mean_value_indices,
                },
            },
            "multi_step__threshold__y__below_mean__max__value": {
                "question": [
                    f"What is the highest {y_axis_title} among scatters that have their {y_axis_title} below the average {y_axis_title} of all scatters?",
                    f"Among scatters whose {y_axis_title} are below the average {y_axis_title} of all scatters, what is the highest {y_axis_title}?",
                    f"What is the highest {y_axis_title} among scatters that have their {y_axis_title} below the mean {y_axis_title} of all scatters?",
                    f"Among scatters whose {y_axis_title} are below the mean {y_axis_title} of all scatters, what is the highest {y_axis_title}?",
                    f"What is the largest {y_axis_title} among scatters that have their {y_axis_title} below the average {y_axis_title} of all scatters?",
                    f"Among scatters whose {y_axis_title} are below the average {y_axis_title} of all scatters, what is the largest {y_axis_title}?",
                    f"What is the largest {y_axis_title} among scatters that have their {y_axis_title} below the mean {y_axis_title} of all scatters?",
                    f"Among scatters whose {y_axis_title} are below the mean {y_axis_title} of all scatters, what is the largest {y_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of each scatter point in this chart:{read_y}",
                        "step_2": f"Second, I need to compute the average {y_axis_title} of all scatters:\n{reason_y_avg}",
                        "step_3": f"Third, I need to find all the scatters whose {y_axis_title} is lower than {y_value_mean}:\n{', '.join(target_scatter_labels[iii] for iii in y_below_mean_indices)}",
                        "step_4": f"Fourth, I need to identify the scatter point with the highest {y_axis_title} among these scatters.",
                    },
                ],
                "constraint": "Y - max value among scatters below mean",
                "answer": y_max_below_mean_value,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "step_3": y_below_mean_indices,
                    "step_4": y_max_below_mean_value_indices,
                    "answer": y_max_below_mean_value_indices,
                },
            },
            "multi_step__threshold__x__below_mean__min__value": {
                "question": [
                    f"What is the lowest {x_axis_title} among scatters that have their {x_axis_title} below the average {x_axis_title} of all scatters?",
                    f"Among scatters whose {x_axis_title} are below the average {x_axis_title} of all scatters, what is the lowest {x_axis_title}?",
                    f"What is the lowest {x_axis_title} among scatters that have their {x_axis_title} below the mean {x_axis_title} of all scatters?",
                    f"Among scatters whose {x_axis_title} are below the mean {x_axis_title} of all scatters, what is the lowest {x_axis_title}?",
                    f"What is the smallest {x_axis_title} among scatters that have their {x_axis_title} below the average {x_axis_title} of all scatters?",
                    f"Among scatters whose {x_axis_title} are below the average {x_axis_title} of all scatters, what is the smallest {x_axis_title}?",
                    f"What is the smallest {x_axis_title} among scatters that have their {x_axis_title} below the mean {x_axis_title} of all scatters?",
                    f"Among scatters whose {x_axis_title} are below the mean {x_axis_title} of all scatters, what is the smallest {x_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {x_axis_title} of each scatter point in this chart:{read_x}",
                        "step_2": f"Second, I need to compute the average {x_axis_title} of all scatters:\n{reason_x_avg}",
                        "step_3": f"Third, I need to find all the scatters whose {x_axis_title} is lower than {x_value_mean}:\n{', '.join(target_scatter_labels[iii] for iii in x_below_mean_indices)}",
                        "step_4": f"Fourth, I need to identify the scatter point with the lowest {x_axis_title} among these scatters.",
                    },
                ],
                "constraint": "X - min value among scatters below mean",
                "answer": x_min_below_mean_value,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "step_3": x_below_mean_indices,
                    "step_4": x_min_below_mean_value_indices,
                    "answer": x_min_below_mean_value_indices,
                },
            },
            "multi_step__threshold__y__below_mean__min__value": {
                "question": [
                    f"What is the lowest {y_axis_title} among scatters that have their {y_axis_title} below the average {y_axis_title} of all scatters?",
                    f"Among scatters whose {y_axis_title} are below the average {y_axis_title} of all scatters, what is the lowest {y_axis_title}?",
                    f"What is the lowest {y_axis_title} among scatters that have their {y_axis_title} below the mean {y_axis_title} of all scatters?",
                    f"Among scatters whose {y_axis_title} are below the mean {y_axis_title} of all scatters, what is the lowest {y_axis_title}?",
                    f"What is the smallest {y_axis_title} among scatters that have their {y_axis_title} below the average {y_axis_title} of all scatters?",
                    f"Among scatters whose {y_axis_title} are below the average {y_axis_title} of all scatters, what is the smallest {y_axis_title}?",
                    f"What is the smallest {y_axis_title} among scatters that have their {y_axis_title} below the mean {y_axis_title} of all scatters?",
                    f"Among scatters whose {y_axis_title} are below the mean {y_axis_title} of all scatters, what is the smallest {y_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of each scatter point in this chart:{read_y}",
                        "step_2": f"Second, I need to compute the average {y_axis_title} of all scatters:\n{reason_y_avg}",
                        "step_3": f"Third, I need to find all the scatters whose {y_axis_title} is lower than {y_value_mean}:\n{', '.join(target_scatter_labels[iii] for iii in y_below_mean_indices)}",
                        "step_4": f"Fourth, I need to identify the scatter point with the lowest {y_axis_title} among these scatters.",
                    },
                ],
                "constraint": "Y - min value among scatters below mean",
                "answer": y_min_below_mean_value,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "step_3": y_below_mean_indices,
                    "step_4": y_min_below_mean_value_indices,
                    "answer": y_min_below_mean_value_indices,
                },
            },
            "multi_step__threshold__x__above_mean__max__label": {
                "question": [
                    f"What is the label of the scatter point that has the highest {x_axis_title} among scatters that have their {x_axis_title} above the average {x_axis_title} of all scatters?",
                    f"Among scatters whose {x_axis_title} are above the average {x_axis_title} of all scatters, whhat is the label of the scatter point that has the highest {x_axis_title}?",
                    f"What is the label of the scatter point that has the highest {x_axis_title} among scatters that have their {x_axis_title} above the mean {x_axis_title} of all scatters?",
                    f"Among scatters whose {x_axis_title} are above the mean {x_axis_title} of all scatters, what is the label of the scatter point that has the highest {x_axis_title}?",
                    f"What is the label of the scatter point that has the largest {x_axis_title} among scatters that have their {x_axis_title} above the average {x_axis_title} of all scatters?",
                    f"Among scatters whose {x_axis_title} are above the average {x_axis_title} of all scatters, whhat is the label of the scatter point that has the largest {x_axis_title}?",
                    f"What is the label of the scatter point that has the largest {x_axis_title} among scatters that have their {x_axis_title} above the mean {x_axis_title} of all scatters?",
                    f"Among scatters whose {x_axis_title} are above the mean {x_axis_title} of all scatters, what is the label of the scatter point that has the largest {x_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {x_axis_title} of each scatter point in this chart:{read_x}",
                        "step_2": f"Second, I need to compute the average {x_axis_title} of all scatters:\n{reason_x_avg}",
                        "step_3": f"Third, I need to find all the scatters whose {x_axis_title} is higher than {x_value_mean}:\n{', '.join(target_scatter_labels[iii] for iii in x_above_mean_indices)}",
                        "step_4": f"Fourth, I need to identify the scatter point with the highest {x_axis_title} among these scatters.",
                    },
                ],
                "constraint": "X - label of the max value among scatters above mean",
                "answer": x_max_above_mean_label,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "step_3": x_above_mean_indices,
                    "step_4": x_max_above_mean_value_indices,
                    "answer": x_max_above_mean_value_indices,
                },
            },
            "multi_step__threshold__y__above_mean__max__label": {
                "question": [
                    f"What is the label of the scatter point that has the highest {y_axis_title} among scatters that have their {y_axis_title} above the average {y_axis_title} of all scatters?",
                    f"Among scatters whose {y_axis_title} are above the average {y_axis_title} of all scatters, whhat is the label of the scatter point that has the highest {y_axis_title}?",
                    f"What is the label of the scatter point that has the highest {y_axis_title} among scatters that have their {y_axis_title} above the mean {y_axis_title} of all scatters?",
                    f"Among scatters whose {y_axis_title} are above the mean {y_axis_title} of all scatters, what is the label of the scatter point that has the highest {y_axis_title}?",
                    f"What is the label of the scatter point that has the largest {y_axis_title} among scatters that have their {y_axis_title} above the average {y_axis_title} of all scatters?",
                    f"Among scatters whose {y_axis_title} are above the average {y_axis_title} of all scatters, whhat is the label of the scatter point that has the largest {y_axis_title}?",
                    f"What is the label of the scatter point that has the largest {y_axis_title} among scatters that have their {y_axis_title} above the mean {y_axis_title} of all scatters?",
                    f"Among scatters whose {y_axis_title} are above the mean {y_axis_title} of all scatters, what is the label of the scatter point that has the largest {y_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of each scatter point in this chart:{read_y}",
                        "step_2": f"Second, I need to compute the average {y_axis_title} of all scatters:\n{reason_y_avg}",
                        "step_3": f"Third, I need to find all the scatters whose {y_axis_title} is higher than {y_value_mean}:\n{', '.join(target_scatter_labels[iii] for iii in y_above_mean_indices)}",
                        "step_4": f"Fourth, I need to identify the scatter point with the highest {y_axis_title} among these scatters.",
                    },
                ],
                "constraint": "Y - label of the max value among scatters above mean",
                "answer": y_max_above_mean_label,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "step_3": y_above_mean_indices,
                    "step_4": y_max_above_mean_value_indices,
                    "answer": y_max_above_mean_value_indices,
                },
            },
            "multi_step__threshold__x__above_mean__min__label": {
                "question": [
                    f"What is the label of the scatter point that has the lowest {x_axis_title} among scatters that have their {x_axis_title} above the average {x_axis_title} of all scatters?",
                    f"Among scatters whose {x_axis_title} are above the average {x_axis_title} of all scatters, what is the label of the scatter point that has the lowest {x_axis_title}?",
                    f"What is the label of the scatter point that has the lowest {x_axis_title} among scatters that have their {x_axis_title} above the mean {x_axis_title} of all scatters?",
                    f"Among scatters whose {x_axis_title} are above the mean {x_axis_title} of all scatters, what is the label of the scatter point that has the lowest {x_axis_title}?",
                    f"What is the label of the scatter point that has the smallest {x_axis_title} among scatters that have their {x_axis_title} above the average {x_axis_title} of all scatters?",
                    f"Among scatters whose {x_axis_title} are above the average {x_axis_title} of all scatters, what is the label of the scatter point that has the smallest {x_axis_title}?",
                    f"What is the label of the scatter point that has the smallest {x_axis_title} among scatters that have their {x_axis_title} above the mean {x_axis_title} of all scatters?",
                    f"Among scatters whose {x_axis_title} are above the mean {x_axis_title} of all scatters, what is the label of the scatter point that has the smallest {x_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {x_axis_title} of each scatter point in this chart:{read_x}",
                        "step_2": f"Second, I need to compute the average {x_axis_title} of all scatters:\n{reason_x_avg}",
                        "step_3": f"Third, I need to find all the scatters whose {x_axis_title} is higher than {x_value_mean}:\n{', '.join(target_scatter_labels[iii] for iii in x_above_mean_indices)}",
                        "step_4": f"Fourth, I need to identify the scatter point with the lowest {x_axis_title} among these scatters.",
                    },
                ],
                "constraint": "X - min value among scatters above mean",
                "answer": x_min_above_mean_label,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "step_3": x_above_mean_indices,
                    "step_4": x_min_above_mean_value_indices,
                    "answer": x_min_above_mean_value_indices,
                },
            },
            "multi_step__threshold__y__above_mean__min__label": {
                "question": [
                    f"What is the label of the scatter point that has the lowest {y_axis_title} among scatters that have their {y_axis_title} above the average {y_axis_title} of all scatters?",
                    f"Among scatters whose {y_axis_title} are above the average {y_axis_title} of all scatters, what is the label of the scatter point that has the lowest {y_axis_title}?",
                    f"What is the label of the scatter point that has the lowest {y_axis_title} among scatters that have their {y_axis_title} above the mean {y_axis_title} of all scatters?",
                    f"Among scatters whose {y_axis_title} are above the mean {y_axis_title} of all scatters, what is the label of the scatter point that has the lowest {y_axis_title}?",
                    f"What is the label of the scatter point that has the smallest {y_axis_title} among scatters that have their {y_axis_title} above the average {y_axis_title} of all scatters?",
                    f"Among scatters whose {y_axis_title} are above the average {y_axis_title} of all scatters, what is the label of the scatter point that has the smallest {y_axis_title}?",
                    f"What is the label of the scatter point that has the smallest {y_axis_title} among scatters that have their {y_axis_title} above the mean {y_axis_title} of all scatters?",
                    f"Among scatters whose {y_axis_title} are above the mean {y_axis_title} of all scatters, what is the label of the scatter point that has the smallest {y_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of each scatter point in this chart:{read_y}",
                        "step_2": f"Second, I need to compute the average {y_axis_title} of all scatters:\n{reason_y_avg}",
                        "step_3": f"Third, I need to find all the scatters whose {y_axis_title} is higher than {y_value_mean}:\n{', '.join(target_scatter_labels[iii] for iii in y_above_mean_indices)}",
                        "step_4": f"Fourth, I need to identify the scatter point with the lowest {y_axis_title} among these scatters.",
                    },
                ],
                "constraint": "Y - min value among scatters above mean",
                "answer": y_min_above_mean_label,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "step_3": y_above_mean_indices,
                    "step_4": y_min_above_mean_value_indices,
                    "answer": y_min_above_mean_value_indices,
                },
            },
            "multi_step__threshold__x__above_mean__sum": {
                "question": [
                    f"What is the sum of {x_axis_title} for scatters that have their {x_axis_title} above the average {x_axis_title} of all scatters?",
                    f"Among scatters whose {x_axis_title} are above the average {x_axis_title} of all scatters, what is the sum of their {x_axis_title}?",
                    f"What is the sum of {x_axis_title} for scatters that have their {x_axis_title} above the mean {x_axis_title} of all scatters?",
                    f"Among scatters whose {x_axis_title} are above the mean {x_axis_title} of all scatters, what is the sum of their {x_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {x_axis_title} of each scatter point in this chart:{read_x}",
                        "step_2": f"Second, I need to compute the average {x_axis_title} of all scatters:\n{reason_x_avg}",
                        "step_3": f"Third, I need to find all the scatters whose {x_axis_title} is higher than {x_value_mean}:\n{', '.join(target_scatter_labels[iii] for iii in x_above_mean_indices)}",
                        "step_4": f"Fourth, I need to calculate the total {x_axis_title} of these scatters:\n{reason_x_above_mean_value_sum}",
                    },
                ],
                "constraint": "X - sum of scatters above mean",
                "answer": x_above_mean_value_sum,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "step_3": x_above_mean_indices,
                    "step_4": x_above_mean_indices,
                    "answer": x_above_mean_indices,
                },
            },
            "multi_step__threshold__y__above_mean__sum": {
                "question": [
                    f"What is the sum of {y_axis_title} for scatters that have their {y_axis_title} above the average {y_axis_title} of all scatters?",
                    f"Among scatters whose {y_axis_title} are above the average {y_axis_title} of all scatters, what is the sum of their {y_axis_title}?",
                    f"What is the sum of {y_axis_title} for scatters that have their {y_axis_title} above the mean {y_axis_title} of all scatters?",
                    f"Among scatters whose {y_axis_title} are above the mean {y_axis_title} of all scatters, what is the sum of their {y_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of each scatter point in this chart:{read_y}",
                        "step_2": f"Second, I need to compute the average {y_axis_title} of all scatters:\n{reason_y_avg}",
                        "step_3": f"Third, I need to find all the scatters whose {y_axis_title} is higher than {y_value_mean}:\n{', '.join(target_scatter_labels[iii] for iii in y_above_mean_indices)}",
                        "step_4": f"Fourth, I need to calculate the total {y_axis_title} of these scatters:\n{reason_y_above_mean_value_sum}",
                    },
                ],
                "constraint": "Y - sum of scatters above mean",
                "answer": y_above_mean_value_sum,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "step_3": y_above_mean_indices,
                    "step_4": y_above_mean_indices,
                    "answer": y_above_mean_indices,
                },
            },
            "multi_step__threshold__x__below_mean__sum": {
                "question": [
                    f"What is the sum of {x_axis_title} for scatters that have their {x_axis_title} below the average {x_axis_title} of all scatters?",
                    f"Among scatters whose {x_axis_title} are below the average {x_axis_title} of all scatters, what is the sum of their {x_axis_title}?",
                    f"What is the sum of {x_axis_title} for scatters that have their {x_axis_title} below the mean {x_axis_title} of all scatters?",
                    f"Among scatters whose {x_axis_title} are below the mean {x_axis_title} of all scatters, what is the sum of their {x_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {x_axis_title} of each scatter point in this chart:{read_x}",
                        "step_2": f"Second, I need to compute the average {x_axis_title} of all scatters:\n{reason_x_avg}",
                        "step_3": f"Third, I need to find all the scatters whose {x_axis_title} is lower than {x_value_mean}:\n{', '.join(target_scatter_labels[iii] for iii in x_below_mean_indices)}",
                        "step_4": f"Fourth, I need to calculate the total {x_axis_title} of these scatters:\n{reason_x_below_mean_value_sum}",
                    },
                ],
                "constraint": "X - sum of scatters below mean",
                "answer": x_below_mean_value_sum,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "step_3": x_below_mean_indices,
                    "step_4": x_below_mean_indices,
                    "answer": x_below_mean_indices,
                },
            },
            "multi_step__threshold__y__below_mean__sum": {
                "question": [
                    f"What is the sum of {y_axis_title} for scatters that have their {y_axis_title} below the average {y_axis_title} of all scatters?",
                    f"Among scatters whose {y_axis_title} are below the average {y_axis_title} of all scatters, what is the sum of their {y_axis_title}?",
                    f"What is the sum of {y_axis_title} for scatters that have their {y_axis_title} below the mean {y_axis_title} of all scatters?",
                    f"Among scatters whose {y_axis_title} are below the mean {y_axis_title} of all scatters, what is the sum of their {y_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of each scatter point in this chart:{read_y}",
                        "step_2": f"Second, I need to compute the average {y_axis_title} of all scatters:\n{reason_y_avg}",
                        "step_3": f"Third, I need to find all the scatters whose {y_axis_title} is lower than {y_value_mean}:\n{', '.join(target_scatter_labels[iii] for iii in y_below_mean_indices)}",
                        "step_4": f"Fourth, I need to calculate the total {y_axis_title} of these scatters:\n{reason_y_below_mean_value_sum}",
                    },
                ],
                "constraint": "Y - sum of scatters below mean",
                "answer": y_below_mean_value_sum,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "step_3": y_below_mean_indices,
                    "step_4": y_below_mean_indices,
                    "answer": y_below_mean_indices,
                },
            },
            "multi_step__threshold__x__above_mean__avg": {
                "question": [
                    f"What is the mean value of {x_axis_title} for scatters that have their {x_axis_title} above the average {x_axis_title} of all scatters? Please round to two decimal places.",
                    f"Among scatters whose {x_axis_title} are above the average {x_axis_title} of all scatters, what is their mean {x_axis_title}? Please round to two decimal places.",
                    f"What is the average value of {x_axis_title} for scatters that have their {x_axis_title} above the mean {x_axis_title} of all scatters? Please round to two decimal places.",
                    f"Among scatters whose {x_axis_title} are above the mean {x_axis_title} of all scatters, what is their average {x_axis_title}? Please round to two decimal places.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {x_axis_title} of each scatter point in this chart:{read_x}",
                        "step_2": f"Second, I need to compute the average {x_axis_title} of all scatters:\n{reason_x_avg}",
                        "step_3": f"Third, I need to find all the scatters whose {x_axis_title} is higher than {x_value_mean}:\n{', '.join(target_scatter_labels[iii] for iii in x_above_mean_indices)}",
                        "step_4": f"Fourth, I need to calculate the mean {x_axis_title} of these scatters:\n{reason_x_above_mean_value_avg}",
                    },
                ],
                "constraint": "X - mean of scatters above mean",
                "answer": x_above_mean_value_avg,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "step_3": x_above_mean_indices,
                    "step_4": x_above_mean_indices,
                    "answer": x_above_mean_indices,
                },
            },
            "multi_step__threshold__y__above_mean__avg": {
                "question": [
                    f"What is the mean value of {y_axis_title} for scatters that have their {y_axis_title} above the average {y_axis_title} of all scatters? Please round to two decimal places.",
                    f"Among scatters whose {y_axis_title} are above the average {y_axis_title} of all scatters, what is their mean {y_axis_title}? Please round to two decimal places.",
                    f"What is the average value of {y_axis_title} for scatters that have their {y_axis_title} above the mean {y_axis_title} of all scatters? Please round to two decimal places.",
                    f"Among scatters whose {y_axis_title} are above the mean {y_axis_title} of all scatters, what is their average {y_axis_title}? Please round to two decimal places.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of each scatter point in this chart:{read_y}",
                        "step_2": f"Second, I need to compute the average {y_axis_title} of all scatters:\n{reason_y_avg}",
                        "step_3": f"Third, I need to find all the scatters whose {y_axis_title} is higher than {y_value_mean}:\n{', '.join(target_scatter_labels[iii] for iii in y_above_mean_indices)}",
                        "step_4": f"Fourth, I need to calculate the mean {y_axis_title} of these scatters:\n{reason_y_above_mean_value_avg}",
                    },
                ],
                "constraint": "Y - mean of scatters above mean",
                "answer": y_above_mean_value_avg,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "step_3": y_above_mean_indices,
                    "step_4": y_above_mean_indices,
                    "answer": y_above_mean_indices,
                },
            },
            "multi_step__threshold__x__below_mean__avg": {
                "question": [
                    f"What is the mean value of {x_axis_title} for scatters that have their {x_axis_title} below the average {x_axis_title} of all scatters? Please round to two decimal places.",
                    f"Among scatters whose {x_axis_title} are below the average {x_axis_title} of all scatters, what is their mean {x_axis_title}? Please round to two decimal places.",
                    f"What is the average value of {x_axis_title} for scatters that have their {x_axis_title} below the mean {x_axis_title} of all scatters? Please round to two decimal places.",
                    f"Among scatters whose {x_axis_title} are below the mean {x_axis_title} of all scatters, what is their average {x_axis_title}? Please round to two decimal places.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {x_axis_title} of each scatter point in this chart:{read_x}",
                        "step_2": f"Second, I need to compute the average {x_axis_title} of all scatters:\n{reason_x_avg}",
                        "step_3": f"Third, I need to find all the scatters whose {x_axis_title} is lower than {x_value_mean}:\n{', '.join(target_scatter_labels[iii] for iii in x_below_mean_indices)}",
                        "step_4": f"Fourth, I need to calculate the mean {x_axis_title} of these scatters:\n{reason_x_below_mean_value_avg}",
                    },
                ],
                "constraint": "X - mean of scatters below mean",
                "answer": x_below_mean_value_avg,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "step_3": x_below_mean_indices,
                    "step_4": x_below_mean_indices,
                    "answer": x_below_mean_indices,
                },
            },
            "multi_step__threshold__y__below_mean__avg": {
                "question": [
                    f"What is the mean value of {y_axis_title} for scatters that have their {y_axis_title} below the average {y_axis_title} of all scatters? Please round to two decimal places.",
                    f"Among scatters whose {y_axis_title} are below the average {y_axis_title} of all scatters, what is their mean {y_axis_title}? Please round to two decimal places.",
                    f"What is the average value of {y_axis_title} for scatters that have their {y_axis_title} below the mean {y_axis_title} of all scatters? Please round to two decimal places.",
                    f"Among scatters whose {y_axis_title} are below the mean {y_axis_title} of all scatters, what is their average {y_axis_title}? Please round to two decimal places.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of each scatter point in this chart:{read_y}",
                        "step_2": f"Second, I need to compute the average {y_axis_title} of all scatters:\n{reason_y_avg}",
                        "step_3": f"Third, I need to find all the scatters whose {y_axis_title} is lower than {y_value_mean}:\n{', '.join(target_scatter_labels[iii] for iii in y_below_mean_indices)}",
                        "step_4": f"Fourth, I need to calculate the mean {y_axis_title} of these scatters:\n{reason_y_below_mean_value_avg}",
                    },
                ],
                "constraint": "mean of scatters below mean",
                "answer": y_below_mean_value_avg,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "step_3": y_below_mean_indices,
                    "step_4": y_below_mean_indices,
                    "answer": y_below_mean_indices,
                },
            },
            "multi_step__threshold__x__mean__sum_diff": {
                "question": [
                    f"What is the absolute difference between the total {x_axis_title} of scatters above the average {x_axis_title} and those below it?"
                    f"What is the absolute value of the difference between the total {x_axis_title} for scatters above the average and those below the average {x_axis_title}?",
                    f"What is the absolute difference between the total {x_axis_title} of scatters above the mean {x_axis_title} and those below it?"
                    f"What is the absolute value of the difference between the total {x_axis_title} for scatters above the mean {x_axis_title} and those below the mean {x_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {x_axis_title} of each scatter point in this chart:{read_x}",
                        "step_2": f"Second, I need to compute the average {x_axis_title} of all scatters:\n{reason_x_avg}",
                        "step_3": f"Third, I need to find the first group of scatters whose {x_axis_title} is higher than {x_value_mean} and the second group of scatters whose {x_axis_title} is lower than {x_value_mean}.",
                        "step_4": f"Fourth, I need to calculate the total {x_axis_title} of these two groups of scatters respectively:\n- Group 1 (above overall mean): {reason_x_above_mean_value_sum}\n- Group 2 (below overall mean): {reason_x_below_mean_value_sum}",
                        "step_5": f"Fifth, I need to calculate the absolute difference between these two groups of scatters:\n|{x_above_mean_value_sum} - {x_below_mean_value_sum}| = {x_sum_diff}.",
                    },
                ],
                "constraint": "Y - sum difference bewteen scatters above and below mean",
                "answer": x_sum_diff,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "step_3": x_above_mean_indices + x_below_mean_indices,
                    "step_4": x_above_mean_indices + x_below_mean_indices,
                    "step_5": x_above_mean_indices + x_below_mean_indices,
                    "answer": x_above_mean_indices + x_below_mean_indices,
                },
            },
            "multi_step__threshold__y__mean__sum_diff": {
                "question": [
                    f"What is the absolute difference between the total {y_axis_title} of scatters above the average {y_axis_title} and those below it?"
                    f"What is the absolute value of the difference between the total {y_axis_title} for scatters above the average and those below the average {y_axis_title}?",
                    f"What is the absolute difference between the total {y_axis_title} of scatters above the mean {y_axis_title} and those below it?"
                    f"What is the absolute value of the difference between the total {y_axis_title} for scatters above the mean {y_axis_title} and those below the mean {y_axis_title}?",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of each scatter point in this chart:{read_y}",
                        "step_2": f"Second, I need to compute the average {y_axis_title} of all scatters:\n{reason_y_avg}",
                        "step_3": f"Third, I need to find the first group of scatters whose {y_axis_title} is higher than {y_value_mean} and the second group of scatters whose {y_axis_title} is lower than {y_value_mean}.",
                        "step_4": f"Fourth, I need to calculate the total {y_axis_title} of these two groups of scatters respectively:\n- Group 1 (above overall mean): {reason_y_above_mean_value_sum}\n- Group 2 (below overall mean): {reason_y_below_mean_value_sum}",
                        "step_5": f"Fifth, I need to calculate the absolute difference between these two groups of scatters:\n|{y_above_mean_value_sum} - {y_below_mean_value_sum}| = {y_sum_diff}.",
                    },
                ],
                "constraint": "Y - sum difference bewteen scatters above and below mean",
                "answer": y_sum_diff,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "step_3": y_above_mean_indices + y_below_mean_indices,
                    "step_4": y_above_mean_indices + y_below_mean_indices,
                    "step_5": y_above_mean_indices + y_below_mean_indices,
                    "answer": y_above_mean_indices + y_below_mean_indices,
                },
            },
            "multi_step__threshold__x__mean__mean_diff": {
                "question": [
                    f"What is the absolute difference between the average {x_axis_title} of scatters above and below the overall average? Please round to two decimal places."
                    f"What is the absolute difference between the mean {x_axis_title} of scatters above the overall average and those below it? Please round to two decimal places.",
                    f"What is the absolute difference between the average {x_axis_title} of scatters whose values are above the overall average and those whose values are below it? Please round to two decimal places.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {x_axis_title} of each scatter point in this chart:{read_x}",
                        "step_2": f"Second, I need to compute the average {x_axis_title} of all scatters:\n{reason_x_avg}",
                        "step_3": f"Third, I need to find the first group of scatters whose {x_axis_title} is higher than {x_value_mean} and the second group of scatters whose {x_axis_title} is lower than {x_value_mean}.",
                        "step_4": f"Fourth, I need to calculate the total {x_axis_title} of these two groups of scatters respectively:\n- Group 1 (above overall mean): {reason_x_above_mean_value_avg}\n- Group 2 (below overall mean): {reason_x_below_mean_value_avg}",
                        "step_5": f"Fifth, I need to calculate the absolute difference between these two groups of scatters:\n|{x_above_mean_value_avg} - {x_below_mean_value_avg}| = {x_mean_diff}.",
                    },
                ],
                "constraint": "mean difference bewteen scatters above and below mean",
                "answer": x_mean_diff,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "step_3": x_above_mean_indices + x_below_mean_indices,
                    "step_4": x_above_mean_indices + x_below_mean_indices,
                    "step_5": x_above_mean_indices + x_below_mean_indices,
                    "answer": x_above_mean_indices + x_below_mean_indices,
                },
            },
            "multi_step__threshold__y__mean__mean_diff": {
                "question": [
                    f"What is the absolute difference between the average {y_axis_title} of scatters above and below the overall average? Please round to two decimal places."
                    f"What is the absolute difference between the mean {y_axis_title} of scatters above the overall average and those below it? Please round to two decimal places.",
                    f"What is the absolute difference between the average {y_axis_title} of scatters whose values are above the overall average and those whose values are below it? Please round to two decimal places.",
                ],
                "reasoning": [
                    {
                        "step_1": f"First, I need to read the {y_axis_title} of each scatter point in this chart:{read_y}",
                        "step_2": f"Second, I need to compute the average {y_axis_title} of all scatters:\n{reason_y_avg}",
                        "step_3": f"Third, I need to find the first group of scatters whose {y_axis_title} is higher than {y_value_mean} and the second group of scatters whose {y_axis_title} is lower than {y_value_mean}.",
                        "step_4": f"Fourth, I need to calculate the total {y_axis_title} of these two groups of scatters respectively:\n- Group 1 (above overall mean): {reason_y_above_mean_value_avg}\n- Group 2 (below overall mean): {reason_y_below_mean_value_avg}",
                        "step_5": f"Fifth, I need to calculate the absolute difference between these two groups of scatters:\n|{y_above_mean_value_avg} - {y_below_mean_value_avg}| = {y_mean_diff}.",
                    },
                ],
                "constraint": "mean difference bewteen scatters above and below mean",
                "answer": y_mean_diff,
                "mask": {
                    "step_1": target_scatter_indices,
                    "step_2": target_scatter_indices,
                    "step_3": y_above_mean_indices + y_below_mean_indices,
                    "step_4": y_above_mean_indices + y_below_mean_indices,
                    "step_5": y_above_mean_indices + y_below_mean_indices,
                    "answer": y_above_mean_indices + y_below_mean_indices,
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

        # Constraint - Value
        min_x = min(chart_metadata["scatter_x_data"])
        max_x = max(chart_metadata["scatter_x_data"])
        min_y = min(chart_metadata["scatter_y_data"])
        max_y = max(chart_metadata["scatter_y_data"])

        # Constraint - Label
        selected_indices = [0, 2, 3, 5, 6]  # TODO: convert fixed indices to soft lists (currently disabled to avoid oversize generarted data)
        selected_scatter_labels = self._convert_answer_idx_to_str(chart_metadata["scatter_labels"], selected_indices)

        # Key: constraint, Value: scatter_list
        constraint_meta = {
            # Selected value
            f"that have their {x_axis_title} above the lowest while below the highest": self._filter_middle_indices(chart_metadata["scatter_x_data"]),
            f"that have their {x_axis_title} higher than {min_x} but lower than {max_x}": self._filter_middle_indices(chart_metadata["scatter_x_data"]),
            f"whose {x_axis_title} are above the lowest while below the highest": self._filter_middle_indices(chart_metadata["scatter_x_data"]),
            f"whose {x_axis_title} are higher than {min_x} but lower than {max_x}": self._filter_middle_indices(chart_metadata["scatter_x_data"]),
            f"with their {x_axis_title} higher than {min_x} but lower than {max_x}": self._filter_middle_indices(chart_metadata["scatter_x_data"]),
            f"with their {x_axis_title} higher than the lowest but lower than the highest": self._filter_middle_indices(chart_metadata["scatter_x_data"]),

            f"that have their {y_axis_title} above the lowest while below the highest": self._filter_middle_indices(chart_metadata["scatter_y_data"]),
            f"that have their {y_axis_title} higher than {min_y} but lower than {max_y}": self._filter_middle_indices(chart_metadata["scatter_y_data"]),
            f"whose {y_axis_title} are above the lowest while below the highest": self._filter_middle_indices(chart_metadata["scatter_y_data"]),
            f"whose {y_axis_title} are higher than {min_y} but lower than {max_y}": self._filter_middle_indices(chart_metadata["scatter_y_data"]),
            f"with their {y_axis_title} higher than {min_y} but lower than {max_y}": self._filter_middle_indices(chart_metadata["scatter_y_data"]),
            f"with their {y_axis_title} higher than the lowest but lower than the highest": self._filter_middle_indices(chart_metadata["scatter_y_data"]),

            # Selected label
            f"that have their labels among '{selected_scatter_labels}'": selected_indices,
            f"whose labels are one of '{selected_scatter_labels}'": selected_indices,
            f"among the labels '{selected_scatter_labels}'": selected_indices,
        }

        # (1) Statistics
        # (1.1) Easy: one-step
        aggregation_easy_qa_pool = self._one_step_statistics(chart_metadata)
        self._qa_pool_converter(qa_pool=aggregation_easy_qa_pool, curriculum_level=1)
        # (1.2) Medium: two-step
        for qa_constraint in constraint_meta:
            qa_scatter_list = constraint_meta[qa_constraint]
            aggregation_medium_qa_pool = self._two_step_statistics(chart_metadata, qa_scatter_list, qa_constraint)
            self._qa_pool_converter(qa_pool=aggregation_medium_qa_pool, curriculum_level=2)

        # (2) Extrema
        # (2.1) Easy: one-step
        extrema_easy_qa_pool = self._one_step_extrema(chart_metadata)
        self._qa_pool_converter(qa_pool=extrema_easy_qa_pool, curriculum_level=1)
        # (2.2) Medium: two-step
        for qa_constraint in constraint_meta:
            qa_scatter_list = constraint_meta[qa_constraint]
            extrema_medium_qa_pool = self._two_step_extrema(chart_metadata, qa_scatter_list, qa_constraint)
            self._qa_pool_converter(qa_pool=extrema_medium_qa_pool, curriculum_level=2)

        # (3) Compare
        # (3.1) Medium: two-step
        compare_scatter_list = [2, 5]  # TODO: convert fixed indices to soft lists (currently disabled to avoid oversize generarted data)
        compare_medium_qa_pool = self._two_step_compare_two_scatters(chart_metadata, compare_scatter_list)
        self._qa_pool_converter(qa_pool=compare_medium_qa_pool, curriculum_level=2)

        # (4) Sort
        # (4.1) Easy: one-step
        sort_easy_qa_pool = self._one_step_sort(chart_metadata)
        self._qa_pool_converter(qa_pool=sort_easy_qa_pool, curriculum_level=1)
        # (4.2) Medium: two-step
        for qa_constraint in constraint_meta:
            qa_scatter_list = constraint_meta[qa_constraint]
            sort_medium_qa_pool = self._two_step_sort(chart_metadata, qa_scatter_list, qa_constraint)
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
