# I.N.S.I.G.H.T. Renderer Package

This package contains all rendering components for the I.N.S.I.G.H.T. platform, providing clean separation of concerns by moving all presentation logic out of the main application.

## Package Contents

### `console_renderer.py`
- **`ConsoleRenderer`**: Static class for all terminal/console output
- Handles formatted output for reports, briefings, and feed analysis
- Provides user interface elements like menus and banners
- Methods:
  - `render_report_to_console()` - Generic post list rendering
  - `render_briefing_to_console()` - Chronological briefing display
  - `render_feed_info()` - RSS/Atom feed analysis display
  - `report_mission_outcome()` - Mission completion feedback
  - `display_mission_menu()` - Mission selection interface
  - `display_output_format_menu()` - Format selection interface
  - `display_startup_banner()` - Application startup display

### `html_renderer.py`
- **`HTMLRenderer`**: Class for generating HTML dossier files
- Creates self-contained HTML reports with embedded CSS
- Enhanced support for RSS/Atom feeds, categories, and media
- Methods:
  - `render_report()` - Simple post list as HTML
  - `render_briefing()` - Full briefing organized by source and date
  - `render_rss_briefing()` - RSS-specific briefing with analytics
  - `save_to_file()` - Export to HTML file

### `__init__.py`
- Package initialization and exports
- Provides clean imports: `from renderer import HTMLRenderer, ConsoleRenderer`

## Benefits of This Refactoring

1. **Clean Separation**: Rendering logic is separated from business logic
2. **Maintainability**: Easier to modify presentation without touching core functionality
3. **Reusability**: Renderer classes can be used independently
4. **Testing**: Rendering components can be tested in isolation
5. **Organization**: Clear structure with related functionality grouped together

## Usage

```python
from renderer import HTMLRenderer, ConsoleRenderer

# Console output
ConsoleRenderer.render_report_to_console(posts, "My Report")
ConsoleRenderer.display_mission_menu()

# HTML output
html_renderer = HTMLRenderer("Intelligence Report")
html_renderer.render_briefing(briefing_data, days)
html_renderer.save_to_file("report.html")
```

## Migration from main.py

All rendering methods have been moved from the `InsightOperator` class to static methods in `ConsoleRenderer`. The main application now focuses purely on:

- Data collection and processing
- JSON export functionality  
- Connector management
- Error handling and timeouts
- Business logic orchestration

This follows the principle of **Single Responsibility** and makes the codebase more maintainable and scalable. 