"""Tests for build_scenario_pool.py command-line defaults."""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.phase_1 import build_scenario_pool  # noqa: E402


class TestBuildScenarioPoolArgs(unittest.TestCase):

    def test_default_dedup_scope_is_category(self):
        with patch.object(sys, "argv", ["build_scenario_pool.py"]):
            args = build_scenario_pool.parse_args()

        self.assertEqual(args.dedup_scope, "category")
        self.assertEqual(args.min_scenarios_per_domain, 1)
        self.assertEqual(args.dedup_threshold, 0.85)

    def test_dedup_scope_and_min_domain_can_be_overridden(self):
        argv = [
            "build_scenario_pool.py",
            "--dedup-scope",
            "domain",
            "--min-scenarios-per-domain",
            "2",
            "--dedup-threshold",
            "0.92",
        ]
        with patch.object(sys, "argv", argv):
            args = build_scenario_pool.parse_args()

        self.assertEqual(args.dedup_scope, "domain")
        self.assertEqual(args.min_scenarios_per_domain, 2)
        self.assertEqual(args.dedup_threshold, 0.92)


if __name__ == "__main__":
    unittest.main()
