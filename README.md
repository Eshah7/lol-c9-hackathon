# League of Legends C9 Hackathon Project

Tools and documentation for interacting with Grid.gg APIs for the Cloud9 x JetBrains Hackathon.

## 📁 Project Structure

```
.
├── README.md                 # This file
├── dashboard.py              # Interactive Streamlit dashboard
├── requirements.txt         # Python dependencies
├── env.example              # Environment variable template
├── docs/                    # All documentation
│   ├── HACKATHON_API_GUIDE.md          # ⭐ Start here - Complete API guide
│   ├── SIMPLE_GUIDE.md                 # Easy guide for non-coders
│   ├── QUICKSTART_MCP_DASHBOARD.md     # Quick start for dashboard & MCP
│   ├── SCOUTING_AND_DASHBOARD_SUMMARY.md # Summary of implementation
│   ├── HACKATHON_CATEGORY_ANALYSIS.md   # Data analysis for each category
│   ├── CATEGORY_DATA_MAPPING.md        # Detailed examples with code
│   ├── DATA_AVAILABILITY_SUMMARY.md    # Quick reference
│   ├── CENTRAL_DATA_API_REFERENCE.md   # Complete Central Data API reference
│   ├── API_DOCUMENTATION.md            # Central Data API quick start
│   ├── SERIES_STATE_API_DOCS.md        # Series State API docs
│   ├── FILE_DOWNLOAD_API_DOCS.md       # File Download API docs
│   ├── QUICKSTART.md                   # Quick start guide
│   └── API_DISCOVERY.md                # Initial API exploration results
├── scripts/                 # Python scripts
│   ├── mcp_server.py                # MCP server for AI assistants
│   ├── scouting_report.py           # Team scouting reports
│   ├── scouting_from_series.py      # Scouting from specific series
│   ├── api_explorer.py              # Explore Central Data API
│   ├── series_state_api.py          # Query Series State API
│   ├── file_download_api.py         # Download event files
│   ├── data_explorer.py             # Comprehensive data exploration
│   ├── query_available_data.py      # Test available data
│   ├── get_valorant_series.py      # Get Valorant series IDs
│   └── utils.py                    # Shared utilities
├── data/                     # Downloaded data files
│   └── (event files, end states, etc.)
└── notes/                    # Notes and references
    └── series_ids.md         # Notable series IDs for testing
```

## 🚀 Quick Start

1. **Get your API key** from hackathon organizers
2. **Set up environment:**
   ```bash
   cp env.example .env
   # Edit .env and add your API key: GRID_API_KEY=your-key-here
   ```
3. **Run a script:**
   ```bash
   python3 scripts/api_explorer.py
   ```

See `docs/QUICKSTART.md` for detailed instructions.

## 📚 Documentation

### Getting Started
- **`docs/HACKATHON_API_GUIDE.md`** ⭐ **Start here!** Complete guide to all three APIs
- **`docs/QUICKSTART.md`** - Step-by-step quick start guide
- **`docs/SIMPLE_GUIDE.md`** - Easy guide for non-coders
- **`docs/QUICKSTART_MCP_DASHBOARD.md`** - Quick start for dashboard & MCP

### Scouting & Analysis
- **`docs/SCOUTING_AND_DASHBOARD_SUMMARY.md`** - Summary of implementation
- **`docs/DASHBOARD_GUIDE.md`** - Guide to using the interactive dashboard
- **`docs/MCP_TOOL_GUIDE.md`** - Guide to using the MCP tools

### Hackathon Categories
- **`docs/HACKATHON_CATEGORY_ANALYSIS.md`** - Data analysis for each category
- **`docs/CATEGORY_DATA_MAPPING.md`** - Detailed examples with code
- **`docs/DATA_AVAILABILITY_SUMMARY.md`** - Quick reference of available data

### API Documentation
- **`docs/CENTRAL_DATA_API_REFERENCE.md`** ⭐ Complete Central Data API reference
- **`docs/API_DOCUMENTATION.md`** - Central Data API quick start
- **`docs/SERIES_STATE_API_DOCS.md`** - Series State API documentation
- **`docs/FILE_DOWNLOAD_API_DOCS.md`** - File Download API documentation

## 🔧 Available Scripts

All scripts are in the `scripts/` directory:

1. **`api_explorer.py`** - Explore Central Data API, get Series IDs
   ```bash
   python3 scripts/api_explorer.py
   ```

2. **`series_state_api.py`** - Query Series State API for match stats
   ```bash
   python3 scripts/series_state_api.py [series-id]
   # API key read from .env automatically
   ```

3. **`file_download_api.py`** - Download event-by-event data files
   ```bash
   python3 scripts/file_download_api.py [series-id]
   # API key read from .env automatically
   ```

4. **`data_explorer.py`** - Comprehensive data exploration
   ```bash
   python3 scripts/data_explorer.py [api-key] [series-id]
   ```

5. **`get_valorant_series.py`** - Get random Valorant Americas series
   ```bash
   python3 scripts/get_valorant_series.py [api-key]
   ```

## 🎯 Available APIs

1. **Central Data API** - Get titles, tournaments, and Series IDs
   - Endpoint: `https://api-op.grid.gg/central-data/graphql`
   - Script: `scripts/api_explorer.py`
   - Docs: `docs/CENTRAL_DATA_API_REFERENCE.md`

2. **Series State API** - Get match results, player stats, draft actions
   - Endpoint: `https://api-op.grid.gg/live-data-feed/series-state/graphql`
   - Script: `scripts/series_state_api.py`
   - Docs: `docs/SERIES_STATE_API_DOCS.md`

3. **File Download API** - Download event-by-event data files
   - Endpoint: `https://api.grid.gg/file-download`
   - Script: `scripts/file_download_api.py`
   - Docs: `docs/FILE_DOWNLOAD_API_DOCS.md`

## 📝 Notes

- **Series IDs:** See `notes/series_ids.md` for notable series IDs for testing
- **Data Files:** Downloaded files are stored in `data/` directory

## 🔑 Authentication

All APIs use the `x-api-key` header. Scripts automatically read your API key from:

**Priority Order:**
1. **`.env` file** (project root) - **Recommended!** ⭐
2. Environment variable (`GRID_API_KEY`)
3. Command line argument (override/fallback)

**Setup:**
```bash
# Create .env file in project root
cp env.example .env

# Edit .env and add your key:
GRID_API_KEY=your-api-key-here
```

The `.env` file is gitignored and won't be committed. Once set up, you can run scripts without passing the API key:
```bash
python3 scripts/api_explorer.py
python3 scripts/series_state_api.py 2654004
```

## 📊 API Workflow

1. **Get Titles** → Find available games
2. **Get Tournaments** → Find tournaments for a title
3. **Get Series** → Get match IDs (Series IDs)
4. **Use Series IDs** → Access Series State API and File Download API

## 🎮 Example Series IDs

- **Valorant:** `2654004` (100 Thieves vs G2 Esports - VCT Americas)
- **League of Legends:** `2616372` (T1 vs Gen.G Esports)

See `notes/series_ids.md` for more.

## 📦 Dependencies

No external dependencies required - all scripts use Python standard library.

## 🔍 Discovery Results

✅ **APIs are working!** 
- 38+ game titles available
- 173+ League of Legends tournaments
- 18,594+ players in database
- Event-by-event data available for analysis

See `docs/API_DISCOVERY.md` for more details.
