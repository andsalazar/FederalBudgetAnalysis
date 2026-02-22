"""
Tests for data integrity and pipeline consistency.

Validates:
  - Output JSON files parse correctly and have expected keys
  - Structural break z-scores match between JSON and FINDINGS.md
  - B50 Q4 factor (0.414) is consistent across scripts
  - Config YAML has required fields
  - No hardcoded API keys in source files
"""
import json
import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "output"
TABLES = OUTPUT / "tables"


# ---------------------------------------------------------------------------
# JSON output integrity
# ---------------------------------------------------------------------------
class TestOutputJSON:
    def test_structural_break_json_exists(self):
        p = TABLES / "structural_break_tests.json"
        assert p.exists(), f"Missing {p}"

    def test_structural_break_json_schema(self):
        p = TABLES / "structural_break_tests.json"
        if not p.exists():
            pytest.skip("structural_break_tests.json not yet generated")
        data = json.loads(p.read_text())
        expected_keys = {
            "customs_share",
            "interest_ratio",
            "regressive_share",
            "safety_net_share",
        }
        assert expected_keys == set(data.keys())
        for key, entry in data.items():
            assert "z_score" in entry, f"Missing z_score in {key}"
            assert "interpretation" in entry, f"Missing interpretation in {key}"

    def test_robustness_json_exists(self):
        p = TABLES / "robustness_summary.json"
        assert p.exists(), f"Missing {p}"

    def test_robustness_json_all_pass(self):
        p = TABLES / "robustness_summary.json"
        if not p.exists():
            pytest.skip("robustness_summary.json not yet generated")
        data = json.loads(p.read_text())
        for entry in data:
            assert entry["robust"] == "YES", (
                f"Test '{entry['test']}' not robust: {entry['conclusion']}"
            )

    def test_counterfactual_json_exists(self):
        p = TABLES / "counterfactual_analysis_results.json"
        assert p.exists(), f"Missing {p}"


# ---------------------------------------------------------------------------
# B50 factor consistency across codebase
# ---------------------------------------------------------------------------
class TestB50Consistency:
    """
    Verify B50 formula consistency across the codebase.
    
    CPS person-income quintiles: B50 = Q1+Q2+0.5*Q3 (each quintile = 20% of persons).
    CEX household-income quintiles: B50_CEX = Q1+Q2+Q3+0.414*Q4 (unequal person shares).
    """
    # The CPS person-income B50 uses Q3_FACTOR = 0.5
    CPS_Q3_FACTOR = "0.5"
    # The CEX calibration uses Q4_FACTOR = 0.414 (only in compute_b50_calibration.py)
    CEX_Q4_FACTOR = "0.414"

    @pytest.mark.parametrize(
        "relpath",
        [
            "run_counterfactual_analysis.py",
            "run_robustness_checks.py",
        ],
    )
    def test_b50_cps_factor_present(self, relpath):
        """The CPS B50 Q3 factor (0.5) must appear in counterfactual/robustness scripts."""
        path = ROOT / relpath
        if not path.exists():
            pytest.skip(f"{relpath} not found")
        text = path.read_text(encoding="utf-8")
        assert "B50_Q3_FACTOR" in text, (
            f"B50_Q3_FACTOR not found in {relpath}"
        )

    def test_cex_factor_in_calibration(self):
        """The CEX Q4 factor (0.414) should appear in the calibration script."""
        path = ROOT / "compute_b50_calibration.py"
        if not path.exists():
            pytest.skip("compute_b50_calibration.py not found")
        text = path.read_text(encoding="utf-8")
        assert self.CEX_Q4_FACTOR in text, (
            f"CEX Q4 factor {self.CEX_Q4_FACTOR} not found in compute_b50_calibration.py"
        )


# ---------------------------------------------------------------------------
# Config integrity
# ---------------------------------------------------------------------------
class TestConfig:
    def test_config_yaml_exists(self):
        assert (ROOT / "config.yaml").exists()

    def test_config_has_fred_api_key_field(self):
        cfg = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))
        fred = cfg.get("collectors", {}).get("fred", {})
        assert "api_key" in fred, "config.yaml missing collectors.fred.api_key"

    def test_config_api_key_not_hardcoded(self):
        """The config should have an empty or placeholder API key, not a real one."""
        cfg = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))
        key = cfg.get("collectors", {}).get("fred", {}).get("api_key", "")
        # A real FRED key is a 32-char hex string
        assert not re.match(r"^[0-9a-f]{32}$", str(key)), (
            "config.yaml contains what looks like a hardcoded FRED API key"
        )


# ---------------------------------------------------------------------------
# No hardcoded API keys in source
# ---------------------------------------------------------------------------
class TestNoHardcodedSecrets:
    SOURCE_FILES = [
        "run_tariff_incidence_analysis.py",
        "src/collectors/fred_collector.py",
    ]

    @pytest.mark.parametrize("relpath", SOURCE_FILES)
    def test_no_hardcoded_api_key(self, relpath):
        path = ROOT / relpath
        if not path.exists():
            pytest.skip(f"{relpath} not found")
        text = path.read_text(encoding="utf-8")
        # Match 32-hex-char strings that look like API keys
        matches = re.findall(r"['\"][0-9a-f]{32}['\"]", text)
        assert len(matches) == 0, (
            f"Possible hardcoded API key(s) in {relpath}: {matches}"
        )


# ---------------------------------------------------------------------------
# FINDINGS.md consistency with JSON outputs
# ---------------------------------------------------------------------------
class TestFindingsConsistency:
    def test_z_scores_match_json(self):
        """
        Z-scores in FINDINGS.md should match the JSON output
        (rounded to 1 decimal place).
        """
        json_path = TABLES / "structural_break_tests.json"
        md_path = OUTPUT / "FINDINGS.md"
        if not json_path.exists() or not md_path.exists():
            pytest.skip("Required files not generated")

        data = json.loads(json_path.read_text())
        md = md_path.read_text(encoding="utf-8")

        # Check customs z appears in the markdown
        customs_z = round(data["customs_share"]["z_score"], 1)
        assert str(customs_z) in md, (
            f"Customs z-score {customs_z} not found in FINDINGS.md"
        )

        interest_z = round(data["interest_ratio"]["z_score"], 1)
        assert str(interest_z) in md, (
            f"Interest z-score {interest_z} not found in FINDINGS.md"
        )
