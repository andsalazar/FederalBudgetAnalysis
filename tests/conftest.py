"""
Shared fixtures for the Federal Budget Analysis test suite.
"""
import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def rng():
    """Seeded random state for reproducible tests."""
    return np.random.RandomState(12345)


@pytest.fixture
def synthetic_quarterly_series():
    """
    Synthetic quarterly time series with a known intervention effect.
    100 pre-intervention periods + 10 post-intervention periods.
    Pre: y = 50 + 0.5*t + noise
    Post: level shift +20, trend change -0.3/quarter
    """
    rng = np.random.RandomState(42)
    n_pre, n_post = 100, 10
    n = n_pre + n_post

    dates = pd.date_range("2000-01-01", periods=n, freq="QS")
    t = np.arange(n, dtype=float)

    y = 50 + 0.5 * t + rng.normal(0, 2, n)
    # Add known intervention effect after period n_pre
    y[n_pre:] += 20  # level shift
    y[n_pre:] += -0.3 * np.arange(n_post)  # trend change

    series = pd.Series(y, index=dates, name="test_series")
    intervention_date = str(dates[n_pre].date())
    return series, intervention_date


@pytest.fixture
def cps_micro_sample(rng):
    """
    Small synthetic CPS ASEC-like microdata for bootstrap testing.
    50 households, ~2.5 persons each ≈ 125 rows.
    """
    rows = []
    hh_ids = np.arange(1, 51)
    for hh in hh_ids:
        n_persons = rng.choice([1, 2, 3, 4], p=[0.2, 0.4, 0.3, 0.1])
        hh_base_income = rng.lognormal(10, 1.2)
        for _ in range(n_persons):
            rows.append({
                "PH_SEQ": hh,
                "MARSUPWT": rng.uniform(500, 3000),
                "pretax_income": hh_base_income * rng.uniform(0.0, 1.5),
            })
    return pd.DataFrame(rows)


@pytest.fixture
def linear_trend_data():
    """
    Clean linear trend for testing structural break z-score formula.
    y = 2.0 + 0.5*x, with known residual std = 1.0.
    Training: x in [2000..2017], break test at x=2025.
    """
    rng = np.random.RandomState(99)
    x_train = np.arange(2000, 2018, dtype=float)
    slope, intercept = 0.5, 2.0
    noise = rng.normal(0, 1.0, len(x_train))
    y_train = intercept + slope * x_train + noise
    return x_train, y_train, slope, intercept
