# KiCad Via Grid Generator

A professional KiCad v9 plugin for automatically placing vias in a grid pattern with full DRC compliance.

## Features

- 🎯 **Automatic DRC Compliance**: Intelligently avoids existing components and traces
- 📐 **Flexible Grid Configuration**: Adjustable spacing in mm or mils
- 🔧 **Customizable Via Parameters**: Size, drill, and net selection
- 🎨 **Board Outline Detection**: Automatically detects and respects board boundaries
- 📊 **Progress Reporting**: Real-time feedback for large operations
- 🔍 **Smart Clearance Checking**: Different clearances for same-net vs different-net items
- 🌐 **Multi-language Ready**: Prepared for internationalization

## Installation

### Via KiCad Plugin and Content Manager (Recommended)

1. Open KiCad 9.0 or later
2. Go to **Tools → Plugin and Content Manager**
3. Search for "Via Grid Generator"
4. Click **Install**
5. Restart KiCad

### Manual Installation

1. Download the latest release from [GitHub Releases](https://github.com/Johannes-ece/kicad-auto-via/releases)
2. Extract the ZIP file
3. Copy the contents to your KiCad plugins directory:
   - Windows: `%APPDATA%\kicad\9.0\plugins\`
   - Linux: `~/.local/share/kicad/9.0/plugins/`
   - macOS: `~/Library/Application Support/kicad/9.0/plugins/`
4. Restart KiCad

## Usage

1. Open your PCB in KiCad PCB Editor
2. Click the **Via Grid Generator** button in the toolbar, or
   - Go to **Tools → External Plugins → Via Grid Generator**
3. Configure your parameters:
   - **Grid Spacing**: Distance between vias (mm or mils)
   - **Via Size**: Diameter of the via pad
   - **Drill Size**: Diameter of the via hole
   - **Net**: Which net to connect (typically GND)
4. Click **Generate**
5. Run DRC to verify the results

## Configuration Options

### Grid Settings
- **Spacing**: 0.1mm to 50mm (adjustable in 0.1mm steps)
- **Units**: Millimeters or mils
- **Area**: Entire board or selected region

### Via Parameters
- **Size**: 0.1mm to 10mm
- **Drill**: 0.1mm to 10mm
- **Net**: Any net in your design

### DRC Settings
- **Minimum Clearance**: Clearance to different-net items
- **Via-to-Via Spacing**: Minimum spacing between vias on the same net

## Requirements

- KiCad 9.0 or later
- Python 3.8 or later (included with KiCad)
- Windows, Linux, or macOS

## Development

To contribute to this plugin:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Building from Source

```bash
# Clone the repository
git clone https://github.com/Johannes-ece/kicad-auto-via.git

# Create the plugin package
cd kicad-auto-via
zip -r via-grid-generator-v1.0.0.zip plugins/ resources/ metadata.json

# Calculate SHA256 for metadata.json
sha256sum via-grid-generator-v1.0.0.zip
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- KiCad development team for the excellent PCB design software
- The KiCad community for testing and feedback

## Support

- 🐛 [Report bugs](https://github.com/Johannes-ece/kicad-auto-via/issues)
- 💡 [Request features](https://github.com/Johannes-ece/kicad-auto-via/issues)
- 📧 [Contact author](https://github.com/Johannes-ece)