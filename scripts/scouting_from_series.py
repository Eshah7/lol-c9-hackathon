#!/usr/bin/env python3
"""
Alternative Scouting Report - Build from Known Series IDs
This works around the team ID issue by analyzing specific series.
"""

import json
import sys
import os
from typing import Dict, Any, List, Optional
from collections import defaultdict, Counter

sys.path.insert(0, os.path.dirname(__file__))
from utils import get_api_key
from series_state_api import get_series_state

def analyze_series_list(series_ids: List[str], team_name: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """Analyze a list of series IDs to generate a scouting report."""
    
    print(f"🔍 Analyzing {len(series_ids)} series for {team_name}...")
    
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
    analyzed_series = []
    
    for series_id in series_ids:
        print(f"   Analyzing series {series_id}...")
        result = get_series_state(series_id, api_key)
        
        if "errors" in result or not result.get("data", {}).get("seriesState"):
            print(f"   ⚠️  Skipping {series_id} - error or no data")
            continue
        
        series_data = result["data"]["seriesState"]
        teams = series_data.get("teams", [])
        
        # Find our team
        team_data = None
        opponent_data = None
        for team in teams:
            if team_name.lower() in team.get("name", "").lower():
                team_data = team
            else:
                opponent_data = team
        
        if not team_data:
            print(f"   ⚠️  Team '{team_name}' not found in series {series_id}")
            continue
        
        team_won = team_data.get("won", False)
        if opponent_data:
            opponents_faced[opponent_data["name"]] += 1
        
        analyzed_series.append({
            "series_id": series_id,
            "date": series_data.get("startedAt"),
            "opponent": opponent_data["name"] if opponent_data else "Unknown",
            "result": "Win" if team_won else "Loss",
            "score": f"{team_data.get('score', 0)}-{opponent_data.get('score', 0) if opponent_data else 0}"
        })
        
        # Analyze games
        for game in series_data.get("games", []):
            game_teams = game.get("teams", [])
            team_game_data = None
            
            for gt in game_teams:
                if team_name.lower() in gt.get("name", "").lower():
                    team_game_data = gt
                    break
            
            if not team_game_data:
                continue
            
            map_name = game.get("map", {}).get("name", "Unknown")
            if team_game_data.get("won"):
                win_rate_by_map[map_name]["wins"] += 1
            else:
                win_rate_by_map[map_name]["losses"] += 1
            
            # Track champions
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
        for player in team_data.get("players", []):
            player_id = player.get("id")
            player_stats[player_id]["series_played"] += 1
            if team_won:
                player_stats[player_id]["wins"] += 1
            player_stats[player_id]["total_kills"] += player.get("kills", 0)
            player_stats[player_id]["total_deaths"] += player.get("deaths", 0)
            player_stats[player_id]["total_assists"] += player.get("killAssistsGiven", 0)
    
    if not analyzed_series:
        return {"error": f"No valid series found for {team_name}"}
    
    # Calculate stats
    total_series = len(analyzed_series)
    wins = sum(1 for s in analyzed_series if s["result"] == "Win")
    win_rate = (wins / total_series * 100) if total_series > 0 else 0
    
    # Champion win rates
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
    
    top_champions = sorted(champion_win_rates.items(), key=lambda x: x[1]["games"], reverse=True)[:10]
    
    # Player performance
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
            "top_champion": top_champ
        }
    
    # Map performance
    map_performance = {}
    for map_name, stats in win_rate_by_map.items():
        total = stats["wins"] + stats["losses"]
        win_rate_map = (stats["wins"] / total * 100) if total > 0 else 0
        map_performance[map_name] = {
            "wins": stats["wins"],
            "losses": stats["losses"],
            "win_rate": win_rate_map
        }
    
    return {
        "team_name": team_name,
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
        "recent_series": analyzed_series
    }

def format_report(report: Dict[str, Any]) -> str:
    """Format the report."""
    if "error" in report:
        return f"❌ Error: {report['error']}"
    
    output = []
    output.append("=" * 80)
    output.append(f"📊 SCOUTING REPORT: {report['team_name']}")
    output.append("=" * 80)
    output.append(f"Series Analyzed: {report['series_analyzed']}")
    output.append("")
    
    stats = report["overall_stats"]
    output.append("📈 OVERALL PERFORMANCE")
    output.append("-" * 80)
    output.append(f"Win Rate: {stats['win_rate']:.1f}% ({stats['wins']}W-{stats['losses']}L)")
    output.append("")
    
    output.append("🎮 TOP CHAMPIONS")
    output.append("-" * 80)
    for champ, stats in list(report["top_champions"].items())[:10]:
        output.append(f"  {champ:20s} | Games: {stats['games']:2d} | Win Rate: {stats['win_rate']:5.1f}% | KDA: {stats['kda']:.2f}")
    output.append("")
    
    output.append("🗺️  MAP PERFORMANCE")
    output.append("-" * 80)
    for map_name, perf in sorted(report["map_performance"].items(), key=lambda x: x[1]["win_rate"], reverse=True):
        output.append(f"  {map_name:20s} | {perf['wins']}W-{perf['losses']}L | Win Rate: {perf['win_rate']:.1f}%")
    output.append("")
    
    output.append("📅 SERIES ANALYZED")
    output.append("-" * 80)
    for series in report["recent_series"]:
        result_emoji = "✅" if series["result"] == "Win" else "❌"
        output.append(f"  {result_emoji} vs {series['opponent']:20s} | {series['score']:10s} | Series: {series['series_id']}")
    output.append("")
    
    return "\n".join(output)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 scouting_from_series.py <team_name> <series_id1> [series_id2] ...")
        print("Example: python3 scouting_from_series.py T1 2616372 2616371")
        print("\nThis analyzes specific series IDs instead of searching by team ID.")
        sys.exit(1)
    
    team_name = sys.argv[1]
    series_ids = sys.argv[2:]
    
    api_key = get_api_key(require_key=False)
    
    report = analyze_series_list(series_ids, team_name, api_key)
    print(format_report(report))
    
    if "--save-json" in sys.argv:
        filename = f"scouting_report_{team_name.replace(' ', '_')}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n💾 Report saved to: {filename}")

