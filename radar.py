"""
radar.py — Digital Product Demand Radar.

Classifies pasted keywords by buyer-intent level and likely product type
using pure regex pattern matching (no API calls, no fabricated numbers).
Combines that with optional trend data and manual Etsy evidence to produce
an opportunity score and a recommended action, then hands off to db.py so
entries accumulate into a monthly archive.
"""

import re
from datetime import datetime
from typing import Optional

from data import INTENT_LEVELS, PRODUCT_TYPE_PATTERNS, ACTION_BUCKETS


def classify_intent(query: str) -> dict:
    """Returns the highest-matching intent level for a query.
    Falls back to level 1 (Informational) if nothing matches, since an
    unclassified query should never be silently treated as high-intent.
    """
    q = query.lower()
    for level in sorted(INTENT_LEVELS.keys(), reverse=True):
        info = INTENT_LEVELS[level]
        for pattern in info["patterns"]:
            if re.search(pattern, q):
                return {"level": level, "label": info["label"], "emoji": info["emoji"]}
    fallback = INTENT_LEVELS[1]
    return {"level": 1, "label": fallback["label"], "emoji": fallback["emoji"]}


def classify_product_type(query: str) -> str:
    q = query.lower()
    for label, pattern in PRODUCT_TYPE_PATTERNS:
        if re.search(pattern, q):
            return label
    return "Unclassified"


def compute_action(score: Optional[float]) -> str:
    if score is None:
        return "⚪ Not enough evidence"
    for threshold, label in ACTION_BUCKETS:
        if score >= threshold:
            return label
    return ACTION_BUCKETS[-1][1]


def score_query(
    query: str,
    trend_score: Optional[float] = None,
    etsy_listings: Optional[float] = None,
    etsy_top_price: Optional[float] = None,
    etsy_avg_reviews: Optional[float] = None,
) -> dict:
    """Combine intent classification with whatever evidence is available.
    Every numeric input is optional — the score only reflects fields you
    actually supplied, and is None (not a guess) when nothing was supplied.
    """
    intent = classify_intent(query)
    product_type = classify_product_type(query)

    # Intent contributes a base score: product-aware queries are worth more
    # because they signal someone is close to a purchase decision.
    intent_score = {1: 30, 2: 60, 3: 85}[intent["level"]]

    evidence_parts = [intent_score]
    weights = [0.30]

    if trend_score is not None:
        evidence_parts.append(max(0, min(100, trend_score)))
        weights.append(0.25)

    if etsy_listings is not None and etsy_listings > 0:
        import math

        scarcity = max(0, min(100, 100 - 18 * math.log10(max(1, etsy_listings))))
        evidence_parts.append(scarcity)
        weights.append(0.25)

    if etsy_top_price:
        price_factor = min(100, (etsy_top_price / 30.0) * 100)
        evidence_parts.append(price_factor)
        weights.append(0.10)

    if etsy_avg_reviews is not None and etsy_avg_reviews > 0:
        review_gap = max(0, min(100, 100 - (etsy_avg_reviews / 5.0)))
        evidence_parts.append(review_gap)
        weights.append(0.10)

    total_weight = sum(weights)
    score = round(sum(p * w for p, w in zip(evidence_parts, weights)) / total_weight, 1)

    evidence_count = sum(
        [
            trend_score is not None,
            bool(etsy_listings),
            bool(etsy_top_price),
            bool(etsy_avg_reviews),
        ]
    )

    return {
        "query": query,
        "intent_level": intent["level"],
        "intent_label": intent["label"],
        "intent_emoji": intent["emoji"],
        "product_type": product_type,
        "trend_score": trend_score,
        "etsy_listings": etsy_listings,
        "etsy_top_price": etsy_top_price,
        "etsy_avg_reviews": etsy_avg_reviews,
        "score": score,
        "evidence_count": evidence_count,
        "action": compute_action(score) if evidence_count >= 1 else "⚪ Not enough evidence",
        "month_tag": datetime.now().strftime("%Y-%m"),
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }


def score_batch(queries: list, trend_lookup: Optional[dict] = None) -> list:
    """Score a list of raw query strings. trend_lookup, if given, maps
    query -> trend score (0-100) e.g. from trends.py."""
    trend_lookup = trend_lookup or {}
    return [score_query(q.strip(), trend_score=trend_lookup.get(q.strip())) for q in queries if q.strip()]
