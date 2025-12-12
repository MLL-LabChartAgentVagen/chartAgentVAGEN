"""
Questions Metadata for Scatter Charts

This file contains pre-made/hardcoded questions for scatter charts.
The structure mirrors METADATA_SCATTER from metadata.py, allowing questions
to be associated with specific chart entries.

Structure:
QUESTIONS_METADATA_SCATTER = {
    "func_id": {
        "category": [
            {
                "questions": [
                    {
                        "qa_type": "question_type_key",
                        "question": ["question variant 1", "question variant 2", ...],
                        "reasoning": [
                            {
                                "step_1": "reasoning step 1",
                                "step_2": "reasoning step 2",
                                ...
                            }
                        ],
                        "constraint": "constraint description",
                        "answer": "answer_value",
                        "mask": {
                            "step_1": [indices],
                            "step_2": [indices],
                            "answer": [indices]
                        }
                    }
                ]
            }
        ]
    }
}
"""

# Import METADATA_SCATTER to ensure structure alignment
from metadata.metadata import METADATA_SCATTER

# Initialize empty structure - questions will be added per chart entry
QUESTIONS_METADATA_SCATTER = {}

# Example structure for draw__3_scatter__func_1
# This can be populated with hardcoded questions from examples/scatter_generator.py
# 
# To add questions:
# 1. Find the func_id and category in METADATA_SCATTER
# 2. Add questions following the structure below
# 3. If answer/mask is None, they will be computed automatically from chart metadata
#
# Note: Questions are matched by func_id, category, and chart_index (order within category)
QUESTIONS_METADATA_SCATTER["draw__3_scatter__func_1"] = {
    "1 - Media & Entertainment": [
        # First chart entry questions (chart_index=0)
        {
            "questions": [
                # Example: Sum questions
                # If answer is None, it will be computed from qa_type (e.g., "sum_x" -> sum of x_data)
                # If mask indices are None, they default to all indices
                {
                    "qa_type": "one_step__statistics__sum_x",
                    "question": [
                        "What is the total Rating Score for all the scatters in this chart?",
                        "For all the scatters in this chart, what is the sum of their Rating Score?",
                        "Can you help calculate the sum of Rating Score for all the scatters in this chart?",
                    ],
                    "reasoning": [
                        {
                            "step_1": "First, I need to read the Rating Score of each scatter point in this chart.",
                            "step_2": "Second, I need to sum them up to calculate the total Rating Score of all the scatters.",
                        }
                    ],
                    "constraint": None,
                    "answer": None,  # Will be computed: sum of scatter_x_data
                    "mask": {
                        "step_1": None,  # Will default to all indices [0,1,2,...,n-1]
                        "step_2": None,  # Will default to all indices
                        "answer": None,  # Will default to all indices
                    }
                },
                # Example: Mean questions with specific mask
                {
                    "qa_type": "one_step__statistics__mean_x",
                    "question": [
                        "What is the mean Rating Score of all the scatters in this chart?",
                        "What is the average Rating Score of all the scatters in this chart?",
                    ],
                    "reasoning": [
                        {
                            "step_1": "I will select all scatter points.",
                            "step_2": "I need to calculate the mean Rating Score for these scatter points.",
                        }
                    ],
                    "constraint": "all items",
                    "answer": None,  # Will be computed: mean of scatter_x_data
                    "mask": {
                        "step_1": None,  # All indices
                        "step_2": None,  # All indices
                        "answer": None,  # All indices
                    }
                },
                # Add more question types as needed
            ]
        },
        # Second chart entry questions (chart_index=1, if multiple charts per category)
        {
            "questions": []
        }
    ],
    # Add other categories as needed
    "2 - Geography & Demography": [
        {
            "questions": []
        }
    ],
}

def get_questions_for_chart(func_id: str, category: str, chart_index: int = 0):
    """
    Get hardcoded questions for a specific chart entry.
    
    Args:
        func_id: Function ID (e.g., "draw__3_scatter__func_1")
        category: Category name (e.g., "1 - Media & Entertainment")
        chart_index: Index of chart within category (default: 0)
    
    Returns:
        List of question dictionaries, or empty list if not found
    """
    if func_id not in QUESTIONS_METADATA_SCATTER:
        return []
    
    if category not in QUESTIONS_METADATA_SCATTER[func_id]:
        return []
    
    category_questions = QUESTIONS_METADATA_SCATTER[func_id][category]
    
    if chart_index >= len(category_questions):
        return []
    
    return category_questions[chart_index].get("questions", [])


def has_questions_for_chart(func_id: str, category: str, chart_index: int = 0) -> bool:
    """
    Check if hardcoded questions exist for a specific chart entry.
    
    Args:
        func_id: Function ID
        category: Category name
        chart_index: Index of chart within category
    
    Returns:
        True if questions exist, False otherwise
    """
    questions = get_questions_for_chart(func_id, category, chart_index)
    return len(questions) > 0

