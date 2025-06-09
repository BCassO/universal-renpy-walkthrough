# Installation Guide

## Quick Installation (Recommended)

### Step 1: Download
- Download [`__urw.rpy`](__urw.rpy) from [releases](../../releases/latest)
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
- Copy `__urw.rpy` into the `game/` folder
- The file should be alongside other `.rpy`, `.rpyc`, or `.rpa` files

### Step 4: Verify Installation
1. **Launch your game**
2. **Press Alt+W** - you should see a settings screen
3. **Enable walkthrough** if not already on
4. **Make a choice** - you should see consequence hints

## Troubleshooting

### "Alt+W doesn't work"
**Solutions:**
- Ensure `__urw.rpy` is in the `game/` folder (not main game folder)
- Restart the game completely
- File must be named exactly `__urw.rpy` (with double underscores)

### "No walkthrough hints appear"
**Debug Steps:**
1. Open `__urw.rpy` in a text editor (Notepad++, VS Code, etc.)
2. Find line 38: `debug = False`
3. Change to: `debug = True`
4. Save and restart game
5. Press **Shift+O** in-game to open console
6. Check for error messages

### "Game crashes after installing"
**Solutions:**
- Remove other walkthrough mods (conflicts)
- Temporarily remove `__urw.rpy` to test
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
Edit these settings in `__urw.rpy`:
```python
# Line 38 - Enable debug output
debug = True

# Default text size (12-40)
persistent.universal_wt_text_size = 25

# Cache size (50-500)
MAX_CONSEQUENCE_CACHE = 200
```

### For Developers
**Integration into your Ren'Py project:**
1. Add `__urw.rpy` to your `game/` folder
2. No code changes needed - auto-detects menus
3. Distributable with your game

## Uninstalling

1. Navigate to `game/` folder
2. Delete `__urw.rpy`
3. Restart game

**Note:** Save games are not affected.

## Getting Help

- 🐛 **Bug Reports:** [GitHub Issues](../../issues)
- 💬 **Questions:** [GitHub Discussions](../../discussions)  
- 📖 **Main Documentation:** [README.md](README.md)

---

[← Back to main documentation](README.md)