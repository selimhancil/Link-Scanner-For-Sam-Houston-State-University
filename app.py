"""
app.py: Modern, professional web interface for auditing university broken links.
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
    page_title="EduLink Inspector | University Broken Link Auditor",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional & Modern CSS Styling
CUSTOM_CSS = """
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    /* Header & Brand Container */
    .app-header {
        padding: 0.5rem 0 1.5rem 0;
        border-bottom: 1px solid rgba(226, 232, 240, 0.8);
        margin-bottom: 1.5rem;
    }
    .brand-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #EEF2FF;
        color: #4F46E5;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 4px 10px;
        border-radius: 9999px;
        border: 1px solid #E0E7FF;
        margin-bottom: 0.6rem;
    }
    .app-title {
        font-size: 1.85rem;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.02em;
        margin: 0 0 0.4rem 0;
        line-height: 1.2;
    }
    .app-subtitle {
        font-size: 0.95rem;
        color: #64748B;
        margin: 0;
        line-height: 1.5;
    }

    /* Metric Grid & Cards */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin: 1.2rem 0;
    }
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1.1rem 1.25rem;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .metric-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
    }
    .metric-label {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #64748B;
        margin-bottom: 0.35rem;
    }
    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #0F172A;
        line-height: 1.1;
    }
    .metric-value.error {
        color: #DC2626;
    }
    .metric-value.success {
        color: #16A34A;
    }
    .metric-sub {
        font-size: 0.78rem;
        color: #94A3B8;
        margin-top: 0.35rem;
    }

    /* Live Status Console */
    .status-panel {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 0.85rem 1rem;
        margin: 1rem 0;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem;
        color: #334155;
    }

    /* Buttons */
    div.stButton > button:first-child {
        font-weight: 600;
        letter-spacing: 0.01em;
        border-radius: 8px;
        transition: all 0.2s ease;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Main Brand Header
st.markdown(
    """
    <div class="app-header">
        <div class="brand-badge">EduLink Inspector · Web Health</div>
        <h1 class="app-title">University Broken Link Auditor</h1>
        <p class="app-subtitle">
            Crawl and audit university web portals to identify 404 (Not Found) errors, unreachable resources,
            and broken links. Social media platforms and bot-protected third-party services are automatically filtered.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Sidebar (Audit Settings)
with st.sidebar:
    st.markdown("### ⚙️ Audit Parameters")
    
    st.markdown("##### Filtering & Scope")
    ignore_social = st.checkbox(
        "Exclude social media platforms",
        value=True,
        help="Filters out Facebook, Instagram, LinkedIn, X, and YouTube links that block bots and return false-positive errors."
    )
    
    scope_option = st.selectbox(
        "Link Audit Scope",
        options=["All Links (Internal + External)", "Internal University Links Only"],
        index=0,
        help="Selecting 'Internal University Links Only' skips validating links pointing to external third-party domains."
    )
    scope = "internal_only" if scope_option == "Internal University Links Only" else "all"

    allow_subdomains = st.checkbox(
        "Include faculty subdomains",
        value=True,
        help="Considers addresses like 'cs.univ.edu' or 'grad.univ.edu' as internal links belonging to the root domain."
    )

    st.markdown("---")
    st.markdown("##### Crawl Limits")
    max_pages = st.slider(
        "Max Pages to Crawl",
        min_value=5,
        max_value=100,
        value=30,
        step=5,
        help="Limits the total number of crawled pages to conserve server bandwidth and runtime."
    )
    timeout = st.slider(
        "Request Timeout (Seconds)",
        min_value=2,
        max_value=15,
        value=5,
        help="Maximum wait time for each URL validation response."
    )

    st.markdown("---")
    st.caption("EduLink Inspector v1.2 · Antigravity Suite")

# URL Search Form
with st.form("scan_form", clear_on_submit=False):
    input_col, button_col = st.columns([5, 1])
    with input_col:
        target_url = st.text_input(
            "Target University Website URL",
            placeholder="https://www.shsu.edu or https://www.harvard.edu",
            label_visibility="collapsed"
        )
    with button_col:
        submit_btn = st.form_submit_button("Start Audit", type="primary", use_container_width=True)

st.caption("Examples: `https://www.shsu.edu` · `https://www.harvard.edu` · `https://www.mit.edu`")

# Execution Logic
if submit_btn:
    if not target_url or not target_url.strip().startswith(("http://", "https://")):
        st.error("Please enter a valid website address starting with 'http://' or 'https://'.")
    else:
        clean_url = target_url.strip()

        # Placeholders for live metrics and status
        metrics_placeholder = st.empty()
        progress_placeholder = st.empty()
        status_placeholder = st.empty()

        broken_dict: Dict[str, BrokenLink] = {}
        total_scanned = 0
        total_checked = 0

        # Execute crawler generator
        crawler_gen = crawl_website(
            start_url=clean_url,
            max_pages=max_pages,
            timeout=timeout,
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

                # Modern KPI Cards
                metrics_placeholder.markdown(
                    f"""
                    <div class="metric-grid">
                        <div class="metric-card">
                            <div class="metric-label">Pages Crawled</div>
                            <div class="metric-value">{total_scanned} <span style="font-size:1rem;color:#94a3b8;">/ {max_pages}</span></div>
                            <div class="metric-sub">In Queue: {queue_size} pages</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Links Checked</div>
                            <div class="metric-value">{total_checked}</div>
                            <div class="metric-sub">Unique URL queries</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Broken Links</div>
                            <div class="metric-value {'error' if broken_count > 0 else 'success'}">{broken_count}</div>
                            <div class="metric-sub">Verified errors</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Link Health</div>
                            <div class="metric-value {'success' if broken_count == 0 else ''}">
                                {round((1 - broken_count / max(total_checked, 1)) * 100, 1)}%
                            </div>
                            <div class="metric-sub">Valid link ratio</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Progress & Console Update
                progress_ratio = min(total_scanned / max_pages, 1.0)
                progress_placeholder.progress(progress_ratio)
                status_placeholder.markdown(
                    f"""
                    <div class="status-panel">
                        <span style="color:#2563EB;">▶ Inspecting:</span> {event['current_page']}
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

                progress_placeholder.progress(1.0)
                status_placeholder.markdown(
                    f"""
                    <div class="status-panel" style="background:#F0FDF4; border-color:#BBF7D0; color:#166534;">
                        ✓ Crawl completed. Audited a total of {total_scanned} pages and {total_checked} unique links.
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # Audit Results Report Section
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Audit Results Report")

        if not broken_dict:
            st.success("Great news! No broken links or 404 errors were found across all scanned pages. The website looks clean and healthy.")
        else:
            records = []
            for b in broken_dict.values():
                records.append({
                    "Broken URL": b.target_url,
                    "Status": b.error_reason,
                    "HTTP Code": b.status_code if b.status_code else "-",
                    "Link Type": "Internal Link" if b.is_internal else "External Link",
                    "Anchor Text": b.link_text,
                    "Discovered On": b.first_found_on,
                    "Occurrences": b.total_occurrences,
                    "raw_status": b.status_code
                })

            df = pd.DataFrame(records)

            # Categorized Tabbed Views
            tab1, tab2, tab3 = st.tabs([
                f"All Broken Links ({len(df)})",
                f"404 Not Found ({len(df[df['raw_status'] == 404])})",
                f"Server & Network Errors ({len(df[df['raw_status'] != 404])})"
            ])

            def render_table(filtered_df: pd.DataFrame):
                if filtered_df.empty:
                    st.info("No broken links found in this category.")
                    return

                display_cols = [
                    "Broken URL",
                    "Status",
                    "HTTP Code",
                    "Link Type",
                    "Anchor Text",
                    "Discovered On",
                    "Occurrences"
                ]

                st.dataframe(
                    filtered_df[display_cols],
                    use_container_width=True,
                    column_config={
                        "Broken URL": st.column_config.LinkColumn("Broken URL"),
                        "Discovered On": st.column_config.LinkColumn("Discovered On"),
                        "Occurrences": st.column_config.NumberColumn("Occurrences", format="%d"),
                        "HTTP Code": st.column_config.TextColumn("HTTP Code")
                    },
                    hide_index=True
                )

            with tab1:
                render_table(df)

            with tab2:
                render_table(df[df["raw_status"] == 404])

            with tab3:
                render_table(df[df["raw_status"] != 404])

            # Export Button
            export_cols = [
                "Broken URL",
                "Status",
                "HTTP Code",
                "Link Type",
                "Anchor Text",
                "Discovered On",
                "Occurrences"
            ]
            csv_data = df[export_cols].to_csv(index=False).encode("utf-8-sig")

            col_exp1, col_exp2 = st.columns([4, 1])
            with col_exp2:
                st.download_button(
                    label="Download Report as CSV",
                    data=csv_data,
                    file_name="university_broken_links_report.csv",
                    mime="text/csv",
                    type="secondary",
                    use_container_width=True
                )
