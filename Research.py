"""
research.py — External link generation, evidence metrics, and scoring.
"""

import math
import urllib.parse

def build_research_links(keyword: str) -> dict:
    encoded = urllib.parse.quote(keyword)
    return {
        "Etsy": f"https://www.etsy.com/search?q={encoded}",
        "Google": f"https://www.google.com/search?q={encoded}",
        "Google Trends": f"https://trends.google.com/trends/explore?q={encoded}",
        "Reddit": f"https://www.reddit.com/search/?q={encoded}",
        "Pinterest": f"https://www.pinterest.com/search/pins/?q={encoded}"
    }

def calculate_demand_score(searches: int, trend: float) -> float | None:
    if searches is None or searches == 0:
        return None
    s = min(100, 20 * math.log10(max(1, searches)))
    t = max(0, min(100, trend)) if trend is not None else 50
    return round(0.70 * s + 0.30 * t, 1)

def calculate_competition_score(listings: int, top_price: float, avg_reviews: int) -> float | None:
    if listings is None or listings == 0:
        return None
    scarcity = max(0, min(100, 100 - 18 * math.log10(max(1, listings))))
    price_factor = min(100, (top_price / 30.0) * 100) if top_price else 50
    review_gap = max(0, min(100, 100 - (avg_reviews / 5.0))) if avg_reviews else 50
    return round(0.50 * scarcity + 0.30 * price_factor + 0.20 * review_gap, 1)

def calculate_opportunity_score(demand: float | None, competition: float | None, pain: float, diff: float) -> float | None:
    if demand is None or competition is None:
        return None
    return round(0.35 * demand + 0.35 * competition + 0.15 * pain + 0.15 * diff, 1)

def calculate_evidence_confidence(inputs: dict) -> float:
    total_fields = 7
    provided = 0
    if inputs.get("searches", 0) > 0: provided += 1
    if inputs.get("listings", 0) > 0: provided += 1
    if inputs.get("top_price", 0) > 0: provided += 1
    if inputs.get("avg_reviews", 0) > 0: provided += 1
    if inputs.get("trend", 50) != 50: provided += 1
    if inputs.get("reddit_volume", 0) > 0: provided += 1
    if inputs.get("pinterest_interest", 0) > 0: provided += 1
    
    return round((provided / total_fields) * 100, 1)
