"""Tests for build_scenario_pool.py command-line defaults."""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.phase_1 import build_scenario_pool  # noqa: E402


class TestBuildScenarioPoolArgs(unittest.TestCase):

    def test_defaults(self):
        with patch.object(sys, "argv", ["build_scenario_pool.py"]):
            args = build_scenario_pool.parse_args()

        self.assertEqual(args.dedup_scope, "domain")
        self.assertEqual(args.min_scenarios_per_domain, 1)
        self.assertEqual(args.dedup_threshold, 0.85)
        # tier-variable K defaults
        self.assertEqual(args.k_simple, 3)
        self.assertEqual(args.k_medium, 5)
        self.assertEqual(args.k_complex, 7)

    def test_overrides(self):
        argv = [
            "build_scenario_pool.py",
            "--dedup-scope",
            "tier",
            "--min-scenarios-per-domain",
            "2",
            "--dedup-threshold",
            "0.92",
            "--k-simple", "2",
            "--k-medium", "4",
            "--k-complex", "6",
        ]
        with patch.object(sys, "argv", argv):
            args = build_scenario_pool.parse_args()

        self.assertEqual(args.dedup_scope, "tier")
        self.assertEqual(args.min_scenarios_per_domain, 2)
        self.assertEqual(args.dedup_threshold, 0.92)
        self.assertEqual(args.k_simple, 2)
        self.assertEqual(args.k_medium, 4)
        self.assertEqual(args.k_complex, 6)

    def test_legacy_category_scope_rejected(self):
        argv = ["build_scenario_pool.py", "--dedup-scope", "category"]
        with patch.object(sys, "argv", argv):
            with self.assertRaises(SystemExit):
                build_scenario_pool.parse_args()


if __name__ == "__main__":
    unittest.main()
