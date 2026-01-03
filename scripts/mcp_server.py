#!/usr/bin/env python3
"""
MCP Server for GRID API Scouting Reports
Exposes tools for generating pre-game scouting reports and analysis.
"""

import asyncio
import json
import sys
import os
from typing import Any, Dict, List, Optional

# Add scripts to path
sys.path.insert(0, os.path.dirname(__file__))

from mcp import Server, types
from scouting_report import generate_scouting_report, format_scouting_report
from series_state_api import get_series_state
from utils import get_api_key

# Initialize MCP Server
server = Server("grid-scouting-server")

@server.list_tools()
async def list_tools() -> List[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="generate_scouting_report",
            description="Generate a comprehensive pre-game scouting report for a League of Legends team. Analyzes recent matches, champion pools, player performance, map statistics, and provides strategic insights (Top 3 watch-outs and How to beat them).",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {
                        "type": "string",
                        "description": "The GRID API team ID to analyze"
                    },
                    "team_name": {
                        "type": "string",
                        "description": "Optional team name for display purposes"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days to look back for analysis (default: 30)",
                        "default": 30
                    }
                },
                "required": ["team_id"]
            }
        ),
        types.Tool(
            name="get_series_analysis",
            description="Get detailed analysis of a specific match series including game-by-game breakdown, player stats, and champion selections.",
            inputSchema={
                "type": "object",
                "properties": {
                    "series_id": {
                        "type": "string",
                        "description": "The GRID API series ID to analyze"
                    }
                },
                "required": ["series_id"]
            }
        ),
        types.Tool(
            name="get_pre_game_analysis",
            description="Generate a pre-game analysis comparing two teams, including head-to-head records, champion pool comparisons, and strategic insights.",
            inputSchema={
                "type": "object",
                "properties": {
                    "team1_id": {
                        "type": "string",
                        "description": "First team ID"
                    },
                    "team2_id": {
                        "type": "string",
                        "description": "Second team ID"
                    },
                    "team1_name": {
                        "type": "string",
                        "description": "Optional name for first team"
                    },
                    "team2_name": {
                        "type": "string",
                        "description": "Optional name for second team"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days to look back (default: 30)",
                        "default": 30
                    }
                },
                "required": ["team1_id", "team2_id"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls."""
    api_key = get_api_key(require_key=False)
    
    if name == "generate_scouting_report":
        team_id = arguments.get("team_id")
        team_name = arguments.get("team_name")
        days = arguments.get("days", 30)
        
        report = generate_scouting_report(team_id, team_name, days, api_key)
        formatted = format_scouting_report(report)
        
        return [
            types.TextContent(
                type="text",
                text=formatted
            )
        ]
    
    elif name == "get_series_analysis":
        series_id = arguments.get("series_id")
        
        result = get_series_state(series_id, api_key)
        
        if "errors" in result:
            error_msg = "\n".join([e.get("message", "Unknown error") for e in result["errors"]])
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ Error analyzing series: {error_msg}"
                )
            ]
        
        # Format the analysis
        data = result.get("data", {}).get("seriesState")
        if not data:
            return [
                types.TextContent(
                    type="text",
                    text="❌ No series data found"
                )
            ]
        
        analysis = []
        analysis.append(f"📊 SERIES ANALYSIS: {data.get('id')}")
        analysis.append("=" * 80)
        analysis.append(f"Title: {data.get('title', {}).get('nameShortened', 'Unknown')}")
        analysis.append(f"Format: {data.get('format', 'Unknown')}")
        analysis.append(f"Status: {'✅ Finished' if data.get('finished') else '⏳ In Progress'}")
        analysis.append("")
        
        # Teams
        teams = data.get("teams", [])
        for team in teams:
            won_emoji = "🏅" if team.get("won") else ""
            analysis.append(f"{won_emoji} {team.get('name', 'Unknown')}: Score {team.get('score', 0)}")
            analysis.append(f"   Kills: {team.get('kills', 0)} | Deaths: {team.get('deaths', 0)}")
            analysis.append("")
        
        # Games
        games = data.get("games", [])
        analysis.append(f"🎮 GAMES ({len(games)}):")
        for game in games:
            game_num = game.get("sequenceNumber", "?")
            map_name = game.get("map", {}).get("name", "Unknown")
            analysis.append(f"\nGame {game_num}: {map_name}")
            
            for team in game.get("teams", []):
                won_emoji = "🏅" if team.get("won") else ""
                analysis.append(f"  {won_emoji} {team.get('name', 'Unknown')} ({team.get('side', 'Unknown')}): {team.get('score', 0)}")
                
                # Top performers
                players = sorted(
                    team.get("players", []),
                    key=lambda p: (p.get("kills", 0) + p.get("killAssistsGiven", 0)) / max(p.get("deaths", 1), 1),
                    reverse=True
                )[:3]
                
                for player in players:
                    champ = player.get("character", {}).get("name", "Unknown")
                    kda = f"{player.get('kills', 0)}/{player.get('deaths', 0)}/{player.get('killAssistsGiven', 0)}"
                    analysis.append(f"    {player.get('name', 'Unknown')} ({champ}): {kda}")
        
        return [
            types.TextContent(
                type="text",
                text="\n".join(analysis)
            )
        ]
    
    elif name == "get_pre_game_analysis":
        team1_id = arguments.get("team1_id")
        team2_id = arguments.get("team2_id")
        team1_name = arguments.get("team1_name")
        team2_name = arguments.get("team2_name")
        days = arguments.get("days", 30)
        
        # Generate reports for both teams
        report1 = generate_scouting_report(team1_id, team1_name, days, api_key)
        report2 = generate_scouting_report(team2_id, team2_name, days, api_key)
        
        # Compare
        comparison = []
        comparison.append("=" * 80)
        comparison.append("⚔️  PRE-GAME ANALYSIS: HEAD-TO-HEAD COMPARISON")
        comparison.append("=" * 80)
        comparison.append("")
        
        if "error" in report1:
            comparison.append(f"❌ Error analyzing {team1_name or team1_id}: {report1['error']}")
        else:
            comparison.append(f"📊 {report1['team_name']}")
            comparison.append(f"   Win Rate: {report1['overall_stats']['win_rate']:.1f}%")
            comparison.append(f"   Recent Record: {report1['overall_stats']['wins']}W-{report1['overall_stats']['losses']}L")
            comparison.append("")
            comparison.append("   Top Champions:")
            for champ, stats in list(report1['top_champions'].items())[:5]:
                comparison.append(f"     {champ}: {stats['games']} games, {stats['win_rate']:.1f}% WR")
        
        comparison.append("")
        
        if "error" in report2:
            comparison.append(f"❌ Error analyzing {team2_name or team2_id}: {report2['error']}")
        else:
            comparison.append(f"📊 {report2['team_name']}")
            comparison.append(f"   Win Rate: {report2['overall_stats']['win_rate']:.1f}%")
            comparison.append(f"   Recent Record: {report2['overall_stats']['wins']}W-{report2['overall_stats']['losses']}L")
            comparison.append("")
            comparison.append("   Top Champions:")
            for champ, stats in list(report2['top_champions'].items())[:5]:
                comparison.append(f"     {champ}: {stats['games']} games, {stats['win_rate']:.1f}% WR")
        
        comparison.append("")
        comparison.append("💡 STRATEGIC INSIGHTS:")
        comparison.append("-" * 80)
        
        if "error" not in report1 and "error" not in report2:
            # Compare win rates
            if report1['overall_stats']['win_rate'] > report2['overall_stats']['win_rate']:
                comparison.append(f"• {report1['team_name']} has better recent form ({report1['overall_stats']['win_rate']:.1f}% vs {report2['overall_stats']['win_rate']:.1f}%)")
            else:
                comparison.append(f"• {report2['team_name']} has better recent form ({report2['overall_stats']['win_rate']:.1f}% vs {report1['overall_stats']['win_rate']:.1f}%)")
            
            # Compare champion pools
            champs1 = set(report1['top_champions'].keys())
            champs2 = set(report2['top_champions'].keys())
            overlap = champs1 & champs2
            if overlap:
                comparison.append(f"• Both teams share {len(overlap)} common champions in their top picks")
        
        return [
            types.TextContent(
                type="text",
                text="\n".join(comparison)
            )
        ]
    
    else:
        return [
            types.TextContent(
                type="text",
                text=f"❌ Unknown tool: {name}"
            )
        ]

async def main():
    """Run the MCP server."""
    # Use stdio transport for MCP
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    # Check if mcp package is available
    try:
        import mcp
    except ImportError:
        print("❌ MCP package not found. Installing...")
        print("Run: pip install mcp")
        print("\nFor development, you can also use the scouting_report.py script directly:")
        print("  python3 scripts/scouting_report.py <team_id>")
        sys.exit(1)
    
    asyncio.run(main())

