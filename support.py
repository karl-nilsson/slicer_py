#!/usr/bin/env python3

import os
import sys
import time
import math

from OCC.Core.AIS import AIS_Line, AIS_Circle, AIS_Plane, AIS_Trihedron
from OCC.Core.BRep import BRep_Tool
from OCC.Core.Geom import Geom_Line
from OCC.Core.BRepAdaptor import BRepAdaptor_HCurve, BRepAdaptor_Surface
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
from OCC.Core.BRepFill import BRepFill_CurveConstraint
from OCC.Display.SimpleGui import init_display
from OCC.Core.GeomAbs import *
from OCC.Core.TopAbs import *
from OCC.Core.TopoDS import *
from OCC.Core.Prs3d import *
from OCC.Core.GeomLProp import GeomLProp_SLProps
from OCC.Core.GeomPlate import *
from OCC.Core.ShapeAnalysis import ShapeAnalysis_Surface, shapeanalysis_GetFaceUVBounds
from OCC.Core.gp import *
from OCC.Core.BRepFill import BRepFill_Filling
from OCC.Core.Graphic3d import Graphic3d_Structure

from OCC.Extend.TopologyUtils import TopologyExplorer, WireExplorer
from OCC.Extend.ShapeFactory import make_face, make_vertex
from OCC.Extend.DataExchange import read_step_file

display, start_display, add_menu, add_function_to_menu = init_display()

drawer = Prs3d_Drawer()


def display_arrow(point: gp_Pnt, direction: gp_Dir):
    """ displays arrow"""

    aStructure = Graphic3d_Structure(display._struc_mgr)


    Prs3d_Arrow.Draw(
        aStructure,
        # starting point is the arrow tip
        point.Translated(gp_Vec(direction)),
        direction,
        math.radians(10),
        # unit vector
        1
    )
    aStructure.Display()
    return aStructure


def normals(face: TopoDS_Face):
    """Docstring"""
    # surf = BRepAdaptor_Surface(face, True)
    surf = BRep_Tool().Surface(face)

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

    # need to filter for points inside of polygon

    for i in range(u_count + 1):
        u = u_min + i * u_interval

        for j in range(v_count + 1):

            v = v_min + j * v_interval

            props = GeomLProp_SLProps(surf, u, v, 1, 1e-6)

            normal = None
            if props.IsNormalDefined():
                normal = props.Normal()
                if face.Orientation() == TopAbs_REVERSED:
                    normal.Reverse()

            result.append((props.Value(), normal))
            # arrow = AIS_Line(Geom_Line(*result[-1]))

            display_arrow(*result[-1])

            # display.DisplayVector(normal, props.Value())

            display.DisplayShape(props.Value())

    return result




if __name__ == "__main__":
    
    # shape = read_step_file('res/cylinder.step')
    shape = read_step_file('res/support_test.step')
    # shape = read_step_file('res/text_test.step')

    faces = TopologyExplorer(shape).faces()

    for f in faces:
        surface = BRepAdaptor_Surface(f, True)
        normals(f)

    display.DisplayShape(shape, update=True)
    
    display.Repaint()

    start_display()