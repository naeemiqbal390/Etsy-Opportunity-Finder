"""
app.py — Main Streamlit user interface for Etsy Opportunity Radar.
Runs entirely locally: no API keys, no paid services, no network calls
except the "Search Etsy/Google/..." buttons, which just open a browser tab.
"""

import streamlit as st
import pandas as pd

from engine import generate_base_idea, make_it_weirder, generate_why_it_fails, commercialize_idea
from research import (
    build_research_links,
    calculate_demand_score,
    calculate_competition_score,
    calculate_opportunity_score,
    calculate_evidence_confidence,
)
from db import init_db, save_opportunity, load_opportunities

st.set_page_config(page_title="Etsy Opportunity Radar", page_icon="🎯", layout="wide")

init_db()

if "idea" not in st.session_state:
    st.session_state.idea = generate_base_idea()

idea = st.session_state.idea

st.title("🎯 Etsy Opportunity Radar")
st.caption("Discover unusual human observations and validate commercial opportunities.")

# ----------------------------
# Sidebar Controls
# ----------------------------
with st.sidebar:
    st.header("Discovery Controls")
    if st.button("✨ Generate Base Idea", use_container_width=True):
        st.session_state.idea = generate_base_idea()
        st.rerun()

    if st.button("🌀 Make It Weirder", use_container_width=True):
        st.session_state.idea = make_it_weirder(st.session_state.idea)
        st.rerun()

# ----------------------------
# Main Header Display
# ----------------------------
st.subheader("Current Concept")
st.markdown(f"## {idea['product']}")
st.write(f"**Core Insight:** {idea['problem_desc'].capitalize()}.")
st.write(f"**Target Buyer:** {idea['buyer']} — {idea['buyer_desc']}.")
st.write(f"**Hook:** \u201c{idea['hook']}\u201d")

# ----------------------------
# Keyword Search Links Workflow
# ----------------------------
st.markdown("### 1. Clickable Research Workflow")
primary_kw = idea["keywords"][0]
links = build_research_links(primary_kw)

cols = st.columns(len(links))
for idx, (platform, url) in enumerate(links.items()):
    cols[idx].link_button(f"Search {platform}", url, use_container_width=True)

st.divider()

# ----------------------------
# Evidence Recording Form
# ----------------------------
st.markdown("### 2. Evidence Recording & Metrics")
st.caption("Enter numbers you actually observed (e.g. from Etsy Marketplace Insights). Nothing here is fetched automatically.")

c1, c2 = st.columns(2)

with c1:
    st.markdown("#### Etsy Marketplace Evidence")
    searches = st.number_input("Etsy Search Volume (30 Days)", min_value=0, value=0, step=50)
    listings = st.number_input("Competing Etsy Listings", min_value=0, value=0, step=10)
    top_price = st.number_input("Top Listing Price ($)", min_value=0.0, value=0.0, step=1.0)
    avg_reviews = st.number_input("Avg Review Count (Top 5)", min_value=0, value=0, step=10)

with c2:
    st.markdown("#### Outside Etsy Signal")
    trend = st.slider("Google Trends relative strength", 0, 100, 50)
    reddit_vol = st.number_input("Reddit mentions / discussions", min_value=0, value=0)
    pinterest_vol = st.number_input("Pinterest pin density", min_value=0, value=0)

pain = st.slider("Pain / Urgency Severity", 0, 100, 70)
diff = st.slider("Differentiation Potential", 0, 100, 80)

# ----------------------------
# Scores Calculation
# ----------------------------
d_score = calculate_demand_score(searches, trend)
c_score = calculate_competition_score(listings, top_price, avg_reviews)
opp_score = calculate_opportunity_score(d_score, c_score, pain, diff)

evidence_inputs = {
    "searches": searches,
    "listings": listings,
    "top_price": top_price,
    "avg_reviews": avg_reviews,
    "trend": trend,
    "reddit_volume": reddit_vol,
    "pinterest_interest": pinterest_vol,
}
confidence = calculate_evidence_confidence(evidence_inputs)

st.divider()

# ----------------------------
# Decision Dashboard
# ----------------------------
m1, m2, m3, m4 = st.columns(4)
m1.metric("Demand Score", "N/A" if d_score is None else f"{d_score}/100")
m2.metric("Competition Score", "N/A" if c_score is None else f"{c_score}/100")
m3.metric("Opportunity Score", "N/A" if opp_score is None else f"{opp_score}/100")
m4.metric("Evidence Confidence", f"{confidence}%")

st.divider()

# ----------------------------
# Red Teaming: Why Might This Fail?
# ----------------------------
st.markdown("### 3. Red Teaming: Why Might This Fail?")
risks = generate_why_it_fails(idea)
for r in risks:
    st.warning(f"**{r['type']}:** {r['text']}")

st.divider()

# ----------------------------
# Commercialization Workflow
# ----------------------------
st.markdown("### 4. Commercialization Pipeline")
if st.button("💼 Commercialize Idea", type="primary"):
    comm = commercialize_idea(idea)
    st.success("Commercialization Blueprint Generated!")

    st.markdown("**Etsy Title:**")
    st.code(comm["etsy_title"])

    st.markdown("**Suggested Tags:**")
    st.code(", ".join(comm["tags"]))

    st.markdown(f"**Product Specification:** {comm['product_spec']}")
    st.markdown(f"**Pricing Strategy:** {comm['pricing_strategy']}")

    st.markdown("**Key Features / Pages:**")
    for feat in comm["pages_features"]:
        st.write(f"- {feat}")

    st.markdown("**Thumbnail Concepts:**")
    for tc in comm["thumbnail_concepts"]:
        st.write(f"- {tc}")

    st.markdown("**Bundle Opportunities:**")
    for b in comm["bundle_opportunities"]:
        st.write(f"- {b}")

    st.markdown("**Product Family Roadmap:**")
    for step in comm["family_roadmap"]:
        st.write(f"- {step}")

st.divider()

# ----------------------------
# Save & Persistence
# ----------------------------
if st.button("💾 Save to Opportunity Database"):
    record = {
        "idea": idea,
        "evidence": evidence_inputs,
        "scores": {
            "demand": d_score,
            "competition": c_score,
            "opportunity": opp_score,
            "confidence": confidence,
        },
    }
    save_opportunity(record)
    st.toast("Opportunity saved to SQLite database!")

# ----------------------------
# Saved Opportunities View
# ----------------------------
st.subheader("📚 Saved Opportunity Database")
saved_data = load_opportunities()
if saved_data:
    flat_data = []
    for s in saved_data:
        flat_data.append(
            {
                "Product": s["idea"]["product"],
                "Opportunity Score": s["scores"]["opportunity"],
                "Confidence": f"{s['scores']['confidence']}%",
                "Searches": s["evidence"]["searches"],
                "Listings": s["evidence"]["listings"],
            }
        )
    df = pd.DataFrame(flat_data)
    st.dataframe(df, use_container_width=True)

    st.download_button(
        "⬇️ Export saved opportunities CSV",
        df.to_csv(index=False),
        "etsy_opportunities.csv",
        "text/csv",
    )
else:
    st.info("No saved opportunities yet.")
