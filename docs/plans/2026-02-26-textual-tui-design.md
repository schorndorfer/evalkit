# EvalKit Textual TUI Design

**Date:** 2026-02-26
**Status:** Approved
**Issue:** [#1](https://github.com/schorndorfer/evalkit/issues/1)

## Overview

Add a rich Terminal User Interface (TUI) to EvalKit using the Textual framework, providing an interactive dashboard for exploring evaluation metrics with in-terminal graphs and full keyboard/mouse support.

## Requirements

- Interactive dashboard layout with multiple panels
- In-terminal graph rendering using plotext and custom widgets
- Full keyboard and mouse navigation
- Export functionality from within TUI
- Configurable panel visibility and layout options
- Graceful error handling and degradation
- Backward compatible with existing CLI

## Architecture

### Approach: Hybrid Architecture

Keep existing evaluation and metrics calculation logic unchanged. Create new TUI-specific components in `evalkit/tui/` that use Textual widgets while reusing core evaluation code.

**Rationale:**
- Maintains backward compatibility with CLI
- Enables rich interactivity via Textual widgets
- Reduces risk by isolating new code
- Supports incremental development
- Clean separation of concerns

### Project Structure

```
evalkit/
├── tui/                           # New TUI module
│   ├── __init__.py               # Exports main TUI entry point
│   ├── app.py                    # Main Textual application
│   ├── config.py                 # Dashboard configuration
│   ├── widgets/                  # Custom Textual widgets
│   │   ├── __init__.py
│   │   ├── header.py            # Summary header panel
│   │   ├── metrics_table.py     # Metrics display widget
│   │   ├── confusion_matrix.py  # Confusion matrix widget
│   │   ├── graph_panel.py       # Graph container with plotext
│   │   └── footer.py            # Keyboard shortcuts help
│   └── layouts/                  # Layout configurations
│       ├── __init__.py
│       └── dashboard.py         # Grid layout definitions
├── formatters/                   # Existing (unchanged)
├── evaluator.py                  # Existing (unchanged)
└── ...
```

### Dependencies

New dependencies to add:
- `textual>=0.47.0` - TUI framework
- `textual-plotext>=0.2.0` - Plotext integration for Textual
- `plotext>=5.2.0` - Terminal plotting

## CLI Integration

Add `--tui` flag to existing `evaluate` command:

```bash
evalkit evaluate predictions.csv --tui
evalkit evaluate data.csv --tui --tui-layout minimal
evalkit evaluate data.csv --tui --tui-theme dark
```

**Flow:**
1. User runs command with `--tui` flag
2. Evaluation runs normally (same code path)
3. Instead of calling `display_results()`, launch Textual app with results
4. TUI runs in full-screen mode until user quits

## Dashboard Layout

### Default Grid Layout

```
┌─────────────────────────────────────────────────────────────┐
│ HEADER: Mode | Samples | File | Accuracy/R²        [? Help] │
├────────────────────────┬────────────────────────────────────┤
│                        │                                    │
│  SUMMARY METRICS       │   PRIMARY GRAPH                    │
│  (Key stats in boxes)  │   - Confusion Matrix (classify)    │
│                        │   - Predicted vs Actual (regress)  │
│                        │                                    │
├────────────────────────┼────────────────────────────────────┤
│                        │                                    │
│  DETAILED METRICS      │   SECONDARY GRAPH                  │
│  (Scrollable table)    │   - Per-class bars (classify)      │
│                        │   - Residual plot (regress)        │
│                        │                                    │
├────────────────────────┴────────────────────────────────────┤
│ FOOTER: [q]uit [e]xport [s]ave [h]elp [tab] focus [↑↓] nav │
└─────────────────────────────────────────────────────────────┘
```

### Configurable Layouts

Layout options via `--tui-layout` flag:
- `minimal`: Header + Primary Graph only
- `standard`: Header + Summary + Detailed Metrics + Primary Graph
- `full`: All panels (default)

Future: User config file (`~/.evalkit/config.toml`) for persistent preferences.

## Widgets

### 1. Header Widget (`header.py`)

**Purpose:** Display summary information and top-level metric

**Content:**
- Evaluation mode (Classification/Regression)
- Sample count
- CSV file name
- Top metric (Accuracy for classification, R² for regression)
- Help button (`?`) in top-right corner

**Styling:**
- Color-coded by performance:
  - Green: > 0.9
  - Yellow: 0.7-0.9
  - Red: < 0.7

### 2. Summary Metrics Widget (`metrics_table.py`)

**Purpose:** Display 4-6 key metrics in highlighted boxes

**Content:**
- **Classification:** Accuracy, Precision, Recall, F1, Kappa
- **Regression:** R², MAE, RMSE, MAPE

**Features:**
- Box-style layout with borders
- Color highlighting for values
- Updates in real-time if data refreshes

### 3. Detailed Metrics Widget (`metrics_table.py`)

**Purpose:** Show all calculated metrics in a table

**Features:**
- Scrollable DataTable widget
- Shows all metrics from evaluation
- Sortable columns
- Clickable rows for highlighting
- Search/filter capability

### 4. Graph Widgets

#### Confusion Matrix Widget (`confusion_matrix.py`)

**Purpose:** Display classification confusion matrix as heatmap

**Implementation:**
- Custom widget using Textual containers + Rich styling
- ASCII art representation with box-drawing characters
- Color gradient: Green (correct) → Red (incorrect)
- Shows actual counts in each cell
- Axis labels for class names
- Auto-scales for different class counts

#### Graph Panel Widget (`graph_panel.py`)

**Purpose:** Container for plotext-based graphs

**Graph Types:**

**Classification:**
- **Primary:** Confusion matrix (see above)
- **Secondary:** Per-class metrics bar chart
  - Horizontal bars for Precision, Recall, F1
  - Color-coded by metric type
  - Scrollable for many classes

**Regression:**
- **Primary:** Predicted vs Actual scatter plot
  - X-axis: Actual values
  - Y-axis: Predicted values
  - Diagonal line showing perfect prediction
  - Color gradient by error magnitude
- **Secondary:** Residual plot
  - X-axis: Predicted values
  - Y-axis: Residuals (actual - predicted)
  - Horizontal line at y=0

**Features:**
- Uses `textual-plotext` integration
- Auto-scaling based on data range
- Legend display
- Axis labels with units
- Grid lines (toggleable)

### 5. Footer Widget (`footer.py`)

**Purpose:** Display keyboard shortcuts and status

**Content:**
- Active keyboard shortcuts
- Current focus indicator
- Status messages

## Graph Implementation Strategy

### Library Usage

| Graph Type | Library | Reason |
|------------|---------|--------|
| Confusion Matrix | Custom (Textual + Rich) | Need precise cell coloring and layout |
| Bar Charts | `plotext` | Native support, clean rendering |
| Scatter Plots | `plotext` | Handles large datasets well |
| Histograms | `plotext` | Built-in histogram function |

### Combination Approach

Use the best tool for each visualization:
- **Custom widgets:** When precise control over layout/coloring needed
- **plotext:** For standard chart types (scatter, bar, histogram)
- **Rich:** For styling and text-based visualizations
- **Textual-plotext:** Integration layer for embedding plotext in Textual

## Interactive Features

### Keyboard Shortcuts

| Key | Action | Description |
|-----|--------|-------------|
| `q` / `Ctrl+C` | Quit | Exit the TUI |
| `Tab` | Focus Next | Cycle through panels |
| `Shift+Tab` | Focus Previous | Cycle backwards |
| `↑` `↓` `←` `→` | Navigate | Scroll within focused panel |
| `h` / `?` | Help | Show keyboard shortcuts overlay |
| `e` | Export | Open export dialog (JSON/CSV/MD) |
| `s` | Save Screenshot | Save current view as PNG |
| `v` | Toggle Panel | Show/hide panels |
| `r` | Refresh | Reload data from CSV |
| `f` | Fullscreen | Maximize focused panel |
| `Esc` | Back | Return from fullscreen/close dialog |

### Mouse Support

- Click panels to focus
- Scroll with mouse wheel
- Click buttons in dialogs
- Future: Drag to resize panels

### Interactive Dialogs

**1. Export Dialog:**
- Triggered by `e` key
- Modal dialog for export options
- Format selection: JSON, CSV, Markdown
- Output path specification
- Progress indicator during export

**2. Panel Toggle Menu:**
- Triggered by `v` key
- Checkboxes for each panel type
- Live preview as selections change
- Save preference for session

**3. Help Overlay:**
- Triggered by `h` or `?`
- Semi-transparent overlay
- Categorized shortcuts
- Press any key to dismiss

**4. Fullscreen Mode:**
- Triggered by `f` on focused panel
- Panel expands to fill entire screen
- Detailed inspection of graphs/tables
- Press `Esc` to return

**5. Data Refresh:**
- Triggered by `r` key
- Shows loading spinner
- Reloads CSV and updates all panels
- Useful for iterative development

## Configuration

### Command-Line Flags

```bash
# Layout configuration
--tui-layout [minimal|standard|full]

# Panel visibility
--tui-panels "header,metrics,graphs"  # Comma-separated

# Theme
--tui-theme [dark|light|auto]

# Graph settings
--tui-graph-style [ascii|unicode|braille]
```

### Config File (Future Enhancement)

```toml
# ~/.evalkit/config.toml
[tui]
default_layout = "full"
theme = "dark"
panels = ["header", "summary", "detailed_metrics", "primary_graph", "secondary_graph"]

[tui.graphs]
style = "unicode"
show_grid = true
colors = true

[tui.keybindings]
quit = "q"
export = "e"
help = "?"
# ... customizable shortcuts
```

## Error Handling

### Graceful Degradation

**Scenario 1: Missing Dependencies**
- If `plotext` unavailable: Show text-based metric summaries instead of graphs
- Warn user on startup: "plotext not installed. Graphs disabled. Install with: pip install plotext"

**Scenario 2: Terminal Too Small**
- Minimum required: 80x24
- If smaller: Auto-switch to minimal layout
- Show warning: "Terminal size too small. Minimum 80x24 required. Current: [size]"

**Scenario 3: Graph Rendering Failure**
- Display error message in panel
- Continue showing other data
- Log error details for debugging

### User-Friendly Error Messages

**Data Loading Error:**
```
┌─────────────────────────────────────────┐
│ ⚠ Error Loading Data                   │
├─────────────────────────────────────────┤
│                                         │
│ Failed to load data from file:          │
│ predictions.csv                         │
│                                         │
│ Reason: File not found                  │
│                                         │
│ [R]etry  [Q]uit  [H]elp                │
└─────────────────────────────────────────┘
```

**Export Failure:**
- Display error reason in modal
- Keep TUI running
- Allow retry or cancel

### Validation

- Check terminal capabilities on startup
- Warn if terminal doesn't support colors/Unicode
- Provide ASCII fallback mode
- Validate minimum terminal size

### Recovery

- Auto-save session state
- If crash occurs, offer to resume from last state
- Log errors to `~/.evalkit/logs/tui.log`

## Testing Strategy

### Unit Tests

**Widget Tests (`tests/tui/test_widgets.py`):**
- Test each widget renders correctly with sample data
- Verify keyboard event handling
- Test widget state updates
- Mock Textual app context for isolated testing

**Layout Tests (`tests/tui/test_layouts.py`):**
- Test grid layout composition
- Verify panel visibility toggles
- Test responsive sizing
- Ensure minimal terminal size requirements

**Graph Tests (`tests/tui/test_graphs.py`):**
- Test plotext integration
- Verify confusion matrix rendering
- Test scatter plot generation
- Check data scaling and axis labels

### Integration Tests

**App Tests (`tests/tui/test_app.py`):**
- Test full app launch with sample data
- Verify all panels initialize correctly
- Test navigation between panels
- Test export functionality end-to-end

**CLI Integration (`tests/test_cli_tui.py`):**
- Test `--tui` flag launches TUI correctly
- Verify all CLI options pass through to TUI
- Test combination with other flags

### Snapshot Tests

- Capture terminal output snapshots using Textual's snapshot testing
- Detect unintended UI changes
- Version control snapshots for regression testing

### Manual Testing Checklist

- [ ] Test on different terminal sizes (80x24, 120x40, 200x60)
- [ ] Verify color themes (dark/light/auto)
- [ ] Test with large datasets (1000+ samples)
- [ ] Test with multiclass classification (10+ classes)
- [ ] Verify mouse interactions
- [ ] Test all keyboard shortcuts
- [ ] Verify export to all formats
- [ ] Test refresh functionality
- [ ] Check graceful degradation without plotext
- [ ] Test on different terminal emulators (iTerm2, Terminal.app, alacritty)

### Test Data

- Reuse existing fixtures from `tests/fixtures/`
- Add TUI-specific test cases:
  - Large datasets for performance testing
  - Many classes for layout stress testing
  - Edge cases (single sample, perfect predictions)
- Create mock CSV files for error scenarios

## Implementation Phases

### Phase 1: Basic TUI Framework
- Set up Textual app structure
- Implement basic grid layout
- Add header and footer widgets
- Integrate with CLI via `--tui` flag

### Phase 2: Metrics Display
- Implement summary metrics widget
- Implement detailed metrics table
- Add keyboard navigation
- Test with both evaluation modes

### Phase 3: Graph Integration
- Implement confusion matrix widget
- Integrate plotext for scatter/bar charts
- Add graph panel containers
- Test rendering with real data

### Phase 4: Interactive Features
- Add export dialog
- Implement panel toggle menu
- Add fullscreen mode
- Implement data refresh

### Phase 5: Polish & Configuration
- Add help overlay
- Implement configuration system
- Add themes
- Comprehensive error handling
- Performance optimization

## Success Criteria

- [ ] TUI launches successfully with `--tui` flag
- [ ] All panels render correctly for both classification and regression
- [ ] Graphs display properly in terminal
- [ ] All keyboard shortcuts work as documented
- [ ] Export functionality works from TUI
- [ ] Gracefully handles errors and small terminals
- [ ] Test coverage > 70%
- [ ] Works on major terminal emulators
- [ ] Performance: Handles 10,000+ samples without lag
- [ ] Documentation updated with TUI usage examples

## Future Enhancements

- Drag-to-resize panels
- Custom color schemes
- Multiple file comparison view
- Live data streaming mode
- Export graph images directly from TUI
- Plugin system for custom widgets
- Remote TUI access (SSH-friendly)
