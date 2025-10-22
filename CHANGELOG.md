# Changelog

All notable changes to the Google Font Text Image Node for ComfyUI will be documented in this file.

## [2025-10-22]

### Added
- **Playwright Integration**: Migrated from html2image to Playwright for more reliable rendering
- **Automatic Dimension Calculation**: Added ability to set width or height to -1 for automatic sizing based on text content
- **Text Wrapping**: Implemented proper text wrapping when using fixed canvas dimensions
- **Individual Padding Controls**: Added separate controls for top, right, bottom, and left padding (0-200px range)
- **Enhanced Text Positioning**: Improved CSS layout with precise control over text positioning

### Changed
- Replaced `html2image` dependency with `playwright` for better rendering capabilities
- Updated HTML/CSS generation to support both auto-sizing and fixed-dimension layouts
- Modified width/height parameters to accept -1 for automatic sizing
- Improved font loading with explicit wait time for better reliability
- Enhanced dimension calculation logic to account for padding values in auto-sizing mode

### Fixed
- Text cutoff issues that were common with html2image
- Inability to automatically size images based on content
- Poor text wrapping behavior with long text strings
- Limited control over text positioning within the canvas

### Deprecated
- html2image rendering engine (replaced by Playwright)

## [2024-XX-XX] - Initial Release

### Added
- Initial release of the Google Font Text Image Node
- Support for Google Fonts API integration
- Basic text rendering with typographic controls
- Dual output modes (Custom Text and Standard Character Set)
- Transparent background support