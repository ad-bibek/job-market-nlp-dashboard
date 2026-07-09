"""Injected CSS for the Job Market Intelligence Dashboard — "market terminal" theme."""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

:root {
    --ink: #0B1220;
    --panel: #121B2E;
    --panel-border: #223049;
    --amber: #E8A33D;
    --signal: #4FD1A5;
    --slate: #8A93A6;
    --paper: #EDEFF3;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ---- App background ---- */
.stApp {
    background: linear-gradient(180deg, #0B1220 0%, #0D1526 100%);
}

/* ---- Headings use the display face ---- */
h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    letter-spacing: -0.01em;
}

h1 {
    color: var(--paper) !important;
    font-weight: 700 !important;
}

/* ---- Title row ---- */
.market-title {
    display: flex;
    align-items: baseline;
    gap: 0.6rem;
    margin-bottom: 0.1rem;
}
.market-title .dot {
    width: 10px; height: 10px; border-radius: 50%;
    background: var(--signal);
    display: inline-block;
    box-shadow: 0 0 8px var(--signal);
}
.market-eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    color: var(--slate);
    font-size: 0.75rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
}

/* ---- Ticker strip: the signature element ---- */
.ticker-strip {
    font-family: 'IBM Plex Mono', monospace;
    background: var(--panel);
    border: 1px solid var(--panel-border);
    border-left: 3px solid var(--amber);
    border-radius: 4px;
    padding: 0.65rem 1rem;
    margin: 0.75rem 0 1.5rem 0;
    color: var(--amber);
    font-size: 0.85rem;
    letter-spacing: 0.02em;
    overflow-x: auto;
    white-space: nowrap;
}
.ticker-strip .sep { color: var(--panel-border); margin: 0 0.6rem; }
.ticker-strip .label { color: var(--slate); }
.ticker-strip .val { color: var(--paper); font-weight: 600; }

/* ---- Tabs styled as a ticker board ---- */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    border-bottom: 1px solid var(--panel-border);
}
.stTabs [data-baseweb="tab"] {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: var(--slate);
    background: transparent;
    border-radius: 4px 4px 0 0;
    padding: 0.6rem 1rem;
}
.stTabs [aria-selected="true"] {
    color: var(--amber) !important;
    border-bottom: 2px solid var(--amber) !important;
}

/* ---- Metrics ---- */
[data-testid="stMetric"] {
    background: var(--panel);
    border: 1px solid var(--panel-border);
    border-left: 3px solid var(--amber);
    border-radius: 4px;
    padding: 0.8rem 1rem 0.6rem 1rem;
}
[data-testid="stMetricLabel"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--slate) !important;
}
[data-testid="stMetricValue"] {
    font-family: 'IBM Plex Mono', monospace !important;
    color: var(--paper) !important;
}

/* ---- Sidebar as a terminal panel ---- */
[data-testid="stSidebar"] {
    background: var(--panel);
    border-right: 1px solid var(--panel-border);
}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: var(--slate) !important;
}

/* ---- Captions ---- */
[data-testid="stCaptionContainer"], .stCaption {
    font-family: 'IBM Plex Mono', monospace !important;
    color: var(--slate) !important;
    font-size: 0.78rem !important;
}

/* ---- Dataframes ---- */
[data-testid="stDataFrame"] {
    border: 1px solid var(--panel-border);
    border-radius: 4px;
    overflow: hidden;
}

/* ---- Section divider rule ---- */
.section-rule {
    border: none;
    border-top: 1px solid var(--panel-border);
    margin: 1.4rem 0;
}
</style>
"""


def ticker_html(stats: list) -> str:
    """stats: list of (label, value) tuples rendered as a market-ticker strip."""
    parts = []
    for i, (label, value) in enumerate(stats):
        if i > 0:
            parts.append('<span class="sep">/</span>')
        parts.append(f'<span class="label">{label}</span> <span class="val">{value}</span>')
    return f'<div class="ticker-strip">{"".join(parts)}</div>'
