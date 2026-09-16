"""
app.py — Etsy Opportunity Finder.

Fully automated monthly scan: generates candidate digital-product search
phrases itself, best-effort expands them via Google Trends, classifies
buyer intent, ranks a Top N shortlist, and flags possible "hidden gem"
low-competition candidates for you to manually verify. No manual keyword
entry required. No API keys required (Google Trends via pytrends is free
and keyless, but best-effort — see trends.py for why).
"""

import streamlit as st
import pandas as pd

from discovery import run_monthly_scan
from research import (
    build_research_links,
    calculate_competition_score,
    calculate_opportunity_score,
)
from db import init_db, save_radar_entries, load_radar_entries, list_radar_months

st.set_page_config(page_title="Etsy Opportunity Finder", page_icon="🎯", layout="wide")

init_db()

st.title("🎯 Etsy Opportunity Finder")
st.caption(
    "Automatically generates and ranks digital-product opportunity candidates for this "
    "month — no manual keyword entry. Excludes books, Notion templates, and Canva templates."
)

with st.sidebar:
    st.header("Scan Settings")
    seed_limit = st.slider("Seed candidates to generate", 50, 900, 300, step=50)
    expand = st.checkbox(
        "Try Google Trends expansion + scoring (best-effort, may be blocked on this host)",
        value=True,
    )
    max_seeds_to_expand = st.slider(
        "Max Google Trends lookups this run", 5, 40, 15,
        help="Each lookup is a real network call to Google Trends — kept low to reduce the chance of getting rate-limited.",
    )
    top_n = st.slider("Shortlist size", 20, 100, 100, step=10)

    run_clicked = st.button("🚀 Run This Month's Scan", type="primary", use_container_width=True)

if run_clicked:
    with st.spinner("Generating and scoring candidates..."):
        st.session_state.scan_result = run_monthly_scan(
            seed_limit=seed_limit,
            expand=expand,
            max_seeds_to_expand=max_seeds_to_expand,
            top_n=top_n,
        )

result = st.session_state.get("scan_result")

if not result:
    st.info("Set your scan settings in the sidebar and click **Run This Month's Scan** to generate this month's shortlist.")
    st.stop()

# ----------------------------
# Scan summary
# ----------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Candidates generated", result["total_candidates_generated"])
c2.metric("After expansion + filtering", result["total_after_expansion_and_filtering"])
c3.metric("Trend lookups fetched", result["trend_scores_fetched"])
c4.metric("Month", result["month_tag"])

if result["trend_scores_fetched"] == 0:
    st.warning(
        "Google Trends returned no data this run (likely rate-limited/blocked from this host). "
        "The shortlist below is still fully ranked, but purely on buyer-intent classification, "
        "not real search-volume trend data. This is normal on shared cloud hosting and not a bug."
    )

st.divider()

# ----------------------------
# Shortlist
# ----------------------------
st.subheader(f"📋 Top {len(result['shortlist'])} Opportunity Candidates — {result['month_tag']}")

shortlist = result["shortlist"]
table_df = pd.DataFrame(
    [
        {
            "Rank": i + 1,
            "Query": e["query"],
            "Intent": f"{e['intent_emoji']} {e['intent_label']}",
            "Product Type": e["product_type"],
            "Trend": "N/A" if e["trend_score"] is None else e["trend_score"],
            "Score": e["score"],
            "Hidden Gem?": "🔎 Check competition" if e["hidden_gem"] else "",
        }
        for i, e in enumerate(shortlist)
    ]
)
st.dataframe(table_df, use_container_width=True, height=420)

st.caption(
    "Score reflects buyer-intent classification plus trend data where available. "
    "Competition is not automated — expand a candidate below to pull research links "
    "and optionally enter real Etsy numbers you find, for a refined opportunity score."
)

st.divider()

# ----------------------------
# Manual competition refinement for shortlisted candidates
# ----------------------------
st.subheader("🔬 Verify a Candidate")
st.caption("Pick a candidate to research. This is the one manual step left — there's no free, reliable source for real Etsy competition data.")

query_options = [e["query"] for e in shortlist]
selected_query = st.selectbox("Candidate", query_options)
selected_entry = next(e for e in shortlist if e["query"] == selected_query)

links = build_research_links(selected_query)
link_cols = st.columns(len(links))
for idx, (platform, url) in enumerate(links.items()):
    link_cols[idx].link_button(f"Search {platform}", url, use_container_width=True)

rc1, rc2, rc3 = st.columns(3)
with rc1:
    etsy_listings = st.number_input("Competing Etsy listings you counted", min_value=0, value=0, step=10)
with rc2:
    etsy_top_price = st.number_input("Top listing price ($)", min_value=0.0, value=0.0, step=1.0)
with rc3:
    etsy_avg_reviews = st.number_input("Avg review count (top 5)", min_value=0, value=0, step=10)

if etsy_listings > 0:
    comp_score = calculate_competition_score(etsy_listings, etsy_top_price, etsy_avg_reviews)
    demand_proxy = selected_entry["trend_score"] if selected_entry["trend_score"] is not None else selected_entry["score"]
    refined_score = calculate_opportunity_score(
        demand=demand_proxy,
        competition=comp_score,
        pain=70,
        diff=70,
    )
    m1, m2 = st.columns(2)
    m1.metric("Competition score (higher = more room)", f"{comp_score}/100")
    m2.metric("Refined opportunity score", f"{refined_score}/100")

st.divider()

# ----------------------------
# Save & archive
# ----------------------------
if st.button("💾 Save this month's shortlist to the archive"):
    save_radar_entries(shortlist)
    st.toast(f"Saved {len(shortlist)} entries to the {result['month_tag']} archive.")

st.subheader("📚 Monthly Archive")
months = list_radar_months()
if months:
    selected_month = st.selectbox("Month", ["All"] + months, key="archive_month")
    entries = load_radar_entries(None if selected_month == "All" else selected_month)
    archive_df = pd.DataFrame(
        [
            {
                "Month": e["month_tag"],
                "Query": e["query"],
                "Intent": f"{e['intent_emoji']} {e['intent_label']}",
                "Product Type": e["product_type"],
                "Score": e["score"],
                "Hidden Gem?": "🔎" if e.get("hidden_gem") else "",
            }
            for e in entries
        ]
    )
    st.dataframe(archive_df, use_container_width=True)
    st.download_button(
        "⬇️ Export archive CSV",
        archive_df.to_csv(index=False),
        f"opportunity_finder_{selected_month}.csv",
        "text/csv",
    )
else:
    st.info("No saved shortlists yet — run a scan and save it above to start your monthly archive.")
