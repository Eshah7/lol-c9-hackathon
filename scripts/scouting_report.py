#!/usr/bin/env python3
"""
Pre-Game Scouting Report Generator
Analyzes team and player data from GRID API to generate scouting reports.
"""

import json
import sys
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter

# Import shared utilities and API modules
sys.path.insert(0, os.path.dirname(__file__))
from utils import get_api_key
from api_explorer import query_graphql as query_central_data, API_URL
from series_state_api import query_graphql as query_series_state, SERIES_STATE_API_URL

def get_team_recent_series(team_id: str, days: Optional[int] = None, limit: int = 100, api_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get recent series for a team with pagination support.
    
    Args:
        team_id: Team ID to search for
        days: Number of days to look back. If None, searches all available series.
        limit: Maximum number of series to return (default 100)
        api_key: API key for authentication
    """
    all_series_list = []
    has_next_page = True
    after_cursor = None
    
    # GRID API has a max page size of 50
    page_size = 50
    
    # Build filter - if days is None, don't filter by date
    cutoff_date = None
    if days is not None:
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat() + "Z"

    print(f"📡 Fetching series for team {team_id}...")

    while has_next_page and len(all_series_list) < limit:
        current_limit = min(page_size, limit - len(all_series_list))
        
        if cutoff_date:
            query = """
            query TeamRecentSeries($teamId: [ID!]!, $cutoffDate: String!, $limit: Int!, $after: Cursor) {
                allSeries(
                    filter: {
                        teamIds: { in: $teamId }
                        startTimeScheduled: { gte: $cutoffDate }
                    }
                    orderBy: StartTimeScheduled
                    orderDirection: DESC
                    first: $limit
                    after: $after
                ) {
                    totalCount
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                    edges {
                        node {
                            id
                            startTimeScheduled
                            format {
                                name
                            }
                            teams {
                                baseInfo {
                                    id
                                    name
                                }
                            }
                        }
                    }
                }
            }
            """
            variables = {
                "teamId": [team_id],
                "cutoffDate": cutoff_date,
                "limit": current_limit,
                "after": after_cursor
            }
        else:
            query = """
            query TeamRecentSeries($teamId: [ID!]!, $limit: Int!, $after: Cursor) {
                allSeries(
                    filter: {
                        teamIds: { in: $teamId }
                    }
                    orderBy: StartTimeScheduled
                    orderDirection: DESC
                    first: $limit
                    after: $after
                ) {
                    totalCount
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                    edges {
                        node {
                            id
                            startTimeScheduled
                            format {
                                name
                            }
                            teams {
                                baseInfo {
                                    id
                                    name
                                }
                            }
                        }
                    }
                }
            }
            """
            variables = {
                "teamId": [team_id],
                "limit": current_limit,
                "after": after_cursor
            }
        
        result = query_central_data(query, variables, api_key)
        
        if "errors" in result:
            print(f"⚠️  API Errors when fetching series for team {team_id}:")
            for error in result["errors"]:
                print(f"   - {error.get('message', 'Unknown error')}")
            break
            
        data = result.get("data", {}).get("allSeries", {})
        if not data:
            break
            
        edges = data.get("edges", [])
        for edge in edges:
            all_series_list.append(edge["node"])
            
        page_info = data.get("pageInfo", {})
        has_next_page = page_info.get("hasNextPage", False)
        after_cursor = page_info.get("endCursor")
        
        if not edges:
            break
            
    print(f"✅ Fetched {len(all_series_list)} series.")
    return all_series_list

def analyze_series_for_team(series_id: str, team_id: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """Analyze a series from a specific team's perspective."""
    query = """
    query SeriesAnalysis($seriesId: ID!) {
        seriesState(id: $seriesId) {
            id
            startedAt
            format
            teams {
                id
                name
                score
                won
                kills
                deaths
                players {
                    id
                    name
                    kills
                    deaths
                    killAssistsGiven
                }
            }
            games {
                id
                sequenceNumber
                started
                finished
                map {
                    name
                }
                teams {
                    id
                    name
                    side
                    won
                    score
                    kills
                    deaths
                    players {
                        id
                        name
                        kills
                        deaths
                        killAssistsGiven
                        character {
                            id
                            name
                        }
                    }
                }
            }
        }
    }
    """
    variables = {"seriesId": series_id}
    result = query_series_state(query, variables, api_key)
    
    if "errors" in result or not result.get("data", {}).get("seriesState"):
        return None
    
    series_data = result["data"]["seriesState"]
    team_data = None
    opponent_data = None
    
    for team in series_data.get("teams", []):
        if team.get("id") == team_id:
            team_data = team
        else:
            opponent_data = team
    
    if not team_data:
        return None
    
    return {
        "series_id": series_id,
        "date": series_data.get("startedAt"),
        "format": series_data.get("format"),
        "team": team_data,
        "opponent": opponent_data,
        "games": series_data.get("games", [])
    }

def generate_insights(top_champions: List, map_performance: Dict, player_performance: Dict) -> Dict[str, Any]:
    """Generate strategic insights based on the scouting data."""
    look_out_for = []
    how_to_beat = []
    
    # 1. Champion threats
    high_winrate_champs = [c for c, s in top_champions if s["win_rate"] > 70 and s["games"] >= 3]
    if not high_winrate_champs:
        high_winrate_champs = [c for c, s in top_champions if s["win_rate"] >= 50 and s["games"] >= 2]
    
    if high_winrate_champs:
        champ = high_winrate_champs[0]
        look_out_for.append(f"Highly effective {champ} usage ({dict(top_champions)[champ]['win_rate']:.1f}% win rate)")
        how_to_beat.append(f"Prioritize banning {champ} or drafting a hard counter")
    
    # 2. Player threats
    top_players = sorted(player_performance.items(), key=lambda x: x[1]["kda"], reverse=True)
    if top_players:
        p_id, p_stats = top_players[0]
        look_out_for.append(f"Carry performance from Player {p_id} (Average KDA: {p_stats['kda']:.2f})")
        how_to_beat.append(f"Focus early pressure and vision on Player {p_id}'s lane to stifle their growth")

    # 3. Map preferences
    strong_maps = sorted([m for m, s in map_performance.items() if s["wins"] > 0], 
                         key=lambda m: map_performance[m]["win_rate"], reverse=True)
    if strong_maps:
        m_name = strong_maps[0]
        look_out_for.append(f"Dominant performance on {m_name} ({map_performance[m_name]['win_rate']:.1f}% win rate)")
        how_to_beat.append(f"Avoid playing {m_name} if possible, or prepare specific level 1 strategies for this map")

    # Default if not enough data
    while len(look_out_for) < 3:
        look_out_for.append("Consistent team coordination in mid-game transitions")
        how_to_beat.append("Force early skirmishes to disrupt their macro play")
    
    return {
        "top_3_watch_out": look_out_for[:3],
        "how_to_beat": how_to_beat[:3]
    }

def generate_scouting_report(team_id: str, team_name: Optional[str] = None, days: Optional[int] = None, api_key: Optional[str] = None) -> Dict[str, Any]:
    """Generate a comprehensive pre-game scouting report for a team.
    
    Args:
        team_id: Team ID to analyze
        team_name: Optional team name for display
        days: Number of days to look back. If None, analyzes all available series.
        api_key: API key for authentication
    """
    print(f"🔍 Generating scouting report for team {team_id}...")
    if days:
        print(f"   Looking back {days} days...")
    else:
        print(f"   Analyzing all available series...")
    
    # Get recent series (or all if days is None)
    recent_series = get_team_recent_series(team_id, days=days, api_key=api_key)
    
    if not recent_series:
        if days:
            error_msg = f"No series found for team {team_id} in the last {days} days"
            suggestion = f"Try increasing the days parameter or set days=None to analyze all available games"
        else:
            error_msg = f"No series found for team {team_id}"
            suggestion = "Team ID might be incorrect, or the team has no matches in the database"
        
        print(f"\n❌ {error_msg}")
        print(f"   Possible reasons:")
        print(f"   - Team ID might be incorrect")
        if days:
            print(f"   - No matches in the last {days} days")
            print(f"   - Try setting days=None to analyze all available games")
        else:
            print(f"   - Team has no matches in the database")
        print(f"   - Or use a known Series ID directly with: python3 scripts/series_state_api.py <series_id>")
        return {
            "error": error_msg,
            "team_id": team_id,
            "team_name": team_name,
            "suggestion": suggestion
        }
    
    print(f"📊 Analyzing {len(recent_series)} recent series...")
    
    # Analyze each series
    analyzed_series = []
    champion_pool = defaultdict(lambda: {"games": 0, "wins": 0, "kills": 0, "deaths": 0, "assists": 0})
    player_stats = defaultdict(lambda: {
        "series_played": 0,
        "wins": 0,
        "total_kills": 0,
        "total_deaths": 0,
        "total_assists": 0,
        "champions": Counter()
    })
    opponents_faced = Counter()
    win_rate_by_map = defaultdict(lambda: {"wins": 0, "losses": 0})
    
    for series_info in recent_series:
        series_id = series_info["id"]
        analysis = analyze_series_for_team(series_id, team_id, api_key)
        
        if not analysis:
            continue
        
        analyzed_series.append(analysis)
        
        # Track opponents
        if analysis.get("opponent"):
            opponents_faced[analysis["opponent"]["name"]] += 1
        
        # Track win/loss
        team_won = analysis["team"].get("won", False)
        
        # Analyze games
        for game in analysis.get("games", []):
            game_teams = game.get("teams", [])
            team_game_data = None
            opponent_game_data = None
            
            for gt in game_teams:
                if gt.get("id") == team_id:
                    team_game_data = gt
                else:
                    opponent_game_data = gt
            
            if not team_game_data:
                continue
            
            # Track map performance
            map_name = game.get("map", {}).get("name", "Unknown")
            if team_game_data.get("won"):
                win_rate_by_map[map_name]["wins"] += 1
            else:
                win_rate_by_map[map_name]["losses"] += 1
            
            # Track champion usage
            for player in team_game_data.get("players", []):
                player_id = player.get("id")
                player_name = player.get("name", "Unknown")
                char_name = player.get("character", {}).get("name", "Unknown")
                
                if char_name != "Unknown":
                    champion_pool[char_name]["games"] += 1
                    if team_game_data.get("won"):
                        champion_pool[char_name]["wins"] += 1
                    champion_pool[char_name]["kills"] += player.get("kills", 0)
                    champion_pool[char_name]["deaths"] += player.get("deaths", 0)
                    champion_pool[char_name]["assists"] += player.get("killAssistsGiven", 0)
                    
                    player_stats[player_id]["champions"][char_name] += 1
        
        # Track player series stats
        for player in analysis["team"].get("players", []):
            player_id = player.get("id")
            player_stats[player_id]["series_played"] += 1
            if team_won:
                player_stats[player_id]["wins"] += 1
            player_stats[player_id]["total_kills"] += player.get("kills", 0)
            player_stats[player_id]["total_deaths"] += player.get("deaths", 0)
            player_stats[player_id]["total_assists"] += player.get("killAssistsGiven", 0)
    
    # Calculate win rates
    total_series = len(analyzed_series)
    wins = sum(1 for s in analyzed_series if s["team"].get("won", False))
    win_rate = (wins / total_series * 100) if total_series > 0 else 0
    
    # Calculate champion win rates
    champion_win_rates = {}
    for champ, stats in champion_pool.items():
        win_rate_champ = (stats["wins"] / stats["games"] * 100) if stats["games"] > 0 else 0
        kda = (stats["kills"] + stats["assists"]) / max(stats["deaths"], 1)
        champion_win_rates[champ] = {
            "games": stats["games"],
            "wins": stats["wins"],
            "win_rate": win_rate_champ,
            "kda": kda
        }
    
    # Sort champions by usage
    top_champions = sorted(champion_win_rates.items(), key=lambda x: x[1]["games"], reverse=True)
    
    # Calculate player KDA and win rates
    player_performance = {}
    for player_id, stats in player_stats.items():
        kda = (stats["total_kills"] + stats["total_assists"]) / max(stats["total_deaths"], 1)
        player_win_rate = (stats["wins"] / stats["series_played"] * 100) if stats["series_played"] > 0 else 0
        top_champ = stats["champions"].most_common(1)[0][0] if stats["champions"] else "Unknown"
        
        player_performance[player_id] = {
            "series_played": stats["series_played"],
            "wins": stats["wins"],
            "win_rate": player_win_rate,
            "kda": kda,
            "total_kills": stats["total_kills"],
            "total_deaths": stats["total_deaths"],
            "total_assists": stats["total_assists"],
            "top_champion": top_champ
        }
    
    # Calculate map win rates
    map_performance = {}
    for map_name, stats in win_rate_by_map.items():
        total = stats["wins"] + stats["losses"]
        win_rate_map = (stats["wins"] / total * 100) if total > 0 else 0
        map_performance[map_name] = {
            "wins": stats["wins"],
            "losses": stats["losses"],
            "win_rate": win_rate_map
        }
    
    # Build report
    insights = generate_insights(top_champions, map_performance, player_performance)
    
    report = {
        "team_id": team_id,
        "team_name": team_name or analyzed_series[0]["team"]["name"] if analyzed_series else "Unknown",
        "analysis_period_days": days,
        "series_analyzed": total_series,
        "overall_stats": {
            "wins": wins,
            "losses": total_series - wins,
            "win_rate": win_rate
        },
        "top_champions": dict(top_champions),
        "player_performance": player_performance,
        "map_performance": map_performance,
        "opponents_faced": dict(opponents_faced.most_common(10)),
        "insights": insights,
        "recent_series": [
            {
                "series_id": s["series_id"],
                "date": s["date"],
                "opponent": s["opponent"]["name"] if s["opponent"] else "Unknown",
                "result": "Win" if s["team"].get("won") else "Loss",
                "score": f"{s['team'].get('score', 0)}-{s['opponent'].get('score', 0)}" if s["opponent"] else f"{s['team'].get('score', 0)}"
            }
            for s in analyzed_series
        ]
    }
    
    return report

def format_scouting_report(report: Dict[str, Any]) -> str:
    """Format scouting report as a readable string."""
    if "error" in report:
        return f"❌ Error: {report['error']}"
    
    output = []
    output.append("=" * 80)
    output.append(f"📊 PRE-GAME SCOUTING REPORT: {report['team_name']}")
    output.append("=" * 80)
    output.append("")
    output.append(f"Team ID: {report['team_id']}")
    output.append(f"Analysis Period: Last {report['analysis_period_days']} days")
    output.append(f"Series Analyzed: {report['series_analyzed']}")
    output.append("")
    
    # Overall stats
    stats = report["overall_stats"]
    output.append("📈 OVERALL PERFORMANCE")
    output.append("-" * 80)
    output.append(f"Win Rate: {stats['win_rate']:.1f}% ({stats['wins']}W-{stats['losses']}L)")
    output.append("")
    
    # Insights
    if "insights" in report:
        output.append("💡 STRATEGIC INSIGHTS")
        output.append("-" * 80)
        output.append("Top 3 things to look out for:")
        for i, item in enumerate(report["insights"]["top_3_watch_out"], 1):
            output.append(f"  {i}. {item}")
        output.append("")
        output.append("How to beat them:")
        for i, item in enumerate(report["insights"]["how_to_beat"], 1):
            output.append(f"  {i}. {item}")
        output.append("")
    
    # Top champions
    output.append("🎮 TOP CHAMPIONS (by usage)")
    output.append("-" * 80)
    for champ, stats in list(report["top_champions"].items())[:10]:
        output.append(f"  {champ:20s} | Games: {stats['games']:2d} | Win Rate: {stats['win_rate']:5.1f}% | KDA: {stats['kda']:.2f}")
    output.append("")
    
    # Player performance
    output.append("👥 PLAYER PERFORMANCE")
    output.append("-" * 80)
    for player_id, perf in sorted(report["player_performance"].items(), key=lambda x: x[1]["kda"], reverse=True):
        output.append(f"  Player ID {player_id}:")
        output.append(f"    Series: {perf['series_played']} | Win Rate: {perf['win_rate']:.1f}% | KDA: {perf['kda']:.2f}")
        output.append(f"    Top Champion: {perf['top_champion']}")
    output.append("")
    
    # Map performance
    output.append("🗺️  MAP PERFORMANCE")
    output.append("-" * 80)
    for map_name, perf in sorted(report["map_performance"].items(), key=lambda x: x[1]["win_rate"], reverse=True):
        output.append(f"  {map_name:20s} | {perf['wins']}W-{perf['losses']}L | Win Rate: {perf['win_rate']:.1f}%")
    output.append("")
    
    # Recent series
    output.append("📅 RECENT SERIES")
    output.append("-" * 80)
    for series in report["recent_series"]:
        result_emoji = "✅" if series["result"] == "Win" else "❌"
        output.append(f"  {result_emoji} vs {series['opponent']:20s} | {series['score']:10s} | {series['date']}")
    output.append("")
    
    return "\n".join(output)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 scouting_report.py <team_id> [team_name] [days]")
        print("Example: python3 scouting_report.py 47494 T1 30")
        print("\nNote: If team ID doesn't work, try using a Series ID directly:")
        print("      python3 scripts/series_state_api.py 2616372")
        print("\nOptional flags:")
        print("  --save-json    Save full report as JSON file")
        print("  --debug        Show detailed API responses")
        sys.exit(1)
    
    team_id = sys.argv[1]
    team_name = sys.argv[2] if len(sys.argv) > 2 else None
    days = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    debug = "--debug" in sys.argv
    
    api_key = get_api_key(require_key=False)
    
    if not api_key:
        print("⚠️  Warning: No API key found. Some queries may fail.")
        print("   Set GRID_API_KEY in .env file or environment variable.")
        print()
    
    report = generate_scouting_report(team_id, team_name, days, api_key)
    
    if "error" in report:
        print(format_scouting_report(report))
        print("\n💡 Alternative: Use the dashboard instead:")
        print("   streamlit run dashboard.py")
        print("   Then go to 'Team Scouting' page")
    else:
        print(format_scouting_report(report))
    
    # Save JSON (optional - just saves the data to a file)
    if "--save-json" in sys.argv:
        filename = f"scouting_report_{team_id}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n💾 Full report saved to: {filename}")
        print(f"   (This is optional - the JSON file contains all the raw data)")

