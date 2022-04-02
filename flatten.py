#!/usr/bin/env python3

from logging import error
import time
import sys
import os
import math
from typing import *

from OCC.Core import Geom, GeomConvert, Standard
from OCC.Core import Geom2dConvert

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
from OCC.Core.BRepPrimAPI import *
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Section
from OCC.Core.BRepBuilderAPI import *
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakeOffset
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface, BRepAdaptor_Curve
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.Geom2d import *
from OCC.Core.GeomAbs import *
import OCC.Core.GeomAbs
from OCC.Core.Geom2dConvert import *
from OCC.Core.GeomConvert import * 
from OCC.Core.Convert import *
from OCC.Core.Geom2dAdaptor import *

from OCC.Display.backend import get_qt_modules
from OCC.Display.SimpleGui import init_display

DEBUG = True

# list of colors from pyocct
colors = ['WHITE', 'BLUE',  'RED',  'GREEN',  'YELLOW', 'CYAN', 'BLACK', 'ORANGE']


# initialize display
display, start_display, add_menu, add_function_to_menu = init_display()
QtCore, QtGui, QtWidgets, QtOpengl = get_qt_modules()

from OCC.Display.qtDisplay import qtViewer3d

def flatten_bezier(curve: Geom2d_BezierCurve, tolerance: float = 0.1) -> List[Geom2d_TrimmedCurve]:

  return []

def flatten_bspline(curve: Geom2d_BSplineCurve, continuity_range: int = 3) -> List[Geom2d_TrimmedCurve]:
  # https://dev.opencascade.org/content/bspline-arc
  # split bspline
  result = []
  splits = Geom2dConvert_BSplineCurveKnotSplitting(curve, continuity_range)
  for i in range(splits.NbSplits()):
    z = splits.SplitValue(i)
    print(z)
    z = curve.Knot(splits.SplitValue(i))
    print(z)
    # subcurve = geom2dconvert_SplitBSplineCurve(curve, splits.SplitValue(i), splits.SplitValue(i+1))

    # create circle
    # result.append()

  return result

def flatten_edge(edge: TopoDS_Edge) -> List:
  print(f'Edge orientation: {edge.Orientation().name}')
  adaptor_curve = BRepAdaptor_Curve(edge)

  c, start, end = BRep_Tool.Curve(edge)

  print(adaptor_curve.GetType())

  return []

def flatten_curve(curve: Union[Geom2d_Curve, Geom2d_TrimmedCurve]) -> List[Geom2d_TrimmedCurve]:
  first = curve.FirstParameter()
  last = curve.LastParameter()

  adaptor_curve = Geom2dAdaptor_Curve(curve)

  v = sys.version_info

  curve_type = adaptor_curve.GetType()

  if curve_type == GeomAbs_Ellipse.value or curve_type == GeomAbs_Parabola.value or curve_type == GeomAbs_Hyperbola.value:
    spline = geom2dconvert_CurveToBSplineCurve(curve)
    
    if DEBUG:
      display.DisplayColoredShape(spline, 'BLUE')
      for pole in spline.Poles():
        display.DisplayColoredShape(pole, 'GREEN')

    flatten_curve(spline)

  elif curve_type == GeomAbs_BSplineCurve.value:
    return flatten_bspline(curve)

    #algo = Geom2dConvert_BSplineCurveToBezierCurve(curve)
    #algo = GeomConvert_BSplineCurveToBezierCurve(curve)

    # broken
    # result: TColGeom2d_Array1OfBezierCurve = 0
    # algo.Arcs(result)
    # print(result)
  
  elif curve_type == GeomAbs_BezierCurve.value:
    return flatten_bezier(curve)
  else:
    raise Exception(f'Invalid curve type: {adaptor_curve.GetType()}')
  

  return []


def flatten_wire(wire: TopoDS_Wire) -> List[Union[Geom2d_TrimmedCurve, Geom2d_Line]]:
  for edge in WireExplorer(wire).ordered_edges():
    flatten_edge(edge)
  
  return []



if __name__ == '__main__':
  # create trimmed ellipse
  e = Geom2d_Ellipse(gp.OX2d(), 20.0, 10.0)
  e = Geom2d_TrimmedCurve(e, math.pi / 4, math.pi * 5 / 4)

  display.DisplayColoredShape(e, 'RED')

  e_flat = flatten_curve(e)

  # display the new arcs
  for i, c in enumerate(e_flat):
    display.DisplayColoredShape(c, colors[i%len(colors)])

  p = Geom2d_Parabola(gp.OX2d(), 3.0)
  p = Geom2d_TrimmedCurve(p, -10, 10)

  display.DisplayColoredShape(p, 'RED')

  p_flat = flatten_curve(p)


  display.FitAll()

  start_display()