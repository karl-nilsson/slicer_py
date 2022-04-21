
### Linear infill

- Parameters: density, angle
- space between lines = line_width * log₂(100/infill) + 1
  - 100%: 1 * line_width
  - 50%: 2 * ...
  - 25%: 3 * ...
  - 12.5%: 4 * ...

### Gyroid infill

- Parameters: density, angle
- periodic wrt z-height
- Sine waves shift until aligned
- Then flip 90°
- use gcode macro/subprogram to reduce code size
- use arcs to further reduce code size