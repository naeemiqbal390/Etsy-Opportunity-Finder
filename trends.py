"""
trends.py — Best-effort, keyless Google Trends lookup via pytrends.

IMPORTANT HONESTY NOTE:
pytrends is an unofficial wrapper around the public Google Trends website.
It requires no API key and costs nothing, BUT Google frequently rate-limits
or blocks requests coming from shared cloud IP ranges (like Streamlit
Community Cloud's), so this can fail intermittently or entirely depending
on where the app is hosted. Every function here fails soft: if pytrends
isn't installed, or Google blocks/errors the request, you get None back
(shown as "N/A" in the UI) instead of a crash or a fabricated number.

If you need reliable trend data in production, that means a paid data
provider (e.g. DataForSEO, SerpAPI) — there is no free, always-reliable
substitute for that.
"""

from typing import Optional, Dict

try:
    from pytrends.request import TrendReq

    _PYTRENDS_AVAILABLE = True
except ImportError:
    _PYTRENDS_AVAILABLE = False


def pytrends_available() -> bool:
    return _PYTRENDS_AVAILABLE


def get_trend_score(keyword: str, timeframe: str = "today 12-m") -> Optional[float]:
    """Returns a 0-100 relative interest score for a single keyword, or
    None if trend data could not be retrieved for any reason."""
    if not _PYTRENDS_AVAILABLE:
        return None
    try:
        pytrends = TrendReq(hl="en-US", tz=360, timeout=(5, 10))
        pytrends.build_payload([keyword], timeframe=timeframe)
        df = pytrends.interest_over_time()
        if df is None or df.empty or keyword not in df.columns:
            return None
        return round(float(df[keyword].mean()), 1)
    except Exception:
        # Any failure (blocked, rate-limited, network error, bad response
        # shape) degrades to "no data" rather than crashing the app.
        return None


def get_trend_scores_batch(keywords: list, timeframe: str = "today 12-m") -> Dict[str, Optional[float]]:
    """Looks up trend scores one keyword at a time (pytrends batches up to
    5 keywords per call, but comparing keywords against each other skews
    the 0-100 scale, so we score each independently instead)."""
    results = {}
    for kw in keywords:
        kw = kw.strip()
        if not kw:
            continue
        results[kw] = get_trend_score(kw, timeframe=timeframe)
    return results
