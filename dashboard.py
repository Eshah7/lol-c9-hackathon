#!/usr/bin/env python3
"""
Interactive League of Legends Match Dashboard
Streamlit dashboard for visualizing GRID API match data.
"""

import streamlit as st
import sys
import os
import json
from typing import Dict, Any, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))

from utils import get_api_key
from series_state_api import get_series_state
from scouting_report import generate_scouting_report, format_scouting_report

# Page config
st.set_page_config(
    page_title="LoL Match Dashboard",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cached API calls
@st.cache_data(ttl=3600)
def get_series_state_cached(series_id, api_key):
    return get_series_state(series_id, api_key)

@st.cache_data(ttl=3600)
def get_team_recent_series_cached(team_id, api_key):
    from scouting_report import get_team_recent_series
    return get_team_recent_series(team_id, api_key=api_key)

@st.cache_data(ttl=3600)
def generate_scouting_report_cached(team_id, team_name=None, days=None, api_key=None):
    return generate_scouting_report(team_id, team_name, days, api_key)

# Initialize session state
if "api_key" not in st.session_state:
    st.session_state.api_key = get_api_key(require_key=False)

# Sidebar
with st.sidebar:
    st.title("🎮 LoL Match Dashboard")
    st.markdown("---")
    
    st.subheader("Configuration")
    api_key_input = st.text_input(
        "API Key",
        value=st.session_state.api_key or "",
        type="password",
        help="Enter your GRID API key"
    )
    if api_key_input:
        st.session_state.api_key = api_key_input
    
    st.markdown("---")
    
    st.subheader("Navigation")
    # Use session state to control the current page
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Match Analysis"
    
    # Update current_page if radio changes
    page = st.radio(
        "Select Page",
        ["Match Analysis", "Team Scouting", "Player Stats"],
        index=["Match Analysis", "Team Scouting", "Player Stats"].index(st.session_state.current_page),
        key="page_selector"
    )
    st.session_state.current_page = page

# Main content
if page == "Match Analysis":
    st.title("📊 Match Analysis")
    st.markdown("Analyze individual match series")
    
    # Known team IDs for League of Legends (same as in Scouting page)
    known_teams = {
        "Select a team...": "",
        "T1": "47494",
        "Gen.G Esports": "47558",
        "DRX": "47559",
        "Dplus KIA": "47560",
        "KT Rolster": "47561",
        "Hanwha Life Esports": "47562",
        "Nongshim RedForce": "47563",
        "OKSavingsBank BRION": "47564",
        "Kwangdong Freecs": "47565",
        "Liiv SANDBOX": "47566"
    }
    
    with st.expander("🔍 Discover Series by Team", expanded=False):
        col1, col2 = st.columns([2, 1])
        with col1:
            discovery_team = st.selectbox(
                "Select Team to find Series IDs",
                options=list(known_teams.keys()),
                key="discovery_team_select"
            )
        with col2:
            lookback_discovery = st.selectbox(
                "Lookback (Days)",
                options=[30, 90, 180, 365, 730],
                index=1,
                help="Search for series within this timeframe",
                key="discovery_lookback"
            )
        
        if discovery_team != "Select a team...":
            discovery_team_id = known_teams[discovery_team]
            with st.spinner(f"Fetching recent series for {discovery_team}..."):
                # Use a higher limit for discovery
                from scouting_report import get_team_recent_series
                recent_series = get_team_recent_series(discovery_team_id, days=lookback_discovery, limit=100, api_key=st.session_state.api_key)
            
            if recent_series:
                series_options = []
                for s in recent_series:
                    opp = "Unknown"
                    for t in s.get("teams", []):
                        if t.get("baseInfo", {}).get("id") != discovery_team_id:
                            opp = t.get("baseInfo", {}).get("name", "Unknown")
                            break
                    date = s.get("startTimeScheduled", "")[:10]
                    series_options.append({
                        "id": s["id"],
                        "label": f"{s['id']} - vs {opp} ({date})"
                    })
                
                selected_discovery = st.selectbox(
                    "Recent Series",
                    options=series_options,
                    format_func=lambda x: x["label"]
                )
                
                if st.button("Load Selected Series ID"):
                    st.session_state.selected_series_id = selected_discovery["id"]
                    st.rerun()
            else:
                st.warning("No series found for this team.")

    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Use session state for series ID if available
        default_series_id = st.session_state.get("selected_series_id", "2616372")
        series_id = st.text_input(
            "Series ID",
            value=default_series_id,
            help="Enter a GRID API Series ID"
        )
    
    with col2:
        analyze_btn = st.button("Analyze Match", type="primary")
    
    if analyze_btn and series_id:
        with st.spinner("Fetching match data..."):
            result = get_series_state_cached(series_id, st.session_state.api_key)
        
        if "errors" in result:
            st.error("❌ Error fetching match data:")
            for error in result["errors"]:
                st.error(error.get("message", "Unknown error"))
        else:
            data = result.get("data", {}).get("seriesState")
            if not data:
                st.warning("No series data found")
            else:
                # Series Overview
                st.header("📋 Series Overview")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Series ID", data.get("id"))
                with col2:
                    st.metric("Format", data.get("format", "Unknown"))
                with col3:
                    status = "✅ Finished" if data.get("finished") else "⏳ In Progress" if data.get("started") else "⏸️ Not Started"
                    st.metric("Status", status)
                with col4:
                    if data.get("startedAt"):
                        st.metric("Started", data.get("startedAt")[:10])
                
                # Teams Summary
                st.header("🏆 Teams")
                teams = data.get("teams", [])
                
                if teams:
                    team_cols = st.columns(len(teams))
                    
                    for idx, team in enumerate(teams):
                        with team_cols[idx]:
                            won_emoji = "🏅" if team.get("won") else ""
                            st.subheader(f"{won_emoji} {team.get('name', 'Unknown')}")
                            
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.metric("Score", team.get("score", 0))
                            with col_b:
                                st.metric("K/D", f"{team.get('kills', 0)}/{team.get('deaths', 0)}")
                            
                            # Players
                            st.markdown("**Players:**")
                            players = team.get("players", [])
                            for player in players:
                                kda = f"{player.get('kills', 0)}/{player.get('deaths', 0)}/{player.get('killAssistsGiven', 0)}"
                                st.text(f"  {player.get('name', 'Unknown')}: {kda}")
                
                # Games Breakdown
                st.header("🎮 Games")
                games = data.get("games", [])
                
                if games:
                    for game in games:
                        with st.expander(f"Game {game.get('sequenceNumber', '?')}: {game.get('map', {}).get('name', 'Unknown Map')}", expanded=True):
                            game_teams = game.get("teams", [])
                            
                            # Game score comparison
                            if len(game_teams) == 2:
                                team1_score = game_teams[0].get("score", 0)
                                team2_score = game_teams[1].get("score", 0)
                                
                                fig = go.Figure(data=[
                                    go.Bar(
                                        x=[game_teams[0].get("name", "Team 1"), game_teams[1].get("name", "Team 2")],
                                        y=[team1_score, team2_score],
                                        marker_color=['#1f77b4' if game_teams[0].get("won") else '#d62728',
                                                     '#1f77b4' if game_teams[1].get("won") else '#d62728']
                                    )
                                ])
                                fig.update_layout(
                                    title="Game Score",
                                    yaxis_title="Score",
                                    height=300
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            
                            # Team details
                            for team in game_teams:
                                won_emoji = "🏅" if team.get("won") else ""
                                st.subheader(f"{won_emoji} {team.get('name', 'Unknown')} ({team.get('side', 'Unknown')})")
                                
                                # Player performance table
                                players_data = []
                                for player in team.get("players", []):
                                    champ = player.get("character", {}).get("name", "Unknown")
                                    kda = (player.get("kills", 0) + player.get("killAssistsGiven", 0)) / max(player.get("deaths", 1), 1)
                                    players_data.append({
                                        "Player": player.get("name", "Unknown"),
                                        "Champion": champ,
                                        "K": player.get("kills", 0),
                                        "D": player.get("deaths", 0),
                                        "A": player.get("killAssistsGiven", 0),
                                        "KDA": f"{kda:.2f}"
                                    })
                                
                                if players_data:
                                    df = pd.DataFrame(players_data)
                                    st.dataframe(df, use_container_width=True, hide_index=True)

elif page == "Team Scouting":
    st.title("🔍 Team Scouting Report")
    st.markdown("Generate comprehensive pre-game scouting reports from all available matches")
    
    # Known team IDs for League of Legends
    known_teams = {
        "Select a team...": "",
        "T1": "47494",
        "Gen.G Esports": "47558",
        "DRX": "47559",
        "Dplus KIA": "47560",
        "KT Rolster": "47561",
        "Hanwha Life Esports": "47562",
        "Nongshim RedForce": "47563",
        "OKSavingsBank BRION": "47564",
        "Kwangdong Freecs": "47565",
        "Liiv SANDBOX": "47566"
    }
    
    tab1, tab2 = st.tabs(["Individual Scouting", "Aggregated Scouting"])
    
    with tab1:
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            selected_team = st.selectbox(
                "Select Team",
                options=list(known_teams.keys()),
                help="Choose a team from the dropdown or select 'Custom' to enter a team ID",
                key="individual_team_select"
            )
            
            if selected_team == "Select a team...":
                team_id = ""
                team_name = ""
            else:
                team_id = known_teams[selected_team]
                team_name = selected_team
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Spacing
            custom_team = st.checkbox("Use Custom Team ID", help="Enter a custom team ID", key="individual_custom_check")
        
        with col3:
            lookback_days = st.selectbox(
                "Lookback Period",
                options=[30, 90, 180, 365, "All Time"],
                index=1,
                help="How far back to analyze matches"
            )
            days_param = None if lookback_days == "All Time" else lookback_days
        
        if custom_team:
            team_id = st.text_input(
                "Custom Team ID",
                value="",
                help="Enter a GRID API Team ID",
                key="individual_custom_id"
            )
            team_name = st.text_input(
                "Team Name (optional)",
                value="",
                help="Optional team name for display",
                key="individual_custom_name"
            )
        
        # Automatic generation if team is selected
        if team_id:
            with st.spinner(f"Generating scouting report for {team_name if team_name else team_id} (period: {lookback_days})..."):
                report = generate_scouting_report_cached(
                    team_id,
                    team_name if team_name else None,
                    days=days_param,
                    api_key=st.session_state.api_key
                )
            
            if "error" in report:
                st.error(f"❌ Error: {report['error']}")
            else:
                # Overview
                st.header(f"📊 {report['team_name']} - Scouting Report")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Series Analyzed", report["series_analyzed"])
                with col2:
                    st.metric("Win Rate", f"{report['overall_stats']['win_rate']:.1f}%")
                with col3:
                    st.metric("Wins", report["overall_stats"]["wins"])
                with col4:
                    st.metric("Losses", report["overall_stats"]["losses"])
                
                # Win rate chart
                fig = go.Figure(data=[
                    go.Bar(
                        x=["Wins", "Losses"],
                        y=[report["overall_stats"]["wins"], report["overall_stats"]["losses"]],
                        marker_color=['#2ecc71', '#e74c3c']
                    )
                ])
                fig.update_layout(
                    title="Win/Loss Record",
                    yaxis_title="Games",
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Top Champions
                st.header("🎮 Top Champions")
                if report["top_champions"]:
                    champs_data = []
                    for champ, stats in list(report["top_champions"].items())[:10]:
                        champs_data.append({
                            "Champion": champ,
                            "Games": stats["games"],
                            "Wins": stats["wins"],
                            "Win Rate": f"{stats['win_rate']:.1f}%",
                            "KDA": f"{stats['kda']:.2f}"
                        })
                    
                    df_champs = pd.DataFrame(champs_data)
                    st.dataframe(df_champs, use_container_width=True, hide_index=True)
                    
                    # Champion usage chart
                    fig = px.bar(
                        df_champs,
                        x="Champion",
                        y="Games",
                        color="Win Rate",
                        title="Champion Usage",
                        color_continuous_scale="RdYlGn"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Map Performance
                st.header("🗺️ Map Performance")
                if report["map_performance"]:
                    maps_data = []
                    for map_name, perf in report["map_performance"].items():
                        maps_data.append({
                            "Map": map_name,
                            "Wins": perf["wins"],
                            "Losses": perf["losses"],
                            "Win Rate": f"{perf['win_rate']:.1f}%"
                        })
                    
                    df_maps = pd.DataFrame(maps_data)
                    st.dataframe(df_maps, use_container_width=True, hide_index=True)
                
                # Recent Series
                st.header("📅 Series History")
                st.markdown("All series analyzed for this scouting report.")
                if report["recent_series"]:
                    series_data = []
                    for series in report["recent_series"]:
                        series_data.append({
                            "Series ID": series["series_id"],
                            "Date": series["date"][:10] if series["date"] else "Unknown",
                            "Opponent": series["opponent"],
                            "Result": series["result"],
                            "Score": series["score"]
                        })
                    
                    df_series = pd.DataFrame(series_data)
                    st.dataframe(df_series, use_container_width=True, hide_index=True)
                    
                    # Quick navigation to Match Analysis
                    st.subheader("🔍 Analyze a Specific Series")
                    series_options = [f"{s['series_id']} vs {s['opponent']} ({s['date'][:10] if s['date'] else '?'})" for s in report["recent_series"]]
                    selected_series_idx = st.selectbox("Select a series to analyze in detail:", range(len(series_options)), format_func=lambda x: series_options[x], key="scouting_series_nav")
                    
                    if st.button("Go to Match Analysis", key="scouting_go_btn"):
                        st.session_state.selected_series_id = report["recent_series"][selected_series_idx]["series_id"]
                        st.session_state.current_page = "Match Analysis"
                        st.rerun()

    with tab2:
        st.header("🏢 Aggregated Scouting (Multi-Team)")
        st.markdown("Combine statistics from multiple teams to identify region-wide trends or common patterns.")
        
        selected_aggregated_teams = st.multiselect(
            "Select Teams to Aggregate",
            options=[t for t in known_teams.keys() if t != "Select a team..."],
            help="Select one or more teams to combine into a single report"
        )
        
        lookback_agg = st.selectbox(
            "Lookback Period (Aggregated)",
            options=[30, 90, 180, 365, "All Time"],
            index=1,
            help="How far back to analyze matches for all selected teams",
            key="agg_lookback"
        )
        days_agg_param = None if lookback_agg == "All Time" else lookback_agg
        
        if st.button("Generate Aggregated Report", type="primary") and selected_aggregated_teams:
            aggregated_reports = []
            with st.spinner(f"Gathering data for {len(selected_aggregated_teams)} teams (period: {lookback_agg})..."):
                for team_name in selected_aggregated_teams:
                    team_id = known_teams[team_name]
                    rep = generate_scouting_report_cached(team_id, team_name, days=days_agg_param, api_key=st.session_state.api_key)
                    if "error" not in rep:
                        aggregated_reports.append(rep)
            
            if not aggregated_reports:
                st.error("Could not generate reports for any of the selected teams.")
            else:
                # Aggregate Logic
                total_series = sum(r["series_analyzed"] for r in aggregated_reports)
                total_wins = sum(r["overall_stats"]["wins"] for r in aggregated_reports)
                total_losses = sum(r["overall_stats"]["losses"] for r in aggregated_reports)
                
                # Combine champions
                combined_champs = defaultdict(lambda: {"games": 0, "wins": 0, "kda_sum": 0, "count": 0})
                for r in aggregated_reports:
                    for champ, stats in r["top_champions"].items():
                        combined_champs[champ]["games"] += stats["games"]
                        combined_champs[champ]["wins"] += stats["wins"]
                        combined_champs[champ]["kda_sum"] += stats["kda"]
                        combined_champs[champ]["count"] += 1
                
                # Display Aggregated Results
                st.subheader(f"📊 Aggregated Report for: {', '.join(selected_aggregated_teams)}")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Series Analyzed", total_series)
                with col2:
                    st.metric("Average Win Rate", f"{(total_wins/total_series*100):.1f}%" if total_series > 0 else "0%")
                with col3:
                    st.metric("Teams Included", len(aggregated_reports))
                
                # Combined Champions Table
                st.subheader("🎮 Aggregated Champion Usage")
                agg_champs_data = []
                for champ, stats in sorted(combined_champs.items(), key=lambda x: x[1]["games"], reverse=True)[:15]:
                    win_rate = (stats["wins"] / stats["games"] * 100) if stats["games"] > 0 else 0
                    avg_kda = stats["kda_sum"] / stats["count"]
                    agg_champs_data.append({
                        "Champion": champ,
                        "Total Games": stats["games"],
                        "Total Wins": stats["wins"],
                        "Avg Win Rate": f"{win_rate:.1f}%",
                        "Avg KDA": f"{avg_kda:.2f}"
                    })
                
                st.dataframe(pd.DataFrame(agg_champs_data), use_container_width=True, hide_index=True)
                
                # Maps
                st.subheader("🗺️ Aggregated Map Performance")
                combined_maps = defaultdict(lambda: {"wins": 0, "losses": 0})
                for r in aggregated_reports:
                    for map_name, stats in r["map_performance"].items():
                        combined_maps[map_name]["wins"] += stats["wins"]
                        combined_maps[map_name]["losses"] += stats["losses"]
                
                agg_maps_data = []
                for map_name, stats in combined_maps.items():
                    total = stats["wins"] + stats["losses"]
                    win_rate = (stats["wins"] / total * 100) if total > 0 else 0
                    agg_maps_data.append({
                        "Map": map_name,
                        "Total Wins": stats["wins"],
                        "Total Losses": stats["losses"],
                        "Win Rate": f"{win_rate:.1f}%"
                    })
                st.dataframe(pd.DataFrame(agg_maps_data), use_container_width=True, hide_index=True)

elif page == "Player Stats":
    st.title("👤 Player Statistics")
    st.markdown("Analyze individual player performance")
    
    st.info("🚧 Player stats page - Coming soon! Use Match Analysis to view player performance in specific matches.")
    
    # Placeholder for future player stats functionality
    series_id = st.text_input(
        "Series ID",
        value="2616372",
        help="Enter a Series ID to view player stats"
    )
    
    if st.button("View Player Stats"):
        with st.spinner("Loading player data..."):
            result = get_series_state(series_id, st.session_state.api_key)
        
        if "errors" not in result and result.get("data", {}).get("seriesState"):
            data = result["data"]["seriesState"]
            teams = data.get("teams", [])
            
            all_players = []
            for team in teams:
                for player in team.get("players", []):
                    kda = (player.get("kills", 0) + player.get("killAssistsGiven", 0)) / max(player.get("deaths", 1), 1)
                    all_players.append({
                        "Team": team.get("name", "Unknown"),
                        "Player": player.get("name", "Unknown"),
                        "K": player.get("kills", 0),
                        "D": player.get("deaths", 0),
                        "A": player.get("killAssistsGiven", 0),
                        "KDA": f"{kda:.2f}"
                    })
            
            if all_players:
                df = pd.DataFrame(all_players)
                st.dataframe(df, use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>League of Legends Match Dashboard | Powered by GRID API</p>
    </div>
    """,
    unsafe_allow_html=True
)

