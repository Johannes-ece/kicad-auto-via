# Via Grid Placer Plugin for KiCad 9

A KiCad 9 plugin that automatically places vias in a grid pattern within selected copper zones while respecting design rules.

## Features

- **Grid-based via placement** within any copper zone shape
- **Reference via copying** - uses an existing via as a template for size, drill, and net properties
- **Configurable grid spacing** with millimeter precision
- **Staggered grid option** for better coverage and thermal performance
- **DRC compliance checking** before placing each via
- **Progress tracking** with ability to cancel long operations
- **Multi-zone support** - process multiple zones in one operation

## Installation

### 1. Locate your KiCad plugins directory

- **Linux**: `~/.local/share/kicad/9.0/scripting/plugins/`
- **Windows**: `%APPDATA%\kicad\9.0\scripting\plugins\`
- **macOS**: `~/Documents/KiCad/9.0/scripting/plugins/`

### 2. Install the plugin

Copy the entire `via_grid_placer` folder to your KiCad plugins directory.

```bash
# Example for Linux/macOS:
cp -r via_grid_placer ~/.local/share/kicad/9.0/scripting/plugins/
```

### 3. Refresh plugins in KiCad

Either:
- Restart KiCad PCB Editor
- Or use: Tools → External Plugins → Refresh Plugins

## Usage

### Basic Usage

1. **Open your PCB** in KiCad's PCB Editor

2. **Select the copper zone(s)** where you want to place vias
   - Click on the zone outline or use box selection
   - You can select multiple zones

3. **Select a reference via** that has the properties you want to copy
   - This via's size, drill, type, and net will be used for all new vias

4. **Run the plugin**
   - Click the Via Grid Placer icon in the toolbar
   - Or access through: Tools → External Plugins → Via Grid Placer

5. **Configure parameters**:
   - **Grid Spacing**: Distance between vias (in mm)
   - **Stagger alternate rows**: Offset every other row for hexagonal-like pattern
   - **Check DRC before placing**: Skip positions that would violate design rules

6. **Click OK** to start placement

### Advanced Tips

- **For thermal vias**: Use smaller spacing (1-2mm) with stagger enabled
- **For shielding**: Use regular grid without stagger
- **Large areas**: The plugin shows progress and can be cancelled if needed

## Configuration Options

### Grid Spacing
- Minimum: 0.1mm
- Maximum: 50.0mm
- Default: 5.0mm

### Stagger Pattern
When enabled, alternating rows are offset by half the grid spacing, creating a more efficient coverage pattern.

### DRC Checking
When enabled, the plugin checks each via position against:
- Minimum clearance rules
- Existing tracks and vias
- Component pads

## Troubleshooting

### Plugin doesn't appear in toolbar
- Check for Python syntax errors in KiCad's Python console
- Verify all files are in the correct directory
- Try Tools → External Plugins → Refresh Plugins

### Vias not visible after placement
- The display should auto-refresh
- Try zooming in/out or pressing F5
- Save and reload the PCB if needed

### "No Zone Selected" error
- Make sure to click on the copper zone outline, not the filled area
- Use the selection tool (S key) to select zones

### DRC violations after placement
- Enable "Check DRC before placing" option
- Verify your board's minimum clearance rules
- Check that the reference via has the correct net assignment

## Technical Details

- **API**: Uses KiCad 9's SWIG Python API
- **Python Version**: Compatible with Python 3.x
- **KiCad Version**: Requires KiCad 9.0 or later

## License

MIT License - See LICENSE file for details

## Contributing

Issues and pull requests welcome at: [your-github-repo-url]

## Version History

- **1.0.0** - Initial release
  - Basic grid placement functionality
  - DRC checking support
  - Stagger pattern option