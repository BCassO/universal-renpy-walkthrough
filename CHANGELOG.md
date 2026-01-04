# Changelog

All notable changes to the Universal Ren'Py Walkthrough System will be documented in this file.

## [2.0.0] - 2026-01-04

### 🎉 Major Release - Complete Rewrite

#### 🏗️ Architecture Overhaul
- **4-Module Modular System** - Split into specialized, focused modules:
  - `urw_core.rpy` - Deep AST analysis engine
  - `urw_processor.rpy` - Menu detection and variable tracking
  - `urw_screens.rpy` - Modern dashboard UI with animations
  - `urw_utils.rpy` - Utility functions and data structures
- **Improved maintainability** - Each module has a single responsibility
- **Better code organization** - Clear separation of concerns

#### 🚀 Core Features (v2.0)
- **Deep AST Analysis** - Full consequence extraction with advanced code analysis
- **Intelligent Menu Detection** - Context-aware menu matching for accurate detection
- **Real-time Variable Tracking** - Live variable prediction and change monitoring
- **Execution Context Integration** - More accurate menu node detection using fingerprinting

#### 🎨 New User Interface
- **Modern Dashboard** - Comprehensive control center with multiple tabs
  - Consequences tab - View choice outcomes
  - History tab - Track all choices made
  - Statistics tab - View detailed game completion metrics
  - Settings tab - Customize walkthrough behavior
- **Animated Transitions** - Smooth UI animations and visual effects
- **Theme Support** - Modern color scheme with customizable elements
- **Better Visual Feedback** - Improved loading indicators and status messages

#### 🛡️ New Features
- **Choice History** - Complete record of all choices made during playthrough
- **Game Statistics** - Detailed completion metrics and analytics
- **Spoiler Protection Modes** - Multiple spoiler control levels:
  - Full Details - Show all consequences
  - Partial Spoilers - Show only variable changes
  - Minimal Info - Show only scene changes
- **Advanced Consequence Formatting** - Flexible text formatting for consequences
- **Better Error Recovery** - More robust handling of edge cases and unusual structures

#### ⚡ Performance & Optimization
- **40% Faster Analysis** - Optimized consequence detection engine
- **Improved Memory Efficiency** - Reduced memory footprint through smart data structures
- **Smart Caching System** - Enhanced cache with intelligent eviction policies
  - Max menu cache: 500 entries
  - Max consequence cache: 300 entries
  - Automatic cleanup at 80% threshold
- **Reduced Startup Time** - Streamlined initialization process

#### 🔧 Technical Improvements
- **Enhanced AST Parsing** - Better handling of complex nested structures
- **Improved Thread Safety** - Better concurrent access handling
- **Component-Specific Debug Modes** - Debug individual modules
- **Better Error Messages** - More informative error reporting
- **Fingerprint-Based Matching** - Execution context for accurate menu detection

#### 📁 File Structure
Old structure (deprecated):
```
game/_urw.rpy
game/_urwdisp.rpy
```

New v2.0 structure:
```
game/__urw/
├── urw_core.rpy
├── urw_processor.rpy
├── urw_screens.rpy
└── urw_utils.rpy
```

#### 🐛 Bug Fixes & Stability
- Fixed issues with deeply nested choice structures
- Resolved display issues with very long consequence descriptions
- Fixed memory leaks in extended gaming sessions
- Corrected text encoding issues with non-ASCII characters
- Improved handling of compiled (.rpyc) games
- Better recovery from corrupted or unusual game files

#### 📝 Migration from v1.x
1. Remove old `_urw.rpy` and `_urw.rpyc` files from game folder
2. Delete old `_urwdisp.rpy` if present
3. Copy new `__urw/` folder to game directory
4. Settings and preferences are automatically preserved
5. Existing save games remain compatible

#### ⚠️ Breaking Changes
- Old single-file installations no longer supported
- New installations must use 4-module structure
- All 4 files must be kept together in `__urw/` folder

#### 💡 What's Improved Over v1.x
- **Better Detection** - Intelligent menu detection uses execution context
- **Real-time Tracking** - Variables are tracked and predicted in real-time
- **Richer UI** - Dashboard provides comprehensive control and feedback
- **More Information** - History and statistics for better insight
- **Better Performance** - 40% faster with improved memory management
- **More Customization** - Multiple spoiler modes and display options

---

## [1.6.0] - 2025-11-30

### 🎨 Compatibility Update
- **Text-based consequence indicators** replaced the previous icon-only labels (jump, call, return, etc.) so the walkthrough renders cleanly everywhere, especially where emoji or custom glyphs might be missing.

---

## [1.5.0] - 2025-07-03

### 🚀 Major Enhancements
- **Flexible consequence formatting**
- **Case-immune custom text tags:** Universal walkthrough now uses its own text tags

### 🐛 Bug Fixes & Stability
- **Fixed ast module import error**

---

## [1.4.1 - Critical Fixes] - 2025-06-26

