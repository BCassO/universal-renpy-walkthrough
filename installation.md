# Installation Guide

## Quick Installation (Recommended)

### Step 1: Download
- Download the folder [__urw](__urw) from [releases](../../releases/latest)
- Save to your Downloads folder

### Step 2: Find Your Game Folder
Navigate to your game's `game/` subfolder:

**Windows Examples:**
```
Steam: C:\Program Files (x86)\Steam\steamapps\common\[GameName]\game\
Itch.io: C:\Users\[Username]\AppData\Roaming\itch\apps\[GameName]\game\
Direct: [GameFolder]\game\
```

**Mac Examples:**
```
Applications: /Applications/[GameName].app/Contents/Resources/autorun/game/
Steam: ~/Library/Application Support/Steam/steamapps/common/[GameName]/game/
```

**Linux Examples:**
```
Steam: ~/.steam/steam/steamapps/common/[GameName]/game/
Local: ~/Games/[GameName]/game/
```

### Step 3: Install
- Copy the entire [__urw](__urw) folder into the `game/` directory. The folder contains 4 modular files that work together:
  - `urw_core.rpy` - Core analysis engine
  - `urw_processor.rpy` - Menu detection and variable tracking
  - `urw_screens.rpy` - Dashboard UI and display
  - `urw_utils.rpy` - Utility functions and helpers

The directory structure should look like:
```
game/__urw/
├── urw_core.rpy
├── urw_processor.rpy
├── urw_screens.rpy
└── urw_utils.rpy
```

Keeping all 4 files together in the `__urw/` folder is essential for proper functionality.

### Step 4: Verify Installation
1. **Launch your game**
2. **Press Alt+W** - you should see a settings screen
3. **Enable walkthrough** if not already on
4. **Make a choice** - you should see consequence hints

## Troubleshooting

### "Alt+W doesn't work"
**Solutions:**
- Ensure all 4 files (`urw_core.rpy`, `urw_processor.rpy`, `urw_screens.rpy`, `urw_utils.rpy`) are in the `game/__urw/` folder together
- Restart the game completely

### "No walkthrough hints appear"
**Debug Steps:**
1. Open `urw_core.rpy` in a text editor (Notepad++, VS Code, etc.)
2. Find `DEBUG = False` in the URWConfig section
3. Change to: `DEBUG = True`
4. Save and restart game
5. Press **Shift+O** in-game to open console
6. Check for error messages

### "Game crashes after installing"
**Solutions:**
- Remove other walkthrough mods (conflicts)
- Temporarily remove `__urw` folder to test
- Check if game works without any mods

### "Wrong consequence information"
**Report Issues:**
1. Enable debug mode (see above)
2. Take screenshots of incorrect info
3. [Submit bug report](../../issues/new) with:
   - Game name and version
   - Debug console output
   - Screenshots

## Advanced Options

### Custom Configuration
Edit these settings in `urw_core.rpy`:
```python
# In URWConfig class
DEBUG = True                          # Enable debug output
VERSION = "2.0.0"

# Cache settings
MAX_MENU_CACHE = 500
MAX_CONSEQUENCE_CACHE = 300

# Display settings
persistent.universal_wt_text_size = 25
```

## Uninstalling

1. Navigate to `game/` folder
2. Delete `__urw` folder
3. Restart game

**Note:** Save games are not affected.

## Getting Help

- 🐛 **Bug Reports:** [GitHub Issues](../../issues)
- 💬 **Questions:** [GitHub Discussions](../../discussions)  
- 📖 **Main Documentation:** [README.md](README.md)

---

[← Back to main documentation](README.md)