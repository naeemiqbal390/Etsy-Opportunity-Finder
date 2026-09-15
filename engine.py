"""
engine.py — Core discovery, weirdness transformer, and commercialization generator.
Pure Python — no API keys or network calls.
"""

import random
import re
from datetime import datetime
from typing import List, Dict

from data import PROBLEMS, BUYERS, FORMATS, WEIRD_REFRAMES, RISK_PATTERNS


def clean_slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def generate_base_idea() -> dict:
    problem, pdesc = random.choice(PROBLEMS)
    buyer, bdesc = random.choice(BUYERS)
    fmt, mult = random.choice(FORMATS)

    product = f"{fmt.title()} for {buyer}: {problem.title()}"
    hook = random.choice(
        [
            "What if the thing you keep postponing is actually the thing you value most?",
            "Turn an invisible problem into a clear number, decision, or system.",
            "The problem people feel long before they know what to call it.",
            "Solve the awkward part before it becomes an emergency.",
        ]
    )

    keywords = [
        f"{problem} {fmt}",
        f"{buyer} {fmt}",
        f"{problem} planner",
        f"{problem} tracker",
        f"{problem} template",
    ]

    return {
        "problem": problem,
        "problem_desc": pdesc,
        "buyer": buyer,
        "buyer_desc": bdesc,
        "format": fmt,
        "product": product,
        "hook": hook,
        "keywords": keywords,
        "created": datetime.now().isoformat(timespec="seconds"),
    }


def make_it_weirder(idea: dict) -> dict:
    problem = idea["problem"]
    reframes = WEIRD_REFRAMES.get(
        problem,
        [
            f"The Anti-{problem.title()} Experiment",
            f"Uncomfortable Questions About {problem.title()}",
            f"The Radical {problem.title()} Blueprint",
        ],
    )
    chosen_reframe = random.choice(reframes)

    weird_idea = dict(idea)
    weird_idea["product"] = f"{chosen_reframe} ({idea['format'].title()})"
    weird_idea["hook"] = (
        f"An unconventional approach to {idea['problem_desc']} specifically built for {idea['buyer']}."
    )
    return weird_idea


def generate_why_it_fails(idea: dict) -> List[Dict]:
    n = min(3, len(RISK_PATTERNS))
    return random.sample(RISK_PATTERNS, n)


def commercialize_idea(idea: dict) -> dict:
    title = f"{idea['product']} | Printable & Digital Instant Download"
    tags = [clean_slug(kw).replace("-", " ") for kw in idea["keywords"]][:13]

    return {
        "product_spec": f"A comprehensive {idea['format']} designed to address {idea['problem_desc']}.",
        "pages_features": [
            "Interactive Dashboard",
            "Step-by-step Setup Guide",
            "Actionable Reflection Prompts",
            "Printable PDF & Digital Fillable Formats",
        ],
        "etsy_title": title[:140],
        "tags": tags,
        "pricing_strategy": "Launch at $7.99 for initial reviews, then step up to $14.99 standard pricing.",
        "thumbnail_concepts": [
            "Clean lifestyle mockups with iPad",
            "Before/After transformation visual",
            "Feature callout overlay",
        ],
        "bundle_opportunities": [f"Combine with a broader {idea['buyer']} productivity suite."],
        "family_roadmap": [
            "v1.0 Basic Printable",
            "v2.0 Automated Spreadsheet / Interactive Web Version",
            "v3.0 Physical Companion Card Deck",
        ],
    }
