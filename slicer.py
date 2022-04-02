#!/usr/bin/env python3

import time
import sys
import multiprocessing
import os
import math
from collections import defaultdict

from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepTools import breptools_Read
from OCC.Core.TopoDS import TopoDS_Shape, TopoDS_Compound
from OCC.Core.TopAbs import *
from OCC.Core.gp import *
from OCC.Core.BOPAlgo import BOPAlgo_Splitter
from OCC.Core.BRep import BRep_Tool
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Section
from OCC.Core.BRepBuilderAPI import *
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakeOffset
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface, BRepAdaptor_Curve
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.GeomAbs import *
# from OCC.Core.Geom2d import *
from OCC.Core.ShapeAnalysis import ShapeAnalysis_Curve, ShapeAnalysis_Wire
from OCC.Core.Geom import *
from OCC.Core.GeomConvert import *
from OCC.Core.Convert import *

from OCC.Display.backend import get_qt_modules
from OCC.Display.SimpleGui import init_display

from OCC.Extend.ShapeFactory import get_aligned_boundingbox
from OCC.Extend.TopologyUtils import TopologyExplorer, WireExplorer
from OCC.Extend.DataExchange import read_step_file

# initialize display
print('Initializing display')
display, start_display, add_menu, add_function_to_menu = init_display("qt-pyqt5")
QtCore, QtGui, QtWidgets, QtOpengl = get_qt_modules()

from OCC.Display.qtDisplay import qtViewer3d

def o(shape):
  print(shape.Orientation())

  if shape.Orientation() == TopAbs_FORWARD:
    return 'FORWARD'
  elif shape.Orientation() == TopAbs_REVERSED:
    return 'REVERSED'
  elif shape.Orientation() == TopAbs_INTERNAL:
    return 'INTERNAL'
  elif shape.Orientation() == TopAbs_EXTERNAL:
    return 'EXTERNAL'
  


# when selecting a shape, print details, and gcode representation
def on_select(shapes):
  if len(shapes) < 1:
    return
  s = shapes[0]

  if s.ShapeType() == TopAbs_EDGE:
    print(o(s))

    tmp = BRepAdaptor_Curve(s)

    # display start and endpoints of curve
    start_point = tmp.Value(tmp.FirstParameter())
    end_point = tmp.Value(tmp.LastParameter())

    if s.Orientation() == TopAbs_FORWARD:
      display.DisplayColoredShape(BRepBuilderAPI_MakeVertex(start_point).Vertex(), "BLUE")
      display.DisplayColoredShape(BRepBuilderAPI_MakeVertex(end_point).Vertex(), "RED")
    else:
      display.DisplayColoredShape(BRepBuilderAPI_MakeVertex(start_point).Vertex(), "RED")
      display.DisplayColoredShape(BRepBuilderAPI_MakeVertex(end_point).Vertex(), "BLUE")


    if tmp.GetType() == GeomAbs_Line:
      t = tmp.Line()
      gcode = f'G01 X{end_point.X():.6f} Y{end_point.Y():.6f}'
      print(f'line: ({start_point.X():.6f}, {start_point.Y():.6f}) → ({end_point.X():.6f}, {end_point.Y():.6f})')
      # print(gcode)
      print(f'line parameters: {tmp.FirstParameter():.6f}, {tmp.LastParameter():.6f}')


    elif tmp.GetType() == GeomAbs_Circle:
      t = tmp.Circle()
      center_point = t.Location()


      # make two line segments, both from the centerpoint, and one to each of the endpoints
      # the cross product of the lines determines the direction. positive = CCW, negative = CW
      # assume for now the arc is in the XY plane, so only check the sign of z
      # assume clockwise for now
      # center format arc
      v1 = gp_Vec(center_point, start_point)
      v2 = gp_Vec(center_point, end_point)

      # angle > 0 if acute, < 0 if obtuse
      angle = v1.AngleWithRef(v2, gp_Vec(0,0,1))
      # use cross product to determine direction
      v1.Cross(v2)
      v1 *= angle
      # TODO: verify
      CCW = True if v1.Z() > 0 else False
      
      gcode = "G0{0} X{1:.6f} Y{2:.6f} I{3:.6f} J{4:.6f}".format(2 if CCW else 3, end_point.X(), end_point.Y(), 
        center_point.X() - start_point.X(), center_point.Y() - start_point.Y())
      print("circle: start (%.6f, %.6f), end (%.6f, %.6f), center (%.6f, %.6f), radius %.6f" % (start_point.X(), start_point.Y(), end_point.X(), end_point.Y(), 
        center_point.X(), center_point.Y(), t.Radius()))
      print("circle parameters: %.6f, %.6f" % (tmp.FirstParameter() / math.pi, tmp.LastParameter() / math.pi))

      # print(gcode)
    elif tmp.GetType() == GeomAbs_Ellipse:
      t = tmp.Ellipse()
      x = t.XAxis()
      y = t.YAxis()
      print("ellipse")
    elif tmp.GetType() == GeomAbs_Hyperbola:
      t = tmp.Hyperbola()
      print("hyperbola")
    elif tmp.GetType() == GeomAbs_Parabola:
      t = tmp.Parabola()
      print("parabola")
    elif tmp.GetType() == GeomAbs_BezierCurve:
      t = tmp.Bezier()
      print("bezier")
    elif tmp.GetType() == GeomAbs_BSplineCurve:
      t = tmp.BSpline()
      print("bspline")
    elif tmp.GetType() == GeomAbs_OffsetCurve:
      t = tmp.OffsetCurve()
      print("offset")
    elif tmp.GetType() == GeomAbs_OtherCurve:
      print("other")

