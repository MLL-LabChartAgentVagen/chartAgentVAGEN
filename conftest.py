"""Pytest root conftest — ensures `pipeline.*` imports resolve when tests run
from any cwd, without needing the project to be pip-installed."""
import os
import sys

_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
