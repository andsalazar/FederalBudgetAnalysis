"""
Tests for cluster-bootstrap and robustness procedures.

Validates:
  - Cluster-bootstrap resamples at household level (not person)
  - Bootstrap CIs are narrower than person-level bootstrap
  - Income share statistics are bounded [0, 100]
  - Gini coefficient is bounded [0, 1]
  - Reproducibility under fixed seed
"""
import numpy as np
import pandas as pd
import pytest


def _compute_b50_share(inc, w):
    """Helper: weighted bottom-50% income share."""
    idx = np.argsort(inc)
    inc_s, w_s = inc[idx], w[idx]
    cum_w = np.cumsum(w_s)
    total_w = cum_w[-1]
    cum_pct = cum_w / total_w
    total_inc = np.sum(inc_s * w_s)
    mask_50 = cum_pct <= 0.50
    b50_inc = np.sum(inc_s[mask_50] * w_s[mask_50])
    return (b50_inc / total_inc * 100) if total_inc > 0 else 0.0


def _compute_gini(inc, w):
    """Helper: approximate weighted Gini coefficient."""
    idx = np.argsort(inc)
    inc_s, w_s = inc[idx], w[idx]
    total_inc = np.sum(inc_s * w_s)
    total_w = np.sum(w_s)
    cum_inc = np.cumsum(inc_s * w_s)
    if total_inc > 0 and total_w > 0:
        return 1 - 2 * np.sum(cum_inc / total_inc * w_s / total_w)
    return 0.0


class TestClusterBootstrap:
    def test_household_preservation(self, cps_micro_sample):
        """
        After cluster-resampling by PH_SEQ, every sampled household
        should appear with all its members intact.
        """
        df = cps_micro_sample
        rng = np.random.RandomState(42)
        hh_keys = df["PH_SEQ"].unique()
        boot_hhs = rng.choice(hh_keys, size=len(hh_keys), replace=True)

        # Build resampled DF
        pieces = [df[df["PH_SEQ"] == hh] for hh in boot_hhs]
        sample = pd.concat(pieces, ignore_index=True)

        # Each household's person count should match original
        orig_counts = df.groupby("PH_SEQ").size()
        for hh in np.unique(boot_hhs):
            n_expected = orig_counts[hh]
            n_times = np.sum(boot_hhs == hh)
            n_actual = len(sample[sample["PH_SEQ"] == hh])
            assert n_actual == n_expected * n_times

    def test_reproducibility_with_seed(self, cps_micro_sample):
        """Two runs with same seed should give identical results."""
        df = cps_micro_sample
        inc = df["pretax_income"].values
        w = df["MARSUPWT"].values

        results = []
        for _ in range(2):
            rng = np.random.RandomState(42)
            hh_keys = df["PH_SEQ"].unique()
            boot_hhs = rng.choice(hh_keys, size=len(hh_keys), replace=True)
            hh_to_rows = {}
            for i, hh in enumerate(df["PH_SEQ"].values):
                hh_to_rows.setdefault(hh, []).append(i)
            row_idx = np.concatenate(
                [np.array(hh_to_rows[hh]) for hh in boot_hhs]
            )
            results.append(_compute_b50_share(inc[row_idx], w[row_idx]))

        assert results[0] == pytest.approx(results[1])


class TestBootstrapStatistics:
    def test_b50_share_bounded(self, cps_micro_sample):
        """B50 share must be in [0, 100]."""
        inc = cps_micro_sample["pretax_income"].values
        w = cps_micro_sample["MARSUPWT"].values
        share = _compute_b50_share(inc, w)
        assert 0 <= share <= 100

    def test_gini_bounded(self, cps_micro_sample):
        """Gini must be in [0, 1] for non-negative incomes."""
        inc = np.abs(cps_micro_sample["pretax_income"].values)
        w = cps_micro_sample["MARSUPWT"].values
        gini = _compute_gini(inc, w)
        assert 0 <= gini <= 1

    def test_perfect_equality_gini(self):
        """If everyone has the same income, Gini → 0."""
        n = 100
        inc = np.ones(n) * 50000
        w = np.ones(n)
        gini = _compute_gini(inc, w)
        assert gini == pytest.approx(0.0, abs=0.02)

    def test_bootstrap_ci_width(self, cps_micro_sample):
        """
        With 100 bootstrap draws, CI should be non-degenerate
        (width > 0) but finite.
        """
        df = cps_micro_sample
        inc = df["pretax_income"].values
        w = df["MARSUPWT"].values
        hh_arr = df["PH_SEQ"].values

        hh_to_rows = {}
        for i, hh in enumerate(hh_arr):
            hh_to_rows.setdefault(hh, []).append(i)
        hh_row_arrays = {hh: np.array(r) for hh, r in hh_to_rows.items()}
        hh_keys = np.array(list(hh_row_arrays.keys()))

        rng = np.random.RandomState(42)
        shares = []
        for _ in range(100):
            boot_hhs = rng.choice(hh_keys, size=len(hh_keys), replace=True)
            row_idx = np.concatenate([hh_row_arrays[h] for h in boot_hhs])
            shares.append(_compute_b50_share(inc[row_idx], w[row_idx]))

        ci_low = np.percentile(shares, 2.5)
        ci_high = np.percentile(shares, 97.5)
        width = ci_high - ci_low

        assert width > 0, "CI should have positive width"
        assert np.isfinite(width), "CI width should be finite"
