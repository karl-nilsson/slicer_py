# OCCT slicer testbed

## Requirements
- Python3
- OCCT
- pythonocc-core

## Usage
python3 slicer.py <filename.step>

## Example output:
![curve test](res/img/curve_test.png)
![concave test](res/img/concave_test.png)

## Offset failure
OCCT's offset algorithm doesn't handle intersections
![](res/img/failure_1.png)
![](res/img/failure_2.png)

## TODO
- Subdivide curves