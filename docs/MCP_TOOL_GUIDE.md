# MCP Tool Guide - Pre-Game Scouting Reports

This guide explains how to set up and use the MCP (Model Context Protocol) server for generating pre-game scouting reports using the GRID API.

## What is MCP?

MCP (Model Context Protocol) is a protocol that allows AI assistants to access external tools and data sources. Our MCP server exposes tools for generating scouting reports and match analysis.

## Installation

### 1. Install MCP Package

```bash
pip install mcp
```

Or add to your `requirements.txt`:
```
mcp
```

### 2. Verify Setup

The MCP server requires:
- Python 3.7+
- Access to GRID API (API key)
- The scouting report module (`scripts/scouting_report.py`)

## Available Tools

The MCP server exposes three main tools:

### 1. `generate_scouting_report`

Generate a comprehensive pre-game scouting report for a team.

**Parameters:**
- `team_id` (required): GRID API team ID
- `team_name` (optional): Team name for display
- `days` (optional): Number of days to look back (default: 30)

**Example Usage:**
```python
# In an MCP client
result = await client.call_tool(
    "generate_scouting_report",
    {
        "team_id": "47494",
        "team_name": "T1",
        "days": 30
    }
)
```

**Output:**
- Overall win rate and record
- Top champions with usage and win rates
- Player performance statistics
- Map performance breakdown
- Recent series history

### 2. `get_series_analysis`

Get detailed analysis of a specific match series.

**Parameters:**
- `series_id` (required): GRID API series ID

**Example Usage:**
```python
result = await client.call_tool(
    "get_series_analysis",
    {
        "series_id": "2616372"
    }
)
```

**Output:**
- Series overview (format, status, date)
- Team statistics
- Game-by-game breakdown
- Player performance per game
- Champion selections

### 3. `get_pre_game_analysis`

Compare two teams head-to-head with strategic insights.

**Parameters:**
- `team1_id` (required): First team ID
- `team2_id` (required): Second team ID
- `team1_name` (optional): First team name
- `team2_name` (optional): Second team name
- `days` (optional): Analysis period in days (default: 30)

**Example Usage:**
```python
result = await client.call_tool(
    "get_pre_game_analysis",
    {
        "team1_id": "47494",
        "team2_id": "47558",
        "team1_name": "T1",
        "team2_name": "Gen.G",
        "days": 30
    }
)
```

**Output:**
- Side-by-side team comparison
- Win rate comparison
- Champion pool overlap
- Strategic insights

## Running the MCP Server

### Standalone Mode

The MCP server can be run directly, but it's designed to work with MCP clients:

```bash
python3 mcp_server.py
```

### With MCP Client

Most MCP implementations use stdio transport. The server is configured to work with:

- Claude Desktop (Anthropic)
- Other MCP-compatible clients

### Configuration

The server automatically reads the API key from:
1. `.env` file (`GRID_API_KEY`)
2. Environment variable (`GRID_API_KEY`)
3. Can be passed programmatically

## Using Without MCP

If you don't need MCP integration, you can use the scouting report module directly:

```bash
# Generate a scouting report
python3 scripts/scouting_report.py 47494 T1 30

# Save as JSON
python3 scripts/scouting_report.py 47494 T1 30 --save-json
```

## Example Output

```
================================================================================
📊 PRE-GAME SCOUTING REPORT: T1
================================================================================

Team ID: 47494
Analysis Period: Last 30 days
Series Analyzed: 15

📈 OVERALL PERFORMANCE
--------------------------------------------------------------------------------
Win Rate: 66.7% (10W-5L)

🎮 TOP CHAMPIONS (by usage)
--------------------------------------------------------------------------------
  Azir                  | Games:  8 | Win Rate:  75.0% | KDA: 3.45
  Varus                 | Games:  7 | Win Rate:  71.4% | KDA: 4.12
  ...

👥 PLAYER PERFORMANCE
--------------------------------------------------------------------------------
  Player ID 20763:
    Series: 15 | Win Rate: 66.7% | KDA: 3.21
    Top Champion: Azir
  ...

🗺️  MAP PERFORMANCE
--------------------------------------------------------------------------------
  Summoner's Rift       | 12W-3L | Win Rate: 80.0%

📅 RECENT SERIES
--------------------------------------------------------------------------------
  ✅ vs Gen.G Esports    | 2-1          | 2024-01-17T10:59:00Z
  ❌ vs DRX              | 1-2          | 2024-01-15T08:30:00Z
  ...
```

## Troubleshooting

### "MCP package not found"
```bash
pip install mcp
```

### "No recent series found"
- Check that the team ID is correct
- Try increasing the `days` parameter
- Verify the team has played matches in the specified period

### API Key Issues
- Ensure your API key is set in `.env` or environment variable
- Verify the key is valid and has access to the GRID API

## Integration Examples

### With Claude Desktop

Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "grid-scouting": {
      "command": "python3",
      "args": ["/path/to/mcp_server.py"]
    }
  }
}
```

### With Custom MCP Client

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="python3",
        args=["mcp_server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {[t.name for t in tools.tools]}")
            
            # Call a tool
            result = await session.call_tool(
                "generate_scouting_report",
                {"team_id": "47494", "days": 30}
            )
            print(result.content[0].text)

asyncio.run(main())
```

## Next Steps

- See `docs/DASHBOARD_GUIDE.md` for the interactive dashboard
- See `scripts/scouting_report.py` for direct script usage
- See `docs/HACKATHON_API_GUIDE.md` for API documentation

