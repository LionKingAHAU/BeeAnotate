# Changelog

All notable changes to the Bee Cell Annotation Tool will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial open source release
- Complete internationalization support (English/Chinese)
- Standardized project structure
- Comprehensive configuration system
- Docker support
- API documentation

## [2.0.0] - 2024-09-29

### Added
- **Internationalization**: Complete English and Chinese language support
- **New Project Structure**: Standardized open source project layout
- **Configuration System**: Environment-based configuration with .env support
- **Security Improvements**: Removed hardcoded secrets and sensitive information
- **Enhanced Testing**: Comprehensive test suite with validation scripts
- **Cell Type Enhancement**: Added Honeycomb as 8th cell classification type
- **API Endpoints**: RESTful API for programmatic access
- **Export Functionality**: JSON and CSV export formats
- **Docker Support**: Containerized deployment option

### Changed
- **Project Structure**: Reorganized from deep nested paths to standard layout
- **Configuration**: Moved from hardcoded config to environment variables
- **Language Support**: Extracted all Chinese text to translation files
- **Cell Classes**: Updated to use internationalization keys
- **Security**: Implemented secure session management

### Improved
- **User Interface**: Responsive design with Bootstrap 5
- **Performance**: Optimized image loading and annotation rendering
- **Accessibility**: Enhanced keyboard navigation and screen reader support
- **Documentation**: Comprehensive README and contributing guidelines

### Fixed
- **Path Issues**: Resolved deep directory path problems
- **Template Errors**: Fixed Jinja2 syntax issues in internationalization
- **Configuration Loading**: Improved environment variable handling
- **Memory Management**: Better resource cleanup in annotation processing

## [1.0.0] - 2024-01-01

### Added
- Initial release of Bee Cell Annotation Tool
- Basic annotation functionality for 7 cell types
- Web-based interface with drawing tools
- Image pagination and navigation
- Annotation export functionality
- Chinese language interface

### Features
- Circle and polygon drawing tools
- 7 cell type classifications (Eggs, Larvae, Capped Brood, Pollen, Nectar, Honey, Other)
- Batch image processing
- JSON annotation format
- Keyboard shortcuts for efficient annotation

---

## Version History

- **v2.0.0**: Open source release with internationalization
- **v1.0.0**: Initial internal release

## Migration Guide

### From v1.0.0 to v2.0.0

1. **Configuration**: Create `.env` file from `.env.example`
2. **Project Structure**: Use new standardized directory layout
3. **Language**: Application now defaults to English (set `DEFAULT_LANGUAGE=zh` for Chinese)
4. **Cell Types**: New "Honeycomb" type added as 8th classification
5. **API**: New REST endpoints available for programmatic access

### Breaking Changes

- Configuration now requires environment variables
- Project directory structure has changed
- Default language changed from Chinese to English
- Some internal API endpoints have new URLs

For detailed migration instructions, see [MIGRATION.md](docs/MIGRATION.md).