def get_viewer():
  app = QtWidgets.QApplication.instance()
  if not app:
    app = QtWidgets.QApplication(sys.argv)
  widgets = app.topLevelWidgets()
  for w in widgets:
    if hasattr(w, "_menus"):
      viewer = w.findChild(qtViewer3d, "qt_viewer_3d")
      return viewer


def wire_gcode(wire):
  print(f'Wire Orientation: {o(wire)}')
  if wire.Orientation() == TopAbs_REVERSED:
    wire.Reverse()

  for edge in WireExplorer(wire).ordered_edges():
    print(f'Edge Orientation: {o(edge)}')
    tmp = BRepAdaptor_Curve(edge)
    # get underlying curve
    c, start, end = BRep_Tool.Curve(edge)
    # display start and endpoints of curve
    start_point = tmp.Value(tmp.FirstParameter())
    end_point = tmp.Value(tmp.LastParameter())

    if edge.Orientation() == TopAbs_FORWARD:
      display.DisplayColoredShape(BRepBuilderAPI_MakeVertex(start_point).Vertex(), "BLUE")
      display.DisplayColoredShape(BRepBuilderAPI_MakeVertex(end_point).Vertex(), "RED")
    else:
      display.DisplayColoredShape(BRepBuilderAPI_MakeVertex(start_point).Vertex(), "RED")
      display.DisplayColoredShape(BRepBuilderAPI_MakeVertex(end_point).Vertex(), "BLUE")

    # display individual curve
    display.DisplayShape(edge, update=True)
    time.sleep(1)


def make_offsets(face, num, distance):
  offset = BRepOffsetAPI_MakeOffset(face, GeomAbs_Arc, False)
  # add all wires to offset algo
  for w in TopologyExplorer(face).wires():
    offset.AddWire(w)
  result = []
  # perform offsets
  for i in range(num):
    offset.Perform(-1 * distance * i)
    if offset.IsDone():
      # display.DisplayShape(offset.Shape(), update=True)
      result.append(offset.Shape())

  return result


