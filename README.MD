# Blender Scripts

A collection of Blender addons for advanced mesh editing in Blender 5.x.

*Created with AI-Monkey*

## Addons

### 1. Radial Symmetry Tool (v0.1.0)
**Advanced tool for working with radial symmetry and batch assigning vertices to vertex groups**

#### Features:
- **Select by Symmetry** — select vertices with radial symmetry around a chosen axis
- **Assign to Groups** — assign selected vertices to named vertex groups with custom division
- **Select & Assign** — combined operation of selection and assignment in one action

#### Parameters:
- **Radial Symmetry**
  - Axis — rotation axis (X, Y, Z)
  - Divisions — number of equal divisions
  - Tolerance — tolerance for finding corresponding vertices

- **Vertex Group Settings**
  - Prefix — prefix for group names
  - Postfix — suffix for group names
  - Weight — influence weight of vertex on group (0.0 - 1.0)
  - Order — processing direction (Forward/Reverse)

#### Usage:
1. Select a mesh in Edit Mode
2. Select one or more vertices
3. Set parameters in the tool panel
4. Press the desired operation button

### 2. Vertex Group Batch Assign (v1.0.0)
**Tool for batch assigning selected vertices to multiple named groups**

#### Features:
- Divide selected vertices into N equal groups
- Automatically create groups with custom naming
- Remove vertices from groups
- Delete entire groups

#### Parameters:
- Group Name — group name for deletion operations
- Prefix — prefix for group names
- Divisions — number of groups to divide into
- Postfix — suffix for group names

## Installation

1. Copy addon files to your Blender addons folder:
   - Windows: `C:\Users\[YourUsername]\AppData\Roaming\Blender Foundation\Blender\5.1\scripts\addons\`
   - macOS: `/Users/[YourUsername]/Library/Application Support/Blender/5.1/scripts/addons/`
   - Linux: `/home/[YourUsername]/.config/blender/5.1/scripts/addons/`

2. Open Blender → Preferences → Extensions

3. Find the addons and enable them

## Requirements

- Blender 5.0 or higher
- Python 3.10+

## Compatibility

✅ Tested with Blender 5.1

## Notes

- Vertex groups are created automatically when assigning
- Pre-select vertices in Edit Mode before direct assignment
- Vertex order is preserved when using "Select & Assign" operation
