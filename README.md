# VectorConfig - Product Configuration & Vector Generation

A desktop application for configuring and generating vector drawings of customizable products, specializing in woodworking and storage solutions.

## Overview

VectorConfig is a specialized tool designed to help makers and craftspeople configure and generate vector drawings for modular products. Similar to kitchen configuration software, but focused on custom storage solutions and woodworking projects. The application comes with built-in product definitions and templates, allowing you to quickly configure and generate production-ready vector drawings. You can import your AutoCAD DXF files and convert them into 3D models, making it easy to visualize and modify your designs in three dimensions.

## Key Features

### Current Features
- Basic vector drawing interface
- Open and save SVG files
- Resize vector drawings
- Simple and intuitive interface

### AutoCAD DXF Support
- Import AutoCAD DXF files:
  - Full layer support
  - Block and component recognition
  - Dimension and annotation preservation
  - Scale and unit conversion
- Features:
  - Automatic depth calculation
  - Material thickness application
  - Joint detection and creation
  - Component separation
  - Layer-based organization
- Export options:
  - Standard 3D formats (STL, OBJ)
  - Interactive 3D viewer
  - Assembly preview
  - Back to DXF for AutoCAD

### Built-in Product Library
- Predefined product templates:
  - Storage containers
  - Plywood furniture
  - Custom storage solutions
  - Modular components
- Each product includes:
  - 3D component definitions
  - Material specifications
  - Joint and connection details
  - Assembly instructions
  - Vector generation rules

### Configuration Features
- Product customization:
  - Adjust dimensions (height, width, depth)
  - Configure features (dividers, compartments)
  - Select materials and thicknesses
  - Define joint types
- Smart constraints:
  - Material thickness compensation
  - Joint and fitting specifications
  - Assembly considerations
  - Minimum/maximum dimensions
  - Standard material sizes

### Vector Generation
- Automatic 2D vector generation from 3D configurations
- Optimized layouts for material sheets
- Export formats for:
  - CNC cutting
  - Laser cutting
  - Manual cutting guides
- Cutting lists and material requirements

## Use Cases

### Importing AutoCAD Designs
1. Export your design from AutoCAD as DXF
2. Import DXF into VectorConfig
3. Define material properties and thickness
4. Convert to 3D model
5. Adjust and refine in 3D view
6. Generate cutting templates
7. Export for manufacturing or back to AutoCAD

### Storage Container Configuration
1. Select container type from built-in templates
2. Adjust dimensions (height, width, depth)
3. Configure features (dividers, compartments)
4. Generate 2D cutting templates
5. Preview 3D model
6. Export vector files for manufacturing

### Custom Furniture Design
1. Choose furniture type from templates
2. Customize dimensions
3. Add/remove components
4. Generate cutting lists
5. View 3D preview
6. Export production-ready vectors

## Technical Requirements

- Python 3.8 or higher
- PyQt6 (for GUI)
- svgwrite (for vector handling)
- Pillow (for image processing)
- Additional 3D libraries:
  - PyOpenGL (for 3D visualization)
  - NumPy (for 3D calculations)
  - Trimesh (for 3D model handling)
  - ezdxf (for DXF file support)
  - OCC-Core (for advanced CAD operations)

## Installation

1. Install Python from https://www.python.org/downloads/
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

```bash
python vector_editor.py
```

## Project Status

Currently in early development. The basic vector editing interface is implemented, with DXF import, 3D conversion, and configuration features planned for future releases.

## Future Development

- Expand product template library
- Add more material types and specifications
- Enhance joint and connection options
- Improve vector optimization algorithms
- Add assembly instruction generation
- Support for custom product definitions
- Advanced 3D modeling features
- Real-time 3D preview
- Interactive assembly simulation
- Enhanced AutoCAD compatibility
- Automatic joint detection and creation
- Material optimization for imported designs
- Direct AutoCAD plugin support

## Contributing

This is a personal project for custom manufacturing workflows. Suggestions and ideas are welcome!