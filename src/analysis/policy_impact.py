"""
Policy impact analysis module.

Provides tools for:
- Event study / interrupted time-series analysis around policy changes
- Structural break detection
- Counterfactual estimation
- Distributional impact analysis
"""

from typing import Optional, Tuple

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from scipy import stats
from loguru import logger

from src.utils.config import load_config
from src.database.models import get_session, Observation


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

def load_series(series_id: str, start_date: str = None, end_date: str = None) -> pd.Series:
    """
    Load a time series from the database as a pandas Series indexed by date.
    """
    session = get_session()
    query = session.query(Observation).filter(Observation.series_id == series_id)

    if start_date:
        query = query.filter(Observation.date >= start_date)
    if end_date:
        query = query.filter(Observation.date <= end_date)

    query = query.order_by(Observation.date)
    rows = query.all()
    session.close()

    if not rows:
        logger.warning(f"No data found for series '{series_id}'")
        return pd.Series(dtype=float)

    dates = [r.date for r in rows]
    values = [r.value for r in rows]
    series = pd.Series(values, index=pd.DatetimeIndex(dates), name=series_id)
    return series


def load_multiple_series(series_ids: list, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """Load multiple series and align them into a DataFrame."""
    frames = {}
    for sid in series_ids:
        s = load_series(sid, start_date, end_date)
        if not s.empty:
            frames[sid] = s
    if not frames:
        return pd.DataFrame()
    df = pd.DataFrame(frames)
    return df


# ---------------------------------------------------------------------------
# Structural break & stationarity tests
# ---------------------------------------------------------------------------

def test_stationarity(series: pd.Series, significance: float = 0.05) -> dict:
    """
    Augmented Dickey-Fuller test for stationarity.

    Returns dict with test statistic, p-value, and whether the series is stationary.
    """
    result = adfuller(series.dropna(), autolag="AIC")
    return {
        "test_statistic": result[0],
        "p_value": result[1],
        "lags_used": result[2],
        "n_observations": result[3],
        "critical_values": result[4],
        "is_stationary": result[1] < significance,
    }


def chow_test(
    y: pd.Series, x: pd.DataFrame, break_date: str
) -> dict:
    """
    Chow test for structural break at a given date.

    Tests whether regression coefficients differ before vs. after break_date.
    """
    break_dt = pd.Timestamp(break_date)
    mask_pre = y.index < break_dt
    mask_post = y.index >= break_dt

    if mask_pre.sum() < 5 or mask_post.sum() < 5:
        logger.warning("Insufficient observations for Chow test")
        return {"error": "Insufficient observations"}

    y_pre, x_pre = y[mask_pre], x[mask_pre]
    y_post, x_post = y[mask_post], x[mask_post]

    def _ssr(y_sub, x_sub):
        x_c = sm.add_constant(x_sub)
        model = sm.OLS(y_sub.values, x_c.values).fit()
        return model.ssr, model.df_resid

    ssr_full_x = sm.add_constant(x)
    ssr_full = sm.OLS(y.values, ssr_full_x.values).fit().ssr

    ssr1, df1 = _ssr(y_pre, x_pre)
    ssr2, df2 = _ssr(y_post, x_post)

    k = x.shape[1] + 1  # number of parameters including constant
    n = len(y)

    f_stat = ((ssr_full - (ssr1 + ssr2)) / k) / ((ssr1 + ssr2) / (n - 2 * k))
    p_value = 1 - stats.f.cdf(f_stat, k, n - 2 * k)

    return {
        "f_statistic": f_stat,
        "p_value": p_value,
        "break_date": break_date,
        "is_significant": p_value < 0.05,
    }


# ---------------------------------------------------------------------------
# Event study / interrupted time-series
# ---------------------------------------------------------------------------

def interrupted_time_series(
    series: pd.Series,
    intervention_date: str,
    pre_periods: int = None,
    post_periods: int = None,
) -> dict:
    """
    Interrupted Time Series (ITS) analysis.

    Fits a segmented regression:
        Y_t = β0 + β1*time + β2*intervention + β3*time_after_intervention + ε_t

    Parameters
    ----------
    series : pd.Series with DatetimeIndex
    intervention_date : str, date of the policy intervention
    pre_periods : int, optional, number of periods before intervention to include
    post_periods : int, optional, number of periods after intervention to include

    Returns
    -------
    dict with model results
    """
    intervention_dt = pd.Timestamp(intervention_date)
    s = series.dropna().sort_index()

    if pre_periods:
        start_idx = s.index.searchsorted(intervention_dt) - pre_periods
        s = s.iloc[max(0, start_idx):]
    if post_periods:
        end_idx = s.index.searchsorted(intervention_dt) + post_periods
        s = s.iloc[:min(len(s), end_idx)]

    # Construct ITS regressors
    time_var = np.arange(len(s))
    intervention = (s.index >= intervention_dt).astype(int)
    time_after = np.where(intervention, time_var - time_var[intervention.argmax()], 0)

    X = pd.DataFrame({
        "time": time_var,
        "intervention": intervention,
        "time_after": time_after,
    }, index=s.index)

    X_const = sm.add_constant(X)
    # Use HAC (Newey-West) standard errors to correct for serial correlation
    # in time series data. Lag length follows Schwert (1989): L ≈ 0.75 * T^(1/3)
    n_obs = len(s)
    max_lags = max(1, int(0.75 * (n_obs ** (1/3))))
    model = sm.OLS(s.values, X_const.astype(float)).fit(
        cov_type='HAC', cov_kwds={'maxlags': max_lags}
    )

    # Counterfactual: predicted values without intervention
    X_counter = X_const.copy()
    X_counter["intervention"] = 0
    X_counter["time_after"] = 0
    counterfactual = model.predict(X_counter.astype(float))

    return {
        "model_summary": model.summary2().as_text(),
        "params": model.params.to_dict(),
        "pvalues": model.pvalues.to_dict(),
        "r_squared": model.rsquared,
        "intervention_effect": model.params.get("intervention", 0),
        "trend_change": model.params.get("time_after", 0),
        "actual": s,
        "fitted": pd.Series(model.fittedvalues, index=s.index),
        "counterfactual": pd.Series(counterfactual, index=s.index),
    }


# ---------------------------------------------------------------------------
# Welfare / distributional helpers
# ---------------------------------------------------------------------------

def compute_real_values(
    nominal_series: pd.Series,
    cpi_series: pd.Series,
    base_year: int = 2023,
) -> pd.Series:
    """Convert nominal values to real (inflation-adjusted) values using CPI."""
    # Align frequencies
    combined = pd.DataFrame({"nominal": nominal_series, "cpi": cpi_series}).dropna()

    if combined.empty:
        return pd.Series(dtype=float)

    # Find base period CPI
    base_mask = combined.index.year == base_year
    if base_mask.any():
        base_cpi = combined.loc[base_mask, "cpi"].mean()
    else:
        base_cpi = combined["cpi"].iloc[-1]

    real_values = combined["nominal"] * (base_cpi / combined["cpi"])
    real_values.name = f"{nominal_series.name}_real_{base_year}"
    return real_values


def percent_change_around_event(
    series: pd.Series,
    event_date: str,
    window_years: int = 3,
) -> dict:
    """Calculate percent change in a series around a policy event."""
    event_dt = pd.Timestamp(event_date)
    pre_start = event_dt - pd.DateOffset(years=window_years)
    post_end = event_dt + pd.DateOffset(years=window_years)

    pre = series.loc[pre_start:event_dt]
    post = series.loc[event_dt:post_end]

    if pre.empty or post.empty:
        return {"error": "Insufficient data around event"}

    pre_mean = pre.mean()
    post_mean = post.mean()
    pct_change = ((post_mean - pre_mean) / abs(pre_mean)) * 100

    return {
        "event_date": event_date,
        "window_years": window_years,
        "pre_mean": pre_mean,
        "post_mean": post_mean,
        "pct_change": pct_change,
        "pre_n": len(pre),
        "post_n": len(post),
    }
