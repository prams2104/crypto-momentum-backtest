import numpy as np
import pandas as pd

def calc_returns(px: pd.DataFrame) -> pd.DataFrame:
    return px / px.shift(1) - 1

def calc_stats(ret_series: pd.Series, ann: int = 365) -> pd.Series:
    """Calculate strategy performance metrics"""
    stats = {}
    
    # Annualized return
    stats['Return'] = ret_series.mean() * ann
    
    # Annualized volatility
    stats['Vol'] = ret_series.std() * np.sqrt(ann)
    
    # Sharpe ratio
    stats['Sharpe'] = stats['Return'] / stats['Vol'] if stats['Vol'] > 0 else 0
    
    # Max drawdown
    cum_ret = (1 + ret_series).cumprod()
    running_max = cum_ret.cummax()
    drawdown = (cum_ret / running_max) - 1
    stats['MaxDD'] = drawdown.min()
    
    # Win rate
    stats['WinRate'] = (ret_series > 0).mean()
    
    return pd.Series(stats)

def winsorize_xs(df: pd.DataFrame, p = 0.01) -> pd.DataFrame:
    low = df.quantile(p, axis=1)
    high = df.quantile(1-p, axis=1)
    return df.clip(lower = low, upper = high, axis = 0)

def winsorize_ts(df: pd.DataFrame, lower=-0.30, upper=0.30) -> pd.DataFrame:
    """Winsorize time-series (cap absolute values)"""
    return df.clip(lower=lower, upper=upper)

def rank_signal_xs(sig: pd.DataFrame, elig: pd.DataFrame = None) -> pd.DataFrame:
    if elig is not None:
        sig = sig.where(elig)   # keep only eligible
    # pct ranks within each day; keeps scale stable
    return sig.rank(axis=1, pct=True)


def demean_xs(df: pd.DataFrame) -> pd.DataFrame:
    return df.subtract(df.mean(axis=1), axis=0)

def demean_xs_masked(df: pd.DataFrame, mask: pd.DataFrame) -> pd.DataFrame:
    x = df.where(mask)
    mu = x.mean(axis=1, skipna=True)
    x = x.sub(mu, axis=0)
    return x.where(mask, 0.0).fillna(0.0)

def normalize_weights_masked(w: pd.DataFrame, mask: pd.DataFrame) -> pd.DataFrame:
    x = w.where(mask, 0.0)
    denom = x.abs().sum(axis=1).replace(0, np.nan)
    return x.div(denom, axis=0).fillna(0.0)


def normalize_weights(w: pd.DataFrame) -> pd.DataFrame:
    denom = w.abs().sum(axis=1).replace(0, np.nan)
    return w.divide(denom, axis=0).fillna(0.0)

# Execution weights: shift(1) + enforce eligibility + renormalize
def calc_exec_weights(port, elig):
    """Calculate execution weights with proper eligibility enforcement"""
    # Yesterday's weights (what we decided)
    w_exec = port.shift(1).fillna(0)
    
    # Can only hold eligible assets TODAY (when returns realize)
    w_exec = w_exec.where(elig, 0.0)
    
    # Renormalize to maintain consistent leverage
    # (keeps sum|w| = 1 among eligible assets)
    w_exec = normalize_weights(w_exec)
    
    return w_exec

def zscore_xs(df: pd.DataFrame) -> pd.DataFrame:
    mu = df.mean(axis=1)
    sd = df.std(axis=1).replace(0, np.nan)
    return df.sub(mu, axis=0).div(sd, axis=0)

def apply_eligibility(df: pd.DataFrame, elig: pd.DataFrame) -> pd.DataFrame:
    return df.where(elig, 0.0).fillna(0.0)




