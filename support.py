#!/usr/bin/env python3

import os
import sys
import time

from OCC.Core.BRep import BRep_Tool
from OCC.Core.BRepAdaptor import BRepAdaptor_HCurve, BRepAdaptor_Surface
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
from OCC.Core.BRepFill import BRepFill_CurveConstraint
from OCC.Display.SimpleGui import init_display
from OCC.Core.GeomAbs import *
from OCC.Core.TopAbs import *
from OCC.Core.TopoDS import *
from OCC.Core.Prs3d import *
from OCC.Core.GeomLProp import GeomLProp_SLProps
from OCC.Core.GeomPlate import (
    GeomPlate_BuildPlateSurface,
    GeomPlate_PointConstraint,
    GeomPlate_MakeApprox,
)
from OCC.Core.ShapeAnalysis import ShapeAnalysis_Surface, shapeanalysis_GetFaceUVBounds
from OCC.Core.gp import gp_Pnt
from OCC.Core.BRepFill import BRepFill_Filling

from OCC.Extend.TopologyUtils import TopologyExplorer, WireExplorer
from OCC.Extend.ShapeFactory import make_face, make_vertex
from OCC.Extend.DataExchange import read_step_file

display, start_display, add_menu, add_function_to_menu = init_display()



def normals(face: TopoDS_Face, reverse = False):
    """Docstring"""
    # surface = BRepAdaptor_Surface(face, True)

    surface = BRep_Tool().Surface(face)

    # if surface.GetType() == GeomAbs_Plane:
    #     p = surface.Plane()
    #     d = p.Axis().Direction()
    #     if reverse:
    #         d = d.Reverse()

    #     return [(p.Location(), d)]

    u_min, u_max, v_min, v_max = shapeanalysis_GetFaceUVBounds(face)

    result = []

    u_count = v_count = 10
    u_interval = (u_max - u_min) // u_count
    v_interval = (v_max - v_min) // v_count

    for i in range(u_count + 1):
        u = u_min + i * u_interval

        for j in range(v_count + 1):

            v = v_min + j * v_interval

            props = GeomLProp_SLProps(surface, u, v, 1, 1e-6)

            normal = None
            if props.IsNormalDefined():
                normal = props.Normal()
                if face.Orientation() == TopAbs_REVERSED:
                    normal.Reverse()

            result.append((props.Value(), normal))
            display.DisplayShape(props.Value())

    return result




if __name__ == "__main__":
    
    shape = read_step_file('res/support_test.step')

    faces = TopologyExplorer(shape).faces()

    for f in faces:
        surface = BRepAdaptor_Surface(f, True)
        normals(f, f.Orientation == TopAbs_REVERSED)

    display.DisplayShape(shape, update=True)
    
    display.Repaint()

    start_display()