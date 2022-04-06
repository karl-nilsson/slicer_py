#!/usr/bin/env python

import math


from OCC.Core.gp import *
from OCC.Core.AIS import *
from OCC.Core.Quantity import Quantity_Color, Quantity_NOC_BLACK
from OCC.Core.Prs3d import Prs3d_DimensionAspect
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Display.SimpleGui import init_display
from OCC.Core.Geom import *

from OCC.Core.GCE2d import *
from OCC.Core.gce import *


from OCC.Extend.ShapeFactory import make_vertex, make_edge2d


def print_click_pos(shape, *kwargs):
  for s in shape:
    print("Shape: ", s)
  print(kwargs)


display, start_display, add_menu, add_function_to_menu = init_display()

c = gp_Circ(gp_Ax2(gp_Pnt(200., 200., 0.), gp_Dir(0., 0., 1.)), 80)

ec = BRepBuilderAPI_MakeEdge(c).Edge()

axis = gp_OX2d()
circle = GCE2d_MakeCircle().Value()
trimmed_circle = Geom_TrimmedCurve(circle, 0, math.pi/2, True)
edge1 = BRepBuilderAPI_MakeEdge(trimmed_circle).Edge()
display.DisplayShape(edge1, update=True)


# ais_shp = AIS_Shape(ec)
# display.Context.Display(ais_shp, True)

rd = AIS_RadiusDimension(ec)
the_aspect = Prs3d_DimensionAspect()
the_aspect.SetCommonColor(Quantity_Color(Quantity_NOC_BLACK))
rd.SetDimensionAspect(the_aspect)

display.Context.Display(rd, True)
display.FitAll()

display.register_select_callback(print_click_pos)


start_display()
