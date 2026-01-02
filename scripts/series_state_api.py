#!/usr/bin/env python3
"""
Grid.gg Series State API Explorer
Queries the Series State API to get match results, player stats, and game data.
"""

import json
import urllib.request
import urllib.parse
import ssl
from typing import Dict, Any, Optional
import os
import sys

# Series State API endpoint
SERIES_STATE_API_URL = "https://api-op.grid.gg/live-data-feed/series-state/graphql"

# Import shared utilities
sys.path.insert(0, os.path.dirname(__file__))
from utils import get_api_key

def get_headers(api_key: Optional[str] = None) -> Dict[str, str]:
    """Get request headers with API key."""
    headers = {
        "Content-Type": "application/json",
    }
    if api_key:
        headers["x-api-key"] = api_key
    return headers

def query_graphql(query: str, variables: Optional[Dict] = None, api_key: Optional[str] = None) -> Dict[str, Any]:
    """Execute a GraphQL query against Series State API."""
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        SERIES_STATE_API_URL,
        data=data,
        headers=get_headers(api_key),
        method='POST'
    )
    
    ssl_context = ssl.create_default_context()
    
    try:
        with urllib.request.urlopen(req, context=ssl_context) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except (ssl.SSLError, urllib.error.URLError) as e:
        if 'CERTIFICATE_VERIFY_FAILED' in str(e) or 'certificate' in str(e).lower():
            ssl_context = ssl._create_unverified_context()
            with urllib.request.urlopen(req, context=ssl_context) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result
        else:
            raise
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"HTTP Error {e.code}: {error_body}")
        raise

def get_series_state(series_id: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """Get complete series state for a Series ID.
    
    Uses a basic query compatible with current API schema.
    LoL-specific fragments and version-specific fields are excluded
    to ensure compatibility across different API versions.
    """
    query = """
    query SeriesState($seriesId: ID!) {
        seriesState(id: $seriesId) {
            id
            version
            title {
                nameShortened
            }
            format
            started
            finished
            valid
            startedAt
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
    return query_graphql(query, variables, api_key)

def get_latest_series_by_player(player_id: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """Get latest series state for a player."""
    query = """
    query LatestSeriesByPlayer($playerId: ID!) {
        latestSeriesStateByPlayerId(id: $playerId) {
            id
            title {
                nameShortened
            }
            format
            started
            finished
            teams {
                id
                name
                score
                won
                players {
                    id
                    name
                    kills
                    deaths
                }
            }
        }
    }
    """
    variables = {"playerId": player_id}
    return query_graphql(query, variables, api_key)

def print_series_summary(series_state: Dict[str, Any]):
    """Print a formatted summary of the series."""
    if "errors" in series_state:
        print("❌ Errors:")
        for error in series_state["errors"]:
            print(f"   - {error.get('message', 'Unknown error')}")
        return
    
    data = series_state.get("data", {}).get("seriesState")
    if not data:
        print("❌ No series data found")
        return
    
    print("=" * 70)
    print(f"📊 Series: {data.get('id')}")
    print("=" * 70)
    print(f"Title: {data.get('title', {}).get('nameShortened', 'Unknown')}")
    print(f"Format: {data.get('format', 'Unknown')}")
    print(f"Status: {'✅ Finished' if data.get('finished') else '⏳ In Progress' if data.get('started') else '⏸️  Not Started'}")
    if data.get('startedAt'):
        print(f"Started: {data.get('startedAt')}")
    print()
    
    # Teams summary
    teams = data.get("teams", [])
    if teams:
        print("🏆 Teams:")
        for team in teams:
            won_emoji = "🏅" if team.get("won") else ""
            print(f"  {won_emoji} {team.get('name', 'Unknown')}")
            print(f"     Score: {team.get('score', 0)}")
            print(f"     Kills: {team.get('kills', 0)} | Deaths: {team.get('deaths', 0)}")
            if team.get('damageDealt'):
                print(f"     Damage: {team.get('damageDealt'):,} dealt | {team.get('damageTaken', 0):,} taken")
            if team.get('visionScore'):
                print(f"     Vision Score: {team.get('visionScore'):.1f}")
            print()
    
    # Games summary
    games = data.get("games", [])
    if games:
        print(f"🎮 Games ({len(games)}):")
        for game in games:
            game_num = game.get("sequenceNumber", "?")
            map_name = game.get("map", {}).get("name", "Unknown Map")
            print(f"  Game {game_num}: {map_name}")
            print(f"     Status: {'✅ Finished' if game.get('finished') else '⏳ In Progress' if game.get('started') else '⏸️  Not Started'}")
            
            game_teams = game.get("teams", [])
            for team in game_teams:
                won_emoji = "🏅" if team.get("won") else ""
                print(f"     {won_emoji} {team.get('name', 'Unknown')} ({team.get('side', 'Unknown')}): Score {team.get('score', 0)}")
            print()
    
    # Top players (from series-level stats, character info comes from games)
    if teams:
        print("⭐ Top Players (by KDA):")
        all_players = []
        for team in teams:
            for player in team.get("players", []):
                kills = player.get("kills", 0)
                deaths = player.get("deaths", 0)
                assists = player.get("killAssistsGiven", 0)
                kda = (kills + assists) / max(deaths, 1)
                all_players.append({
                    "name": player.get("name", "Unknown"),
                    "team": team.get("name", "Unknown"),
                    "kills": kills,
                    "deaths": deaths,
                    "assists": assists,
                    "kda": kda,
                    "player_id": player.get("id")
                })
        
        all_players.sort(key=lambda x: x["kda"], reverse=True)
        for i, player in enumerate(all_players[:5], 1):
            # Try to find character from games (use most played character)
            character = "Unknown"
            if games:
                char_counts = {}
                for game in games:
                    for game_team in game.get("teams", []):
                        for game_player in game_team.get("players", []):
                            if game_player.get("id") == player["player_id"]:
                                char_name = game_player.get("character", {}).get("name")
                                if char_name:
                                    char_counts[char_name] = char_counts.get(char_name, 0) + 1
                if char_counts:
                    character = max(char_counts.items(), key=lambda x: x[1])[0]
            
            print(f"  {i}. {player['name']} ({character}) - {player['team']}")
            print(f"     K/D/A: {player['kills']}/{player['deaths']}/{player['assists']} (KDA: {player['kda']:.2f})")

def main():
    # Get API key from multiple sources
    # Get API key (prioritizes .env file, then env var, then command line)
    api_key = get_api_key()
    
    # Get series ID (now first argument since API key is optional)
    if len(sys.argv) > 1:
        # Check if first arg looks like a series ID (numeric) or API key
        first_arg = sys.argv[1]
        if first_arg.isdigit() or len(first_arg) > 20:  # Series IDs are usually numeric, API keys are long
            series_id = first_arg
        elif len(sys.argv) > 2:
            series_id = sys.argv[2]
        else:
            series_id = input("Enter Series ID: ").strip()
    else:
        series_id = input("Enter Series ID: ").strip()
    
    if not series_id:
        print("❌ No Series ID provided")
        return
    
    print(f"🔍 Querying Series State API for Series ID: {series_id}")
    print()
    
    try:
        result = get_series_state(series_id, api_key)
        print_series_summary(result)
        
        # Optionally save full JSON
        if "--save-json" in sys.argv:
            filename = f"series_state_{series_id}.json"
            with open(filename, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\n💾 Full JSON saved to: {filename}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

