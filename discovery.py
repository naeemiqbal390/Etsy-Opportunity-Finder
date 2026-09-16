"""
discovery.py — Automated monthly Opportunity Finder scan.

Generates candidate search phrases itself (no user typing), optionally
expands them via best-effort Google Trends related-queries, filters out
excluded categories (books, Notion, Canva), classifies + scores every
candidate, and ranks them into a monthly Top N shortlist.

Nothing here claims to be "every search on the internet" — it's a large,
realistic, combinatorially-generated seed pool plus whatever real related
queries Google Trends is willing to hand back for free on a given day.
Competition is NOT estimated automatically (no free, reliable source for
that exists) — each shortlisted candidate instead gets a research link so
you can check it yourself.
"""

import random
import re
from datetime import datetime
from typing import List, Dict, Optional

from data import SEED_NICHES, SEED_PRODUCT_TERMS, EXCLUDE_PATTERNS
from radar import classify_intent, classify_product_type
from trends import pytrends_available, get_trend_score


def generate_seed_candidates(limit: Optional[int] = None) -> List[str]:
    """Combinatorially build realistic search phrases from niches x product
    terms. Order is shuffled so a limited/sampled run isn't biased toward
    the first niches in the list."""
    candidates = []
    for niche in SEED_NICHES:
        for term in SEED_PRODUCT_TERMS:
            candidates.append(f"{niche} {term}")
    random.shuffle(candidates)
    if limit:
        candidates = candidates[:limit]
    return candidates


def _is_excluded(query: str) -> bool:
    q = query.lower()
    return any(re.search(p, q) for p in EXCLUDE_PATTERNS)


def expand_with_related_queries(seed_keywords: List[str], max_seeds_to_expand: int = 15) -> List[str]:
    """Best-effort: ask Google Trends for real related queries on a sample
    of seeds. Returns only the expansion results (not the seeds themselves).
    Fails soft to an empty list if pytrends is unavailable or blocked."""
    if not pytrends_available():
        return []
    expanded = []
    try:
        from pytrends.request import TrendReq

        pytrends = TrendReq(hl="en-US", tz=360, timeout=(5, 10))
        sample = seed_keywords[:max_seeds_to_expand]
        for kw in sample:
            try:
                pytrends.build_payload([kw], timeframe="today 12-m")
                related = pytrends.related_queries()
                data = related.get(kw, {})
                for key in ("top", "rising"):
                    df = data.get(key)
                    if df is not None and not df.empty and "query" in df.columns:
                        expanded.extend(df["query"].tolist())
            except Exception:
                # This one seed failed (rate limit, no data, etc.) — skip it
                # and keep going with the rest of the sample.
                continue
    except Exception:
        return expanded
    return expanded


def run_monthly_scan(
    seed_limit: int = 300,
    expand: bool = True,
    max_seeds_to_expand: int = 15,
    top_n: int = 100,
) -> Dict:
    """Runs the full automated pipeline and returns a dict with the ranked
    shortlist plus metadata about what was actually possible this run
    (e.g. whether trend expansion worked at all)."""
    seeds = generate_seed_candidates(limit=seed_limit)

    expanded = []
    trends_worked = False
    if expand:
        expanded = expand_with_related_queries(seeds, max_seeds_to_expand=max_seeds_to_expand)
        trends_worked = len(expanded) > 0

    all_candidates = list(dict.fromkeys(seeds + expanded))  # dedupe, keep order
    all_candidates = [c for c in all_candidates if not _is_excluded(c)]

    scored = []
    trend_scores_fetched = 0
    for query in all_candidates:
        intent = classify_intent(query)
        # Skip pure informational queries — no buying intent to act on.
        if intent["level"] == 1:
            continue
        product_type = classify_product_type(query)

        trend_score = None
        # Only spend trend-lookup budget on candidates that already show
        # buying intent, and only if expansion worked at all this run.
        if expand and trends_worked and trend_scores_fetched < max_seeds_to_expand:
            trend_score = get_trend_score(query)
            if trend_score is not None:
                trend_scores_fetched += 1

        intent_base = {2: 60, 3: 85}[intent["level"]]
        if trend_score is not None:
            score = round(0.6 * intent_base + 0.4 * trend_score, 1)
        else:
            score = intent_base

        scored.append(
            {
                "query": query,
                "intent_level": intent["level"],
                "intent_label": intent["label"],
                "intent_emoji": intent["emoji"],
                "product_type": product_type,
                "trend_score": trend_score,
                "score": score,
            }
        )

    scored.sort(key=lambda e: e["score"], reverse=True)

    # Flag possible hidden gems: clear buying intent, but trend data (when
    # available) suggests low search volume -- exactly the "low search,
    # maybe low competition" pattern worth checking manually.
    trend_values = [e["trend_score"] for e in scored if e["trend_score"] is not None]
    median_trend = sorted(trend_values)[len(trend_values) // 2] if trend_values else None

    for e in scored:
        if e["intent_level"] == 3 and median_trend is not None and e["trend_score"] is not None and e["trend_score"] < median_trend:
            e["hidden_gem"] = True
        else:
            e["hidden_gem"] = False

    month_tag = datetime.now().strftime("%Y-%m")
    for e in scored:
        e["month_tag"] = month_tag
        e["created_at"] = datetime.now().isoformat(timespec="seconds")

    return {
        "shortlist": scored[:top_n],
        "total_candidates_generated": len(seeds),
        "total_after_expansion_and_filtering": len(all_candidates),
        "trends_worked": trends_worked,
        "trend_scores_fetched": trend_scores_fetched,
        "month_tag": month_tag,
    }
