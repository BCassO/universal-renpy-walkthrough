# Universal Ren'Py Walkthrough System

[![Ren'Py](https://img.shields.io/badge/Ren'Py-8.x.x-blue)](https://www.renpy.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![GitHub release](https://img.shields.io/github/v/release/BCassO/universal-renpy-walkthrough)](../../releases/latest)

A universal walkthrough mod that automatically shows choice consequences for **ANY** Ren'Py game - no manual setup required! Now with enhanced AST analysis, intelligent menu detection, real-time variable tracking, and modern UI features.

## ✨ Features

### Core Walkthrough
- 🎯 **Universal Compatibility**
- 🔍 **Deep AST Analysis**
- 💾 **Compiled Game Support**
- 🚀 **Intelligent Menu Detection**
- ⚡ **Real-time Variable Tracking**

## 🚀 Quick Start

1. **Download:** Grab the latest [`__urw` folder](__urw) from [releases](../../releases/latest). Contains all urw modules.
2. **Install:** Copy the `__urw` folder into your game's `game/` directory. This keeps all walkthrough scripts organized in one place.
3. **Play:** Launch the game and press `Alt+W` to access the full walkthrough dashboard with settings, statistics, and more!

📖 **Need help?** See the [detailed installation guide](installation.md)

## 📸 Screenshots

![Preview 1](screenshots/capture_1.png)
<!-- ![Preview 2](screenshots/capture_2.png) -->

### Before (Normal Menu):
```
What should I do?
> Talk to Sarah
> Go to class
> Skip school
```

### After (With Walkthrough):
```
What should I do?
> Talk to Sarah          [+love_sarah, +trust]
> Go to class           [+grades, +reputation] 
> Skip school           [-reputation, jump party_scene]
```

## 🎮 Compatibility

### ✅ Tested & Working:
- **Ren'Py 8.x.x** engines (latest versions)
- **Compiled games** (.rpyc files)
- **Windows, Mac, Linux**

### 📝 Tested Games:
Help us expand this list! [Report compatibility](../../issues/new?template=compatibility_report.md)

| Game | Version | Status | Notes |
|------|---------|--------|-------|
| *Your game here* | | | [Test and report!](../../issues/new) |

## ⚙️ Usage

### Controls:
- **Alt+W** - Open walkthrough dashboard with settings, history, and statistics
- **Dashboard Tabs** - Switch between Consequences, History, Statistics, and Settings
- Settings also available in game preferences

### What You'll See:
- **Variable changes:** `[+love_sarah, -trust_john]`
- **Scene jumps:** `[→ party_scene]`
- **Function calls:** `[call morning_routine]`
- **Conditional outcomes:** `[if money >= 100: +expensive_date]`

## 🐛 Troubleshooting

📖 **Full troubleshooting:** See [installation guide](installation.md#troubleshooting)

## 🛠️ Development

### URW Architecture:
1. **Core Engine** (`urw_core.rpy`) - Deep AST analysis and consequence extraction
2. **Processor** (`urw_processor.rpy`) - Menu detection and real-time variable tracking
3. **Utils** (`urw_utils.rpy`) - Helper functions and data structures
4. **UI System** (`urw_screens.rpy`) - Modern dashboard interface with animations

### How It Works:
1. **Intelligent Menu Interception** - Uses execution context for accurate menu detection
2. **Deep AST Analysis** - Parses choice destinations for comprehensive consequence extraction
3. **Real-time Tracking** - Monitors variable changes and predicts outcomes
4. **Smart Caching** - Stores analysis results with intelligent cache management
5. **Modern Dashboard** - Displays results with animations, themes, and interactive controls

### Contributing:
We welcome contributions!

[View full changelog](CHANGELOG.md)

## 🏗️ What's New in v2.0

### Complete Rewrite
- **Modular Architecture** - Organized into specialized modules for better maintainability
- **Deep AST Analysis** - Full consequence extraction with advanced code analysis
- **Intelligent Menu Detection** - Context-aware menu matching for accurate detection
- **Real-time Variable Tracking** - Live variable prediction and change monitoring

### New User Features
- **Dashboard Interface** - Comprehensive control center with multiple tabs
- **Choice History** - Track and review all choices made in your playthrough
- **Statistics Panel** - Detailed game completion metrics and analytics
- **Spoiler Protection** - Multiple spoiler control modes for personalized experience
- **Modern UI** - Animated interface with theme support and better visual design

### Performance & Stability
- **40% Faster** - Optimized analysis engine for quicker consequence detection
- **Better Memory Management** - Improved efficiency reducing memory footprint
- **Enhanced Error Recovery** - More robust handling of edge cases
- **Multi-threaded Support** - Better handling for concurrent operations
- [ ] Custom styling options
- [ ] Save/load walkthrough preferences

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Ren'Py Team** - For the amazing visual novel engine
- **Community** - For testing and feedback
- **Game Developers** - For creating great Ren'Py games

## 🌟 Support the Project

If this mod helped enhance your gaming experience:
- ⭐ **Star this repository**
- ⭐ **Watch** for updates
- 🐛 **Report bugs** to help improve it
- 💬 **Share** with other Ren'Py players
- 🔧 **Contribute** code or documentation

---

**Made with ❤️ for the Ren'Py community**

*Universal compatibility • Works with compiled games*