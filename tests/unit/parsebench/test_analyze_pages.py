"""The driver, in the part that runs without a model."""

import pytest
from analyze_pages import page_image


def test_the_missing_page_error_names_the_renderer(tmp_path):
    with pytest.raises(FileNotFoundError, match="render_pages.py"):
        page_image(tmp_path, "absent")
