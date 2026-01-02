# Quick Start: MCP Tool & Dashboard

Quick guide to get started with the MCP scouting tool and interactive dashboard.

## 🚀 Quick Start

### Option 1: Interactive Dashboard (Easiest)

1. **Install dependencies:**
   ```bash
   pip install streamlit pandas plotly
   ```

2. **Run the dashboard:**
   ```bash
   streamlit run dashboard.py
   ```

3. **Open in browser:** The dashboard will open at `http://localhost:8501`

4. **Enter API key** in the sidebar (or set in `.env` file)

5. **Start analyzing:**
   - **Match Analysis:** Enter a Series ID (e.g., `2616372`)
   - **Team Scouting:** Enter a Team ID (e.g., `47494` for T1)

### Option 2: MCP Tool (For AI Assistants)

1. **Install MCP package:**
   ```bash
   pip install mcp
   ```

2. **Configure MCP client** (e.g., Claude Desktop):
   ```json
   {
     "mcpServers": {
       "grid-scouting": {
         "command": "python3",
         "args": ["/path/to/scripts/mcp_server.py"]
       }
     }
   }
   ```

3. **Use in AI assistant:**
   - "Generate a scouting report for team 47494"
   - "Analyze series 2616372"
   - "Compare T1 and Gen.G"

### Option 3: Command Line (Direct Script)

1. **Generate scouting report:**
   ```bash
   python3 scripts/scouting_report.py 47494 T1 30
   ```

2. **Save as JSON:**
   ```bash
   python3 scripts/scouting_report.py 47494 T1 30 --save-json
   ```

## 📋 Example IDs

### Series IDs (for Match Analysis)
- `2616372` - T1 vs Gen.G Esports
- `2616371` - NONGSHIM RED FORCE vs DRX
- `2654004` - 100 Thieves vs G2 Esports (Valorant)

### Team IDs (for Scouting)
- `47494` - T1
- `47558` - Gen.G Esports

Find more in `notes/series_ids.md` or use the Central Data API.

## 📚 Full Documentation

- **Dashboard Guide:** `docs/DASHBOARD_GUIDE.md`
- **MCP Tool Guide:** `docs/MCP_TOOL_GUIDE.md`
- **API Documentation:** `docs/HACKATHON_API_GUIDE.md`

## 🔑 API Key Setup

Create a `.env` file in the project root:
```
GRID_API_KEY=your-api-key-here
```

Or set environment variable:
```bash
export GRID_API_KEY='your-api-key-here'
```

## 🎯 Use Cases

### Pre-Game Scouting
1. Open dashboard → Team Scouting
2. Enter opponent team ID
3. Review champion pool, map performance, recent form
4. Use insights for draft strategy

### Post-Game Analysis
1. Open dashboard → Match Analysis
2. Enter series ID
3. Review game-by-game breakdown
4. Analyze player performance and key moments

### Automated Reporting
1. Set up MCP tool
2. Ask AI assistant for scouting reports
3. Get formatted analysis automatically

## ⚡ Troubleshooting

**Dashboard won't start?**
```bash
pip install streamlit pandas plotly
```

**MCP not working?**
```bash
pip install mcp
```

**No data showing?**
- Check API key is set correctly
- Verify Series/Team ID exists
- Check network connection to GRID API

## 🎮 Next Steps

1. Explore the dashboard features
2. Generate scouting reports for your favorite teams
3. Integrate MCP tool with your AI assistant
4. Customize the dashboard for your needs

Happy analyzing! 🎯

