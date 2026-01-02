# Simple Guide - No Claude/MCP Needed!

**You don't need Claude Desktop or MCP!** Here are the easy ways to use the tools:

## 🎯 Option 1: Use the Dashboard (Easiest!)

The dashboard is a web interface - no coding needed!

```bash
# Install (one time)
pip install streamlit pandas plotly

# Run the dashboard
streamlit run dashboard.py
```

Then:
1. Open the browser (it opens automatically)
2. Enter your API key in the sidebar (or set in `.env` file)
3. Go to **"Match Analysis"** tab
4. Enter a Series ID like `2616372`
5. Click "Analyze Match"

**That's it!** You'll see:
- Match overview
- Team stats
- Game-by-game breakdown
- Player performance
- Charts and visualizations

## 🎯 Option 2: Use Known Series IDs Directly

Instead of searching by team ID, use Series IDs we already know work:

```bash
# Analyze a specific match
python3 scripts/series_state_api.py 2616372
```

This shows you:
- Match results
- Team performance
- Player stats
- Game breakdowns

**Known Series IDs that work:**
- `2616372` - T1 vs Gen.G Esports (LoL)
- `2616371` - NONGSHIM RED FORCE vs DRX (LoL)
- `2654004` - 100 Thieves vs G2 Esports (Valorant)

See `notes/series_ids.md` for more!

## 🎯 Option 3: Scouting Report from Series IDs (Works!)

If team ID search doesn't work, use this alternative that analyzes specific series:

```bash
# Analyze specific matches for a team
python3 scripts/scouting_from_series.py "T1" 2616372 2616371

# This will:
# - Find T1 in those matches
# - Analyze their performance
# - Show champion usage, win rates, etc.
```

**This always works** because it uses Series IDs we know exist!

## ❓ What is the "JSON step"?

The `--save-json` flag is **completely optional**. It just saves the data to a file:

```bash
# Without JSON (just shows on screen)
python3 scripts/series_state_api.py 2616372

# With JSON (saves to file - optional!)
python3 scripts/series_state_api.py 2616372 --save-json
```

The JSON file is just the raw data - you don't need it unless you want to:
- Analyze the data in another program
- Keep a record of the data
- Process it with other tools

**You can ignore it completely!**

## 🚀 Recommended Workflow

### For Match Analysis:
1. **Use the Dashboard** - Easiest and most visual
   ```bash
   streamlit run dashboard.py
   ```

### For Quick Stats:
2. **Use Series IDs directly**
   ```bash
   python3 scripts/series_state_api.py 2616372
   ```

### For Team Scouting:
3. **Use the Dashboard's "Team Scouting" tab**
   - Or try the scouting script with more days:
   ```bash
   python3 scripts/scouting_report.py 47494 T1 90
   ```

## 🔍 Why "No recent series found"?

This happens because:
1. **The team might not have played in the last 30 days**
   - Solution: Increase days to 60 or 90
   
2. **The team ID might be wrong**
   - Solution: Use Series IDs directly instead
   
3. **The API might not have data for that team**
   - Solution: Use known Series IDs from `notes/series_ids.md`

## 💡 Quick Tips

1. **Start with the Dashboard** - It's the easiest way
2. **Use known Series IDs** - They're guaranteed to work
3. **The JSON step is optional** - You can ignore it
4. **You don't need Claude/MCP** - The dashboard and scripts work fine on their own

## 📊 What Each Tool Does

| Tool | What It Does | When to Use |
|------|--------------|-------------|
| **Dashboard** | Web interface with charts | Best for visual analysis |
| **series_state_api.py** | Shows match stats | Quick match lookup |
| **scouting_report.py** | Team analysis report | Pre-game scouting (if team ID works) |

## 🎮 Example: Analyze T1 vs Gen.G Match

```bash
# Method 1: Dashboard (recommended)
streamlit run dashboard.py
# Then enter: 2616372 in Match Analysis tab

# Method 2: Command line
python3 scripts/series_state_api.py 2616372
```

Both show the same data - dashboard is just prettier! 😊

## ❓ Still Having Issues?

1. **Check your API key** - Make sure it's in `.env` file
2. **Try the dashboard** - It's more user-friendly
3. **Use known Series IDs** - They always work
4. **Check the error messages** - They'll tell you what's wrong

## 🎉 You're All Set!

Remember:
- ✅ Dashboard = Easiest way (no coding)
- ✅ Series IDs = Guaranteed to work
- ✅ JSON = Optional (you can ignore it)
- ✅ No Claude/MCP needed!

Happy analyzing! 🎮

