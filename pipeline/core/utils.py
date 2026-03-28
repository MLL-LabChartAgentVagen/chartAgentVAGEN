"""
Shared utility functions and constants for the AGPDS pipeline.

Salvaged from generation_pipeline.py — META_CATEGORIES, ID generation,
category lookup helpers.
"""

import json
import hashlib
import random
from datetime import datetime
from typing import Optional


# =============================================================================
# Domain Taxonomy (30 categories)
# =============================================================================

META_CATEGORIES = [
    "1 - Media & Entertainment",
    "2 - Geography & Demography",
    "3 - Education & Academia",
    "4 - Business & Industry",
    "5 - Major & Course",
    "6 - Animal & Zoology",
    "7 - Plant & Botany",
    "8 - Biology & Chemistry",
    "9 - Food & Nutrition",
    "10 - Space & Astronomy",
    "11 - Sale & Merchandise",
    "12 - Market & Economy",
    "13 - Sports & Athletics",
    "14 - Computing & Technology",
    "15 - Health & Medicine",
    "16 - Energy & Environment",
    "17 - Travel & Expedition",
    "18 - Arts & Culture",
    "19 - Communication & Collaboration",
    "20 - Language & Linguistics",
    "21 - History & Archaeology",
    "22 - Weather & Climate",
    "23 - Transportation & Infrastructure",
    "24 - Psychology & Personality",
    "25 - Materials & Engineering",
    "26 - Philanthropy & Charity",
    "27 - Fashion & Apparel",
    "28 - Parenting & Child Development",
    "29 - Architecture & Urban Planning",
    "30 - Gaming & Recreation",
]


# =============================================================================
# Utility Functions
# =============================================================================

def generate_unique_id(prefix: str = "gen") -> str:
    """Generate unique ID for tracking generations."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_suffix = hashlib.md5(str(random.random()).encode()).hexdigest()[:6]
    return f"{prefix}_{timestamp}_{random_suffix}"


def validate_category(category: str) -> bool:
    """Check if category is in valid taxonomy."""
    return category in META_CATEGORIES


def get_category_by_id(category_id: int) -> Optional[str]:
    """Get category name by ID (1-30)."""
    if 1 <= category_id <= 30:
        return META_CATEGORIES[category_id - 1]
    return None


def get_available_categories() -> list[str]:
    """
    Get list of all available categories for manual topic selection.

    Returns:
        List of 30 predefined category strings
    """
    return META_CATEGORIES.copy()


def print_available_categories():
    """Print all available categories in a formatted list."""
    print("Available 30 topic categories:")
    print("=" * 60)
    for i, category in enumerate(META_CATEGORIES, 1):
        print(f"{i:2d}. {category}")
    print("=" * 60)
