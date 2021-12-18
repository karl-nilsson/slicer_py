#!/usr/bin/env python3

import time
import sys
import os
import math

from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepTools import breptools_Read
from OCC.Core.TopoDS import *
from OCC.Core.TopAbs import *
from OCC.Core.gp import *

from OCC.Core.BRepAlgoAPI import *
from OCC.Extend.ShapeFactory import get_aligned_boundingbox
from OCC.Extend.TopologyUtils import TopologyExplorer, WireExplorer
from OCC.Extend.DataExchange import read_step_file
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
from OCC.Core.BRepPrimAPI import *

from OCC.Display.backend import get_qt_modules
from OCC.Display.SimpleGui import init_display

# initialize display
print('Initializing display')
display, start_display, add_menu, add_function_to_menu = init_display("qt-pyqt5")
QtCore, QtGui, QtWidgets, QtOpengl = get_qt_modules()

HASHCODE_SIZE = 1000


def slice_shape(shape):
  center, [dx, dy, dz], box_shape = get_aligned_boundingbox(shape)

  z_max = center.Z() + dz / 2

  slice_height = 2

  slice_z = [i * slice_height for i in range(int(z_max/ slice_height))]

  slices = []
  wires = dict()

  for z in slice_z:
    p = gp_Pln(gp_Pnt(0., 0., z), gp.DZ())
    face = BRepBuilderAPI_MakeFace(p).Shape()

    s = (BRepAlgoAPI_Common(shape, face).Shape())

    slices.append(s)
    slice_hash = s.HashCode(HASHCODE_SIZE)

    t = TopExp_Explorer(slices[-1], TopAbs_WIRE)
    wires[slice_hash] = []
    while t.More():
      wires[slice_hash].append(t.Current())
      t.Next()
      

  return slices, wires


  

def compare(shape1, shape2):
  print('-' * 20)
  print(f'a.IsPartner(b): {shape1.IsPartner(shape2)}')
  print(f'a.IsSame(b): {shape1.IsSame(shape2)}')
  print(f'a.IsEqual(b): {shape1.IsEqual(shape2)}')
  print('-' * 20)


if __name__ == '__main__':

  # shape = read_step_file('res/cube.step')

  shape = BRepPrimAPI_MakeCylinder(10, 5).Shape()

  slices, wires = slice_shape(shape)

  hashcodes = []

  for s in slices:
    display.DisplayShape(s)
    print(s.HashCode(1000))
    hashcodes.append(s.HashCode(1000))

    for s2 in slices:
      if(s == s2):
        continue

      compare(s, s2)

    print('-' * 20)

  for k,v in wires.items():
    print(k)
    for i in v:
      print(i.HashCode(HASHCODE_SIZE))
      hashcodes.append(i.HashCode(HASHCODE_SIZE))

      for edge in WireExplorer(i).ordered_edges():
        print(edge.HashCode(HASHCODE_SIZE))
        hashcodes.append(edge.HashCode(HASHCODE_SIZE))

  hashcodes.sort()
  print(hashcodes)


  display.FitAll()

  start_display()