def find_faces(solid):
  # search the solid for the bottom-most horizontal planes
  result = defaultdict(list)
  # downward-facing XY plane
  d = gp.DZ().Reversed()
  # loop over all faces (only faces)
  for f in TopologyExplorer(solid).faces():
    surf = BRepAdaptor_Surface(f, True)
    # skip non-planar faces
    if surf.GetType() != GeomAbs_Plane:
      continue
    # get surface attributes
    pln = surf.Plane()
    location = pln.Location()
    normal = pln.Axis().Direction()

    # if face is reversed, reverse the surface normal
    if f.Orientation() == TopAbs_REVERSED:
      normal.Reverse()

    # add face if it's parallel (opposite) and coincident with a slicing plane
    if d.IsEqual(normal, 0.1):
      result[location.Z()].append(f)
      # display the face
      # display.DisplayShape(f, update=True)
      # display the face normal
      # display.DisplayVector(gp_Vec(normal), location, update=True)

  # sort the dict by keys (z-height), and return the lowest
  lowest = sorted(result.keys())[0]

  for f in result[lowest]:
    print(f'z: {lowest}, orientation: {"FORWARD" if f.Orientation() == TopAbs_FORWARD else "REVERSED"}')
  # return all faces associated with the lowest value
  print(f'number of faces: {len(result[lowest])}')

  return result[lowest]

def arange(start, end, diff):
  result = [start]
  while result[-1] < end:
    result.append(result[-1] + diff)
  return result


def slice(shape):
  # keep track of time for perf
  init_time = time.time()
  # get the axis-aligned bounding box and dimensions of shape
  center, [dx, dy, dz], box_shp = get_aligned_boundingbox(shape)
  # get maximum z coordinate
  z_max = center.Z() + dz / 2
  # slice height in mm
  slice_height = 2 # 0.3
  # number of shells (offsets)
  num_shells = 3
  # distance between offsets
  shell_thickness = 0.4
  # list of slicing plane heights
  # z_list = [i * slice_height for i in range(int(z_max / slice_height) + 1)]
  # splitter function
  splitter = BOPAlgo_Splitter()
  splitter.SetRunParallel(True)
  splitter.SetFuzzyValue(0.001)
  splitter.AddArgument(shape)
  # loop over slicing planes
  planes = {}  
  for z in arange(0, z_max, slice_height):
    # create slicing plane
    plane = gp_Pln(gp_Pnt(0., 0., z), gp.DZ())
    face = BRepBuilderAPI_MakeFace(plane).Shape()
    # add slicing plane (face) to dict
    planes[z] = face
    # add slicing plane to splitter algo
    splitter.AddTool(face)

  # split the shape
  splitter.Perform()
  # record the time spent
  split_time = time.time()
  # get the solid slices from the result
  exp = TopExp_Explorer(splitter.Shape(), TopAbs_SOLID)
  faces = []
  while exp.More():
    faces.extend(find_faces(exp.Current()))
    exp.Next()
  search_time = time.time()
  # display.EraseAll()
  # offset wires
  print('offsetting wires')
  wires = []
  # loop over faces
  for f in faces:
    # display.DisplayShape(f, update=False)
    # make offsets of all wires in face
    # wires.append(make_offsets(f, num_shells, shell_thickness))
    z = TopExp_Explorer(f, TopAbs_WIRE)
    while z.More():
      wires.append(z.Current())
      z.Next()

  offset_time = time.time()


  print('displaying offsets')
  for w in wires:
    wire_gcode(w)

  # update viewer when all is added:
  display.Repaint()
  current_time = time.time()
  print('Splitting time: ', split_time - init_time)
  print('Searching time: ', search_time - split_time)
  print('Offsetting time: ', offset_time - split_time)
  print('Display time: ', current_time - offset_time)
  print('Total time: ', current_time - init_time)
  viewer = get_viewer()
  viewer.sig_topods_selected.connect(on_select)
  start_display()


if __name__ == '__main__':
  if len(sys.argv) < 2:
    sys.exit(1)
  if not os.path.isfile(sys.argv[1]):
    sys.exit(1)

  shape = read_step_file(sys.argv[1])

  #display.DisplayShape(shape)

  slice(shape)
