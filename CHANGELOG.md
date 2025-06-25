# Changelog

All notable changes to the Universal Ren'Py Walkthrough System will be documented in this file.

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