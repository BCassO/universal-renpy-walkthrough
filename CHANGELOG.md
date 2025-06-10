# Changelog

All notable changes to the Universal Ren'Py Walkthrough System will be documented in this file.

## [Unreleased]

### Planned
- More detailed consequence analysis
- Localization support (multiple languages)
- Custom styling options
- Save/load walkthrough preferences


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