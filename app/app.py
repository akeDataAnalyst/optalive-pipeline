import streamlit as st
import os
import sys
import pandas as pd

# Ensure root directory is in sys.path for absolute imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data_loader import OptaLiveLoader
from src.preprocessing import OptaLivePreprocessor
from src.validation import OptaLiveValidator

# Page Configuration
st.set_page_config(
    page_title="OptaLive | Soccer Data & QA Dashboard",
    page_icon="⚽",
    layout="wide"
)

st.markdown("# ⚽ OptaLive In-Ground QA Command Center")
st.markdown("Simulating professional Stats Perform soccer event collection, line-up verification, and automated quality assurance.")
st.divider()

# Caching Data Pipeline Execution
@st.cache_data
def run_optalive_pipeline(match_id):
    loader = OptaLiveLoader(raw_data_dir="data/raw")
    lineups = loader.load_lineup(match_id)
    events = loader.load_events(match_id)
    
    preprocessor = OptaLivePreprocessor(raw_events_df=events, lineup_df=lineups)
    key_events = preprocessor.extract_key_events()
    readiness = preprocessor.validate_pre_match_readiness()
    
    validator = OptaLiveValidator(key_events_df=key_events, lineup_df=lineups)
    validated_events = validator.validate_events()
    qa_report = validator.generate_data_quality_report()
    
    return lineups, key_events, readiness, validated_events, qa_report

@st.cache_resource
def load_matches():
    loader = OptaLiveLoader(raw_data_dir="data/raw")
    return loader.load_matches()

# Sidebar: Match Selection
st.sidebar.markdown("### 🏟️ Match Configuration")
try:
    df_matches = load_matches()
    cols = df_matches.columns.tolist()
    home_col = next((c for c in cols if 'home' in c.lower() and 'name' in c.lower()), cols[0])
    away_col = next((c for c in cols if 'away' in c.lower() and 'name' in c.lower()), cols[1] if len(cols) > 1 else cols[0])
    
    df_matches['label'] = "ID: " + df_matches['match_id'].astype(str) + " | " + df_matches[home_col].astype(str) + " vs " + df_matches[away_col].astype(str)
    selected_label = st.sidebar.selectbox("Select Fixture:", df_matches['label'].tolist())
    
    selected_row = df_matches[df_matches['label'] == selected_label].iloc[0]
    match_id = int(selected_row['match_id'])
    home_team = selected_row[home_col]
    away_team = selected_row[away_col]
except Exception as e:
    st.sidebar.warning(f"Could not load match list automatically. Defaulting to Match 3754217. ({e})")
    match_id = 3754217
    home_team = "Chelsea"
    away_team = "Arsenal"

st.sidebar.info(f"Active Match: **{match_id}**\n\n*{home_team} vs {away_team}*")

# Load Pipeline Data for Selected Match
try:
    lineups, key_events, readiness, validated_events, qa_report = run_optalive_pipeline(match_id)
except Exception as e:
    st.error(f"Error executing pipeline for match {match_id}: {e}")
    st.stop()

# Main Dashboard Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Executive Summary", "📋 Pre-Match Readiness", "⏱️ Live Event Feed", "🔍 QA Audit & Export"])

with tab1:
    st.markdown("### 📈 Match Health & Incident Overview")
    c1, c2, c3, c4 = st.columns(4)
    
    score = qa_report['quality_score']
    score_color = "#10B981" if score >= 90 else "#F59E0B"
    
    c1.metric("Match Health Score", f"{score}%")
    c2.metric("Total Key Events", qa_report['total_events'])
    c3.metric("Valid Events", qa_report['valid_events'])
    c4.metric("QA Errors", qa_report['errors'])
    
    st.divider()
    st.markdown(f"**Fixture:** {home_team} vs {away_team} (Match ID: `{match_id}`)")
    st.write("This command center monitors live in-ground event streams, validates player attributions, tracks card/substitution rules, and ensures broadcast-ready data quality.")

with tab2:
    st.markdown("### 📋 Team Sheet Readiness & Roster Check")
    col1, col2 = st.columns(2)
    for idx, row in readiness.iterrows():
        with (col1 if idx == 0 else col2):
            status = row['readiness_status']
            st.markdown(f"""
                <div style="background: #F9FAFB; padding: 1rem; border-radius: 0.5rem; border-left: 5px solid {'#10B981' if status == 'Ready' else '#F59E0B'};">
                    <h4>{row['team_name']}</h4>
                    <p><b>Squad Size:</b> {row['total_squad']} | <b>Missing Numbers:</b> {row['missing_jersey_count']}</p>
                    <p><b>Status:</b> <code>{status}</code></p>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("#### Squad Lineups")
    st.dataframe(lineups[['team_name', 'jersey_number', 'player_name', 'country']].rename(columns={'team_name': 'Team', 'jersey_number': 'Shirt #', 'player_name': 'Player', 'country': 'Nationality'}), use_container_width=True, hide_index=True)

with tab3:
    st.markdown("### ⏱️ Chronological Match Event Feed")
    if key_events.empty:
        st.info("No key events found.")
    else:
        for _, row in key_events.iterrows():
            icon = "⚽" if row['event_type'] == "Goal" else ("🟨" if row['event_type'] == "Card" else "🔄")
            st.markdown(f"`{row.get('period', 1)}H {row.get('minute', 0)}'` {icon} **{row['team_name']}** — {row['player_name']} *({row['event_type']}: {row.get('detail', '')})*")

with tab4:
    st.markdown("### 🔍 Automated QA Audit & Downloads")
    st.dataframe(validated_events[['minute', 'event_type', 'team_name', 'player_name', 'validation_status', 'issue_description']], use_container_width=True, hide_index=True)
    
    st.markdown("#### 📥 Download Reports")
    d1, d2 = st.columns(2)
    with d1:
        st.download_button("Download Key Events CSV", key_events.to_csv(index=False).encode('utf-8'), f"key_events_{match_id}.csv", "text/csv")
    with d2:
        st.download_button("Download QA Audit Log CSV", validated_events.to_csv(index=False).encode('utf-8'), f"qa_audit_{match_id}.csv", "text/csv")