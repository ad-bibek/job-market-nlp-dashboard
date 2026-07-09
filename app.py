"""
Job Market Intelligence Dashboard — NLP Enhancement
Implements US-01 through US-06 from the project backlog (see docs/BRD.docx).
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import streamlit as st
import pandas as pd
import plotly.express as px

from validation import validate
from skills import extract_skills, skill_frequency_by_category, top_skills_for_category
from topics import fit_topics
from similarity import SimilarityIndex
from theme import CSS, ticker_html

st.set_page_config(page_title="Job Market Intelligence Dashboard", layout="wide", page_icon="📡")
st.markdown(CSS, unsafe_allow_html=True)

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "postings.csv")

PLOTLY_LAYOUT = dict(
    paper_bgcolor="#121B2E", plot_bgcolor="#121B2E",
    font=dict(family="Inter, sans-serif", color="#EDEFF3", size=13),
    title_font=dict(family="Space Grotesk, sans-serif", size=16, color="#EDEFF3"),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
    margin=dict(t=50, l=10, r=10, b=10),
)
COLOR_SEQUENCE = ["#E8A33D", "#4FD1A5", "#7C93C9", "#D97757", "#8A93A6", "#B5CDA3"]


def style_fig(fig):
    fig.update_layout(**PLOTLY_LAYOUT)
    fig.update_xaxes(gridcolor="#223049", zerolinecolor="#223049")
    fig.update_yaxes(gridcolor="#223049", zerolinecolor="#223049")
    return fig


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    clean_df, validation_log = validate(df)
    return df, clean_df, validation_log


@st.cache_data
def compute_skills(clean_df):
    clean_df = clean_df.copy()
    clean_df["skills_found"] = clean_df["description"].apply(extract_skills)
    clean_df["skills_text"] = clean_df["skills_found"].apply(lambda s: " ".join(s))
    freq_df = skill_frequency_by_category(clean_df)
    return clean_df, freq_df


@st.cache_data
def compute_topics(clean_df_with_skills, n_topics):
    topics_df, labels = fit_topics(clean_df_with_skills, n_topics=n_topics, text_col="skills_text")
    return topics_df, labels


@st.cache_resource
def build_similarity_index(clean_df_with_skills):
    return SimilarityIndex(clean_df_with_skills)


# ---------- Load & prep ----------
raw_df, clean_df, validation_log = load_data()
clean_df, freq_df = compute_skills(clean_df)

st.markdown('<div class="market-eyebrow">Real-Time Signal &middot; Global DS/AI Roles</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="market-title"><span class="dot"></span>'
    '<h1 style="margin:0;">Job Market Intelligence</h1></div>',
    unsafe_allow_html=True,
)
st.markdown(
    ticker_html([
        ("POSTINGS", len(clean_df)),
        ("CATEGORIES", clean_df["category"].nunique()),
        ("COMPANIES", clean_df["company"].nunique()),
        ("FLAGGED", len(validation_log)),
        ("TOP SKILL", freq_df.groupby("skill")["count"].sum().idxmax() if len(freq_df) else "—"),
    ]),
    unsafe_allow_html=True,
)

# ---------- Sidebar filters (US-05) ----------
st.sidebar.header("Filters")
categories = sorted(clean_df["category"].unique())
selected_categories = st.sidebar.multiselect("Role category", categories, default=categories)

locations = sorted(clean_df["location"].unique())
selected_locations = st.sidebar.multiselect("Location", locations, default=locations)

min_date = pd.to_datetime(clean_df["posted_date"]).min()
max_date = pd.to_datetime(clean_df["posted_date"]).max()
date_range = st.sidebar.date_input("Posted date range", value=(min_date, max_date),
                                    min_value=min_date, max_value=max_date)

filtered = clean_df[
    clean_df["category"].isin(selected_categories) & clean_df["location"].isin(selected_locations)
]
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered = filtered[
        (pd.to_datetime(filtered["posted_date"]) >= start) & (pd.to_datetime(filtered["posted_date"]) <= end)
    ]

st.sidebar.metric("Postings matching filters", len(filtered))
st.sidebar.metric("Records flagged & excluded", len(validation_log))

tab_overview, tab_skills, tab_topics, tab_similar, tab_search, tab_quality = st.tabs(
    ["Overview", "Skill Demand", "Topic Clusters", "Similar Postings", "Search", "Data Quality"]
)

# ---------- Overview (US-05) ----------
with tab_overview:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total postings (filtered)", len(filtered))
    col2.metric("Companies", filtered["company"].nunique())
    col3.metric("Locations", filtered["location"].nunique())

    c1, c2 = st.columns(2)
    with c1:
        cat_counts = filtered["category"].value_counts().reset_index()
        cat_counts.columns = ["category", "postings"]
        fig = px.bar(cat_counts, x="category", y="postings", title="Postings by Role Category",
                     color_discrete_sequence=[COLOR_SEQUENCE[0]])
        st.plotly_chart(style_fig(fig), use_container_width=True)
    with c2:
        loc_counts = filtered["location"].value_counts().reset_index()
        loc_counts.columns = ["location", "postings"]
        fig = px.pie(loc_counts, names="location", values="postings", title="Postings by Location",
                     color_discrete_sequence=COLOR_SEQUENCE, hole=0.45)
        st.plotly_chart(style_fig(fig), use_container_width=True)

    trend = filtered.copy()
    trend["posted_date"] = pd.to_datetime(trend["posted_date"])
    trend_counts = trend.groupby([pd.Grouper(key="posted_date", freq="W"), "category"]).size().reset_index(name="postings")
    fig = px.line(trend_counts, x="posted_date", y="postings", color="category", title="Posting Volume Over Time",
                  color_discrete_sequence=COLOR_SEQUENCE)
    st.plotly_chart(style_fig(fig), use_container_width=True)

# ---------- Skill Demand (US-02) ----------
with tab_skills:
    st.subheader("Top skills by role category")
    st.caption("FS-1: skill frequency extracted via spaCy PhraseMatcher against a curated skills vocabulary.")
    sel_cat = st.selectbox("Choose a role category", categories)
    top_n = st.slider("Number of skills to show", 5, 20, 10)
    top_skills = top_skills_for_category(freq_df, sel_cat, top_n)
    if len(top_skills):
        fig = px.bar(top_skills.sort_values("count"), x="count", y="skill", orientation="h",
                     title=f"Top {top_n} skills — {sel_cat}",
                     color_discrete_sequence=[COLOR_SEQUENCE[1]])
        st.plotly_chart(style_fig(fig), use_container_width=True)
    else:
        st.info("No skill data for this category yet.")

# ---------- Topic Clusters (US-03) ----------
with tab_topics:
    st.subheader("Thematic topic clusters")
    st.caption(
        "FS-2: postings clustered on extracted-skill profiles using TF-IDF + KMeans with "
        "c-TF-IDF-style labeling (BERTopic-equivalent pipeline; sentence-transformer backbone "
        "swapped for a transformer-free implementation — see src/topics.py docstring)."
    )
    n_topics = st.slider("Number of topic clusters", 3, 10, 6)
    topics_df, topic_labels = compute_topics(clean_df, n_topics)

    label_df = pd.DataFrame([{"topic_id": k, "label": v} for k, v in topic_labels.items()])
    counts = topics_df["topic_id"].value_counts().reset_index()
    counts.columns = ["topic_id", "postings"]
    merged = label_df.merge(counts, on="topic_id").sort_values("postings", ascending=False)

    fig = px.bar(merged, x="postings", y="label", orientation="h", title="Topic Clusters by Size",
                 color_discrete_sequence=[COLOR_SEQUENCE[2]])
    st.plotly_chart(style_fig(fig), use_container_width=True)

    sel_topic_label = st.selectbox("Inspect a cluster", merged["label"])
    sel_topic_id = merged.loc[merged["label"] == sel_topic_label, "topic_id"].iloc[0]
    cluster_postings = topics_df[topics_df["topic_id"] == sel_topic_id][
        ["posting_id", "title", "company", "category", "location"]
    ]
    st.dataframe(cluster_postings, use_container_width=True, hide_index=True)

# ---------- Similar Postings (US-04) ----------
with tab_similar:
    st.subheader("Find similar postings")
    st.caption(
        "FS-3: semantic similarity via TF-IDF + Truncated SVD (LSA) embeddings and cosine similarity "
        "— a transformer-free stand-in for sentence-transformer embeddings."
    )
    sim_index = build_similarity_index(clean_df)

    options = clean_df.apply(lambda r: f"{r['posting_id']} — {r['title']} @ {r['company']}", axis=1)
    choice = st.selectbox("Pick a posting", options)
    chosen_id = int(choice.split(" — ")[0])

    top_n_sim = st.slider("How many similar postings?", 3, 10, 5)
    results = sim_index.similar_to(chosen_id, top_n=top_n_sim)

    st.write(f"**Postings most similar to #{chosen_id}:**")
    if len(results):
        st.dataframe(
            results[["posting_id", "title", "company", "category", "location", "similarity"]]
            .style.format({"similarity": "{:.2f}"}),
            use_container_width=True, hide_index=True,
        )
    else:
        st.info("No similar postings found.")

# ---------- Search (US-01) ----------
with tab_search:
    st.subheader("Search postings")
    st.caption("US-01: keyword search across title and description.")
    query = st.text_input("Search by keyword (title or description)")
    if query:
        mask = filtered["title"].str.contains(query, case=False, na=False) | \
               filtered["description"].str.contains(query, case=False, na=False)
        results = filtered[mask]
    else:
        results = filtered
    st.write(f"{len(results)} matching postings")
    st.dataframe(
        results[["posting_id", "title", "company", "category", "location", "seniority", "posted_date"]],
        use_container_width=True, hide_index=True,
    )

# ---------- Data Quality (US-06) ----------
with tab_quality:
    st.subheader("Data quality & validation log")
    st.caption("FS-4: records missing title, description, or posted_date are excluded from analysis and logged here.")
    c1, c2 = st.columns(2)
    c1.metric("Total ingested records", len(raw_df))
    c2.metric("Excluded (failed validation)", len(validation_log))
    if len(validation_log):
        st.dataframe(validation_log, use_container_width=True, hide_index=True)
    else:
        st.success("No validation issues found.")
