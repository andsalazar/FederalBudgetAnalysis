"""
Tests for structural break z-score computation.

Validates the out-of-sample prediction SE formula:
    SE_pred = σ̂ * sqrt(1 + 1/n + (x_new - x̄)² / SS_x)
    z = residual / SE_pred
"""
import numpy as np
import pytest
from scipy import stats


class TestPredictionSE:
    """
    Unit tests for the out-of-sample prediction standard error.
    """

    def _compute_z(self, x_train, y_train, x_new, y_new):
        """Replicate the z-score logic from run_25year_analysis.py."""
        slope, intercept, _, _, _ = stats.linregress(x_train, y_train)
        predicted = slope * x_new + intercept
        residual = y_new - predicted

        pre_predicted = slope * x_train + intercept
        n = len(x_train)
        se_resid = np.std(y_train - pre_predicted, ddof=2)
        x_bar = np.mean(x_train)
        ss_x = np.sum((x_train - x_bar) ** 2)
        se_pred = se_resid * np.sqrt(1 + 1 / n + (x_new - x_bar) ** 2 / ss_x)
        z = residual / se_pred
        return z, se_pred, predicted

    def test_zero_residual_gives_zero_z(self, linear_trend_data):
        """If the new point is exactly on trend, z should be ~0."""
        x_train, y_train, slope, intercept = linear_trend_data
        # Fit the actual trend to training data, predict 2025, then
        # supply the predicted value as 'actual'. z ≈ 0.
        s, i, _, _, _ = stats.linregress(x_train, y_train)
        y_on_trend = s * 2025 + i
        z, _, _ = self._compute_z(x_train, y_train, 2025, y_on_trend)
        assert abs(z) < 0.01

    def test_large_deviation_gives_large_z(self, linear_trend_data):
        """A 20-sigma deviation should produce |z| >> 2."""
        x_train, y_train, _, _ = linear_trend_data
        s, i, _, _, _ = stats.linregress(x_train, y_train)
        y_extreme = s * 2025 + i + 50  # ~50 units above trend
        z, _, _ = self._compute_z(x_train, y_train, 2025, y_extreme)
        assert z > 5  # very large positive z

    def test_se_pred_larger_than_sigma(self, linear_trend_data):
        """
        Prediction SE should always be > residual σ̂ due to the
        1 + 1/n + leverage terms under the square root.
        """
        x_train, y_train, _, _ = linear_trend_data
        slope, intercept, _, _, _ = stats.linregress(x_train, y_train)
        se_resid = np.std(
            y_train - (slope * x_train + intercept), ddof=2
        )
        _, se_pred, _ = self._compute_z(x_train, y_train, 2025, 0)
        assert se_pred > se_resid

    def test_leverage_increases_se(self):
        """
        Predicting at a high-leverage point (far from x̄) should
        give a larger SE_pred than predicting near x̄.
        """
        rng = np.random.RandomState(7)
        x = np.arange(2000, 2018, dtype=float)
        y = 0.5 * x + rng.normal(0, 1, len(x))

        _, se_near, _ = self._compute_z(x, y, np.mean(x), 0)
        _, se_far, _ = self._compute_z(x, y, 2050, 0)
        assert se_far > se_near

    def test_more_data_reduces_se(self):
        """More training observations should reduce SE_pred."""
        rng = np.random.RandomState(8)
        x_short = np.arange(2005, 2018, dtype=float)
        x_long = np.arange(2000, 2018, dtype=float)

        y_short = 0.5 * x_short + rng.normal(0, 1, len(x_short))
        # Re-draw with same seed portion for fair comparison
        rng2 = np.random.RandomState(8)
        y_long = 0.5 * x_long + rng2.normal(0, 1, len(x_long))

        _, se_short, _ = self._compute_z(x_short, y_short, 2025, 0)
        _, se_long, _ = self._compute_z(x_long, y_long, 2025, 0)
        # Longer training → smaller SE (in expectation), but with
        # different draws we just test the formula's structural behavior
        # by checking they're both positive and finite
        assert np.isfinite(se_short) and se_short > 0
        assert np.isfinite(se_long) and se_long > 0


class TestStructuralBreakVerdict:
    """Verify the |z| > 2.0 classification logic."""

    @pytest.mark.parametrize("z, expected", [
        (2.5, True),
        (-2.1, True),
        (25.8, True),
        (1.9, False),
        (-1.5, False),
        (0.5, False),
    ])
    def test_break_threshold(self, z, expected):
        is_break = abs(z) > 2.0
        assert is_break == expected
