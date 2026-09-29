"""
app.py: CampusPulse — High-Performance University Link Health & 404 Auditor.
Bespoke modern interface with dark command-center aesthetic, real-time analytics, and noise-free crawling.
"""

from dataclasses import asdict
import importlib
from typing import Dict, List
import pandas as pd
import streamlit as st

import crawler
importlib.reload(crawler)
from crawler import BrokenLink, crawl_website

# Page Configuration
st.set_page_config(
    page_title="CampusPulse | University Link Health Auditor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Bespoke Modern Dark-SaaS Design System
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Global Overrides */
    * {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    #MainMenu, header, footer {
        visibility: hidden !important;
        height: 0 !important;
    }
    
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 1200px !important;
    }

    body, [data-testid="stAppViewContainer"] {
        background-color: #0B0F19 !important;
        color: #F1F5F9 !important;
    }

    /* Top Navigation Bar */
    .top-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.85rem 1.5rem;
        background: rgba(17, 24, 39, 0.7);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        margin-bottom: 2rem;
    }
    .brand-group {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .brand-logo {
        width: 32px;
        height: 32px;
        background: linear-gradient(135deg, #6366F1 0%, #A855F7 100%);
        border-radius: 9px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 16px;
        color: #FFFFFF;
        box-shadow: 0 0 16px rgba(99, 102, 241, 0.4);
    }
    .brand-name {
        font-size: 1.15rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #FFFFFF;
    }
    .brand-pill {
        background: rgba(99, 102, 241, 0.15);
        color: #A5B4FC;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 3px 9px;
        border-radius: 999px;
        border: 1px solid rgba(99, 102, 241, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .nav-status {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.82rem;
        color: #94A3B8;
        font-weight: 500;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        background-color: #10B981;
        border-radius: 50%;
        box-shadow: 0 0 8px #10B981;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); opacity: 0.8; }
        50% { transform: scale(1.15); opacity: 1; }
        100% { transform: scale(0.95); opacity: 0.8; }
    }

    /* Hero Section */
    .hero-container {
        text-align: center;
        padding: 1.5rem 1rem 2rem 1rem;
        max-width: 820px;
        margin: 0 auto;
    }
    .hero-headline {
        font-size: 2.75rem;
        font-weight: 800;
        letter-spacing: -0.035em;
        line-height: 1.15;
        background: linear-gradient(180deg, #FFFFFF 0%, #94A3B8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.85rem;
    }
    .hero-sub {
        font-size: 1.05rem;
        color: #94A3B8;
        line-height: 1.6;
        margin-bottom: 1.8rem;
    }

    /* Modern Card Layouts */
    .saas-card {
        background: #111827;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.4rem;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25);
    }

    /* Metric Grid */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin: 1.5rem 0;
    }
    .kpi-box {
        background: rgba(17, 24, 39, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 14px;
        padding: 1.2rem;
        position: relative;
        overflow: hidden;
    }
    .kpi-box::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.6), transparent);
    }
    .kpi-title {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #94A3B8;
        margin-bottom: 0.4rem;
    }
    .kpi-number {
        font-size: 2rem;
        font-weight: 800;
        color: #FFFFFF;
        line-height: 1.1;
    }
    .kpi-number.danger {
        color: #F87171;
        text-shadow: 0 0 12px rgba(239, 68, 68, 0.35);
    }
    .kpi-number.safe {
        color: #34D399;
        text-shadow: 0 0 12px rgba(16, 185, 129, 0.35);
    }
    .kpi-meta {
        font-size: 0.78rem;
        color: #64748B;
        margin-top: 0.35rem;
    }

    /* Live Terminal Console */
    .terminal-box {
        background: #060911;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 0.85rem 1.15rem;
        margin: 1.2rem 0;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.82rem;
        color: #38BDF8;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* Form Controls */
    div[data-testid="stTextInput"] input {
        background-color: #060911 !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
        color: #FFFFFF !important;
        font-size: 1rem !important;
        padding: 0.75rem 1rem !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.25) !important;
    }

    /* Action Buttons */
    div.stButton > button, div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.4) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(79, 70, 229, 0.55) !important;
    }

    /* Quick Preset Chips */
    .chip-btn {
        display: inline-block;
        padding: 4px 12px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 999px;
        color: #94A3B8;
        font-size: 0.78rem;
        margin-right: 6px;
        margin-top: 6px;
        text-decoration: none;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# 1. Top Navbar
st.markdown(
    """
    <div class="top-nav">
        <div class="brand-group">
            <div class="brand-logo">⚡</div>
            <div class="brand-name">CampusPulse</div>
            <div class="brand-pill">Link Health Engine</div>
        </div>
        <div class="nav-status">
            <div class="status-dot"></div>
            <span>Audit Engine Ready · v2.0</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# 2. Hero Section
st.markdown(
    """
    <div class="hero-container">
        <h1 class="hero-headline">Audit Your Campus Web.<br>Catch Broken Links in Minutes.</h1>
        <p class="hero-sub">
            University websites lose track of dead links buried across deep departmental subpages.
            CampusPulse crawls your academic portal at lightning speed, discards bot false-alarms,
            and pinpoints every hidden 404 error to protect student experience.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# 3. Main Search Form & Presets
# Initialize session state for target url if not present
if "input_url" not in st.session_state:
    st.session_state.input_url = "https://www.shsu.edu"

# Quick preset selector pills
chip_col1, chip_col2, chip_col3, chip_col4, chip_space = st.columns([1.5, 1.2, 1.1, 1.1, 3.1])
with chip_col1:
    if st.button("🐾 SHSU (shsu.edu)", use_container_width=True):
        st.session_state.input_url = "https://www.shsu.edu"
with chip_col2:
    if st.button("🏛️ Harvard", use_container_width=True):
        st.session_state.input_url = "https://www.harvard.edu"
with chip_col3:
    if st.button("⚡ MIT", use_container_width=True):
        st.session_state.input_url = "https://www.mit.edu"
with chip_col4:
    if st.button("🎓 ITU", use_container_width=True):
        st.session_state.input_url = "https://www.itu.edu.tr"

with st.form("audit_form", clear_on_submit=False):
    search_col, action_col = st.columns([5, 1.3])
    with search_col:
        target_url = st.text_input(
            "Target University URL",
            value=st.session_state.input_url,
            placeholder="https://www.shsu.edu or https://www.your-university.edu",
            label_visibility="collapsed"
        )
    with action_col:
        submit_btn = st.form_submit_button("⚡ Run Audit", use_container_width=True)

# 4. Collapsible Advanced Tuning Toolbar
with st.expander("🛠️ Audit Engine Tuning & Filters", expanded=False):
    t_col1, t_col2, t_col3 = st.columns(3)
    with t_col1:
        max_pages = st.select_slider(
            "Crawl Depth Budget (Pages)",
            options=[10, 20, 30, 50, 75, 100],
            value=30,
            help="Limits how many pages the spider explores from the base address."
        )
    with t_col2:
        scope_choice = st.radio(
            "Audit Scope",
            options=["All Links (Internal + External)", "Campus Internal Only"],
            index=0,
            horizontal=True
        )
        scope = "internal_only" if scope_choice == "Campus Internal Only" else "all"
    with t_col3:
        ignore_social = st.checkbox(
            "Smart Anti-Bot Filter",
            value=True,
            help="Suppresses false 403/429 alerts from Facebook, Instagram, LinkedIn, and YouTube."
        )
        allow_subdomains = st.checkbox(
            "Include Academic Subdomains (*.edu)",
            value=True,
            help="Explores department subdomains like cs.univ.edu or grad.univ.edu."
        )

# 5. Execution & Real-Time Analytics
if submit_btn:
    if not target_url or not target_url.strip().startswith(("http://", "https://")):
        st.error("Please provide a valid website address starting with 'http://' or 'https://'.")
    else:
        clean_url = target_url.strip()

        # Dynamic KPI Containers
        kpi_placeholder = st.empty()
        progress_placeholder = st.empty()
        console_placeholder = st.empty()

        broken_dict: Dict[str, BrokenLink] = {}
        total_scanned = 0
        total_checked = 0

        # Start Crawler Generator
        crawler_gen = crawl_website(
            start_url=clean_url,
            max_pages=max_pages,
            timeout=5,
            allow_subdomains=allow_subdomains,
            ignore_social=ignore_social,
            scope=scope
        )

        for event in crawler_gen:
            event_type = event.get("type")

            if event_type == "ERROR":
                st.error(event.get("message"))
                break

            elif event_type == "PAGE_START":
                total_scanned = event["pages_scanned"]
                total_checked = event.get("checked_count", 0)
                broken_count = event["broken_count"]
                queue_size = event["queue_size"]

                health_score = round((1 - broken_count / max(total_checked, 1)) * 100, 1)

                # Executive KPI Cards
                kpi_placeholder.markdown(
                    f"""
                    <div class="kpi-grid">
                        <div class="kpi-box">
                            <div class="kpi-title">Pages Explored</div>
                            <div class="kpi-number">{total_scanned} <span style="font-size:1.1rem;color:#64748B;">/ {max_pages}</span></div>
                            <div class="kpi-meta">Queue: {queue_size} pending pages</div>
                        </div>
                        <div class="kpi-box">
                            <div class="kpi-title">Links Audited</div>
                            <div class="kpi-number">{total_checked}</div>
                            <div class="kpi-meta">Unique URL validations</div>
                        </div>
                        <div class="kpi-box">
                            <div class="kpi-title">Broken Discovered</div>
                            <div class="kpi-number {'danger' if broken_count > 0 else 'safe'}">{broken_count}</div>
                            <div class="kpi-meta">Confirmed 404 / 5xx failures</div>
                        </div>
                        <div class="kpi-box">
                            <div class="kpi-title">Health Score</div>
                            <div class="kpi-number {'safe' if health_score >= 95 else 'danger'}">{health_score}%</div>
                            <div class="kpi-meta">Institutional link index</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Modern Progress & Live Terminal Feed
                progress_ratio = min(total_scanned / max_pages, 1.0)
                progress_placeholder.progress(progress_ratio)
                console_placeholder.markdown(
                    f"""
                    <div class="terminal-box">
                        <span style="color:#10B981;font-weight:700;">● PROBING</span>
                        <span style="color:#64748B;">|</span>
                        <span style="color:#F8FAFC;">{event['current_page']}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            elif event_type == "BROKEN_LINK":
                broken_obj: BrokenLink = event["broken"]
                broken_dict[broken_obj.target_url] = broken_obj

            elif event_type == "COMPLETED":
                total_scanned = event["total_scanned_pages"]
                total_checked = event["total_checked_links"]
                broken_count = event["total_broken_links"]
                health_score = round((1 - broken_count / max(total_checked, 1)) * 100, 1)

                progress_placeholder.progress(1.0)
                console_placeholder.markdown(
                    f"""
                    <div class="terminal-box" style="border-color:#059669; background:rgba(6,78,59,0.25); color:#34D399;">
                        ✓ AUDIT COMPLETE — Evaluated {total_scanned} pages and {total_checked} unique links across the target domain.
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # 6. Audit Report & Tabbed Analysis
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📋 Audit Intelligence Report")

        if not broken_dict:
            st.success("🌟 Flawless Audit: Zero broken links or 404 errors detected across all explored pages. Site health is 100%!")
        else:
            records = []
            for b in broken_dict.values():
                records.append({
                    "Broken URL": b.target_url,
                    "Status": b.error_reason,
                    "HTTP Code": b.status_code if b.status_code else "-",
                    "Link Type": "Internal" if b.is_internal else "External",
                    "Anchor Text": b.link_text,
                    "Host Page": b.first_found_on,
                    "Occurrences": b.total_occurrences,
                    "raw_status": b.status_code
                })

            df = pd.DataFrame(records)

            tab_all, tab_404, tab_server = st.tabs([
                f"All Issues ({len(df)})",
                f"404 Not Found ({len(df[df['raw_status'] == 404])})",
                f"Server & Network Failures ({len(df[df['raw_status'] != 404])})"
            ])

            def render_styled_table(data_subset: pd.DataFrame):
                if data_subset.empty:
                    st.info("No broken links found in this specific category.")
                    return

                cols = ["Broken URL", "Status", "HTTP Code", "Link Type", "Anchor Text", "Host Page", "Occurrences"]
                st.dataframe(
                    data_subset[cols],
                    use_container_width=True,
                    column_config={
                        "Broken URL": st.column_config.LinkColumn("Broken Target URL"),
                        "Host Page": st.column_config.LinkColumn("Discovered On (Source)"),
                        "Occurrences": st.column_config.NumberColumn("Occurrences", format="%d"),
                        "HTTP Code": st.column_config.TextColumn("Code"),
                        "Status": st.column_config.TextColumn("Failure Reason")
                    },
                    hide_index=True
                )

            with tab_all:
                render_styled_table(df)
            with tab_404:
                render_styled_table(df[df["raw_status"] == 404])
            with tab_server:
                render_styled_table(df[df["raw_status"] != 404])

            # Export Bar
            export_cols = ["Broken URL", "Status", "HTTP Code", "Link Type", "Anchor Text", "Host Page", "Occurrences"]
            csv_export = df[export_cols].to_csv(index=False).encode("utf-8-sig")

            down_col1, down_col2 = st.columns([4, 1.5])
            with down_col2:
                st.download_button(
                    label="📥 Export Audit CSV (Excel-Ready)",
                    data=csv_export,
                    file_name="campuspulse_link_health_report.csv",
                    mime="text/csv",
                    use_container_width=True
                )