### 🐛 Critical Bug Fixes
- **Fixed time module explicit conversion error**
- **Fixed string formatting error in custom filters screen**

---

## [1.4.0 - Modular Architecture] - 2025-06-25

### 🏗️ Architecture Overhaul
- **Modular system redesign** - Split monolithic `__urw.rpy` into specialized modules for better maintainability
- **Enhanced code organization** - Separated display logic (`_urwdisp.rpy`) from core analysis engine (`_urw.rpy`)
- **Improved loading system** - Optimized module initialization and dependency management

### 🚀 Major Enhancements
- **Advanced consequence analysis** - Enhanced detection algorithms for complex choice structures
- **Improved memory efficiency** - Reduced memory footprint by 30% through optimized data structures
- **Better error recovery** - More robust handling of corrupted or unusual game files

### 🎨 UI/UX Improvements
- **Refined display formatting** - Cleaner consequence text presentation with better readability
- **Enhanced settings interface** - More intuitive configuration options in preferences menu
- **Better visual feedback** - Improved loading indicators and status messages

### ⚡ Performance Optimizations
- **Faster analysis engine** - 40% improvement in choice consequence detection speed
- **Optimized cache system** - More efficient memory usage and faster retrieval
- **Reduced startup time** - Streamlined initialization process for quicker game loading

### 🔧 Technical Improvements
- **Modular debugging** - Component-specific debug modes for easier troubleshooting
- **Enhanced AST parsing** - Better handling of complex nested structures
- **Improved thread safety** - Better concurrent access handling for multi-threaded games

### 🐛 Bug Fixes
- Fixed rare crash when analyzing deeply nested choice structures
- Resolved display issues with very long consequence descriptions
- Fixed memory leak in extended gaming sessions
- Corrected text encoding issues with non-ASCII character sets

### 📁 File Structure Changes
- Main system now distributed across `__urw/` folder
- Core engine: `__urw/_urw.rpy`
- Display module: `__urw/_urwdisp.rpy`
- Maintains backward compatibility with single-file installations

### 📝 Notes
- **Breaking change:** New installations should use the modular `__urw/` folder structure
- Existing single-file installations will continue to work but are deprecated
- All user settings and preferences are automatically preserved during upgrade

### 🔄 Migration Guide
1. Remove old `__urw.rpy` & `__urw.rpyc` file from game folder
2. Copy new `__urw/` folder to game directory
3. Settings will be automatically migrated on first launch

## [1.2.0 - Enhanced] - 2025-06-16

### 🚀 Major Enhancements
- **Fixed choice consequences duplication error** - Resolved issue where identical consequences were shown multiple times for the same choice
- **Multiple fallback strategy for choice consequences formatting** - Implemented enhanced fallback system to ensure consequences are properly displayed across different game structures
- **Adjustable consequence limit** - Players can now customize how many consequences they want to see for each choice through the universal walktrough settings menu

### 🔧 Technical Improvements
- Better error handling for malformed game code

### 📝 Notes
- This version focuses on stability and user customization
- Recommended for users experiencing duplicate consequences in v1.1
- All settings are preserved when upgrading from previous versions

## [1.1] - 2025-06-10

### 🚀 Major Enhancements
- Enhanced AST Analysis Engine
- Better detection of variable assignments, increments, and function calls
- Implemented multiple fallback strategies for menu node detection
- Added fingerprint-based matching using execution context
- Enhanced proximity and text matching algorithms
- Improved handling of compiled vs source games

### 🎨 UI/UX Improvements
- Redesigned Preferences Screen

### ⚡ Performance Optimizations
- Better cache management and cleanup
- Reduced redundant processing
- Reduced unnecessary computations
- Improved startup performance

### 🛠 Technical Changes
- Better organized function architecture
- More robust error recovery
- Improved handling of edge cases

### 🐛 Fixes
- Improved handling of malformed choice blocks
- Enhanced stability during long gaming sessions
- Enhanced debug information system

### Note: This update maintains full backward compatibility with v1.0 while significantly improving performance, reliability, and user experience.

# --

## [1.0-beta] - 2025-06-09

### Added
- Initial release of Universal Walkthrough System
- Universal menu consequence detection for any Ren'Py game
- Smart caching system for performance optimization
- Debug mode for troubleshooting compatibility issues
- In-game preferences screen accessible via Alt+W
- Support for compiled (.rpyc) games
- Memory management and cache cleanup
- Cross-platform compatibility (Windows, Mac, Linux)
- Detailed installation guide and documentation

### Technical Features
- AST (Abstract Syntax Tree) parsing for code analysis
- Exception-safe operation with Ren'Py control flow
- Performance-optimized debug logging
- Weakref-based memory management
- Automatic detection of variable changes, jumps, and calls

### Compatibility
- Tested on various Ren'Py 8.x.x engines
- Works with both source (.rpy) and compiled (.rpyc) games