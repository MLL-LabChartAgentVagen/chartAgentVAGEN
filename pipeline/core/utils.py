"""
Legacy 30-category taxonomy + the single lookup retained for the
``--category-id`` CLI translation in agpds_pipeline._sample_domain
(and for run/log strings in agpds_runner.py / agpds_generate.py).

Sprint C trimmed the unused validate_category / get_available_categories /
print_available_categories helpers. The full file removal is gated on the
agpds_*.py CLI rename (Sprint F.4) — once that lands, the runtime lookup
moves with it and this file goes away.
"""

from typing import Optional


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


def get_category_by_id(category_id: int) -> Optional[str]:
    """Get category name by ID (1-30); None if out of range."""
    if 1 <= category_id <= 30:
        return META_CATEGORIES[category_id - 1]
    return None
