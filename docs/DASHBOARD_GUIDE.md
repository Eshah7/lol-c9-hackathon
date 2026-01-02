# Interactive Dashboard Guide

This guide explains how to set up and use the interactive Streamlit dashboard for visualizing League of Legends match data from the GRID API.

## Overview

The dashboard provides three main views:
1. **Match Analysis** - Analyze individual match series
2. **Team Scouting** - Generate comprehensive team scouting reports
3. **Player Stats** - View player performance statistics

## Installation

### 1. Install Required Packages

```bash
pip install streamlit pandas plotly
```

Or add to your `requirements.txt`:
```
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.17.0
```

### 2. Verify Setup

Ensure you have:
- Python 3.7+
- GRID API key (in `.env` file or environment variable)
- Access to the GRID API

## Running the Dashboard

### Start the Dashboard

```bash
streamlit run dashboard.py
```

The dashboard will open in your default web browser at `http://localhost:8501`

### Command Line Options

```bash
# Run on a specific port
streamlit run dashboard.py --server.port 8502

# Run without opening browser
streamlit run dashboard.py --server.headless true
```

## Features

### 1. Match Analysis Page

**Purpose:** Analyze individual match series in detail.

**How to Use:**
1. Enter a Series ID (e.g., `2616372`)
2. Click "Analyze Match"
3. View:
   - Series overview (format, status, date)
   - Team statistics and player performance
   - Game-by-game breakdown with visualizations
   - Champion selections per game

**Features:**
- Interactive score charts
- Player performance tables
- Game-by-game expandable sections
- Champion information

**Example Series IDs:**
- `2616372` - T1 vs Gen.G Esports
- `2616371` - NONGSHIM RED FORCE vs DRX
- See `notes/series_ids.md` for more

### 2. Team Scouting Page

**Purpose:** Generate comprehensive pre-game scouting reports.

**How to Use:**
1. Enter a Team ID (e.g., `47494` for T1)
2. Optionally enter team name
3. Set analysis period (7-90 days)
4. Click "Generate Scouting Report"

**Features:**
- Overall win rate and record
- Top champions with usage statistics
- Champion usage charts
- Map performance breakdown
- Recent series history
- Interactive visualizations

**Example Team IDs:**
- `47494` - T1
- `47558` - Gen.G Esports
- Use the Central Data API to find more team IDs

### 3. Player Stats Page

**Purpose:** View individual player performance (coming soon).

Currently shows player stats from specific matches. Future enhancements will include:
- Player career statistics
- Performance trends over time
- Champion-specific performance
- Head-to-head player comparisons

## Configuration

### API Key Setup

The dashboard reads your API key from:

1. **Sidebar Input** (temporary, session-only)
2. **`.env` file** (recommended)
   ```bash
   GRID_API_KEY=your-api-key-here
   ```
3. **Environment Variable**
   ```bash
   export GRID_API_KEY='your-api-key-here'
   ```

### Customization

You can customize the dashboard by editing `dashboard.py`:

- **Colors:** Modify the Plotly color schemes
- **Layout:** Adjust column widths and sections
- **Metrics:** Add or remove displayed statistics
- **Charts:** Customize chart types and styling

## Screenshots & Features

### Match Analysis View

- **Series Overview Cards:** Quick stats at a glance
- **Team Comparison:** Side-by-side team statistics
- **Game Breakdown:** Expandable sections for each game
- **Score Visualizations:** Interactive bar charts
- **Player Tables:** Sortable performance data

### Team Scouting View

- **Win Rate Metrics:** Overall performance indicators
- **Champion Usage Chart:** Visual representation of top picks
- **Map Performance Table:** Win rates by map
- **Recent Series Timeline:** Match history with results

## Troubleshooting

### Dashboard Won't Start

**Error:** `streamlit: command not found`
```bash
pip install streamlit
```

**Error:** `ModuleNotFoundError`
```bash
pip install -r requirements.txt
```

### No Data Displayed

- **Check API Key:** Verify it's set correctly in sidebar or `.env`
- **Verify Series/Team ID:** Ensure the ID exists in GRID API
- **Check Network:** Ensure you can reach the GRID API endpoints

### Charts Not Rendering

- **Clear Browser Cache:** Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
- **Check Browser Console:** Look for JavaScript errors
- **Update Plotly:** `pip install --upgrade plotly`

### Performance Issues

- **Reduce Analysis Period:** Use fewer days in scouting reports
- **Limit Series Analyzed:** The scouting report analyzes up to 20 series by default
- **Clear Session State:** Use the sidebar "Clear Cache" option

## Advanced Usage

### Custom Analysis

You can extend the dashboard by:

1. **Adding New Pages:**
   ```python
   elif page == "Custom Analysis":
       st.title("Custom Analysis")
       # Your custom code
   ```

2. **Creating Custom Charts:**
   ```python
   import plotly.graph_objects as go
   fig = go.Figure(...)
   st.plotly_chart(fig)
   ```

3. **Integrating Additional Data:**
   - Add file download API integration
   - Include event-by-event analysis
   - Add draft phase analysis

### Deployment

#### Local Network Access

```bash
streamlit run dashboard.py --server.address 0.0.0.0
```

Access from other devices on your network at `http://your-ip:8501`

#### Cloud Deployment

**Streamlit Cloud:**
1. Push code to GitHub
2. Connect to Streamlit Cloud
3. Set environment variables (API key)
4. Deploy

**Other Platforms:**
- Heroku
- AWS EC2
- Google Cloud Run
- Docker container

## Example Workflows

### Pre-Game Preparation

1. Navigate to "Team Scouting"
2. Enter opponent team ID
3. Review champion pool and map performance
4. Check recent series for patterns
5. Use insights for draft strategy

### Post-Game Analysis

1. Navigate to "Match Analysis"
2. Enter series ID from completed match
3. Review game-by-game breakdown
4. Analyze player performance
5. Identify key moments and decisions

### Player Evaluation

1. Navigate to "Match Analysis"
2. Enter series ID
3. Review player performance tables
4. Compare KDA and champion performance
5. Use for roster decisions

## Next Steps

- See `docs/MCP_TOOL_GUIDE.md` for MCP tool integration
- See `scripts/scouting_report.py` for command-line usage
- See `docs/HACKATHON_API_GUIDE.md` for API documentation
- See `README.md` for project overview

## Tips & Best Practices

1. **Bookmark Common Series/Teams:** Keep a list of frequently analyzed IDs
2. **Use Multiple Time Periods:** Compare 7-day vs 30-day performance
3. **Export Data:** Use the JSON export features for further analysis
4. **Combine with Other Tools:** Use MCP tools for automated reporting
5. **Regular Updates:** Refresh data regularly for up-to-date insights

