#!/usr/bin/env python3
from __future__ import annotations

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

from OCC.Core.BOPTools import BOPTools_AlgoTools3D
from OCC.Core.IntTools import IntTools_Context

from OCC.Extend.TopologyUtils import TopologyExplorer, WireExplorer
from OCC.Extend.ShapeFactory import make_face, make_vertex
from OCC.Extend.DataExchange import read_step_file

display, start_display, add_menu, add_function_to_menu = init_display()

drawer = Prs3d_Drawer()

face_normal_map: dict[TopoDS_Shape, list[tuple[gp_Pnt, gp_Dir]]] = {}


def display_arrow(point: gp_Pnt, direction: gp_Dir) -> None:
    """displays arrow"""

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


def normals(face: TopoDS_Face) -> list[tuple[gp_Pnt, gp_Dir]]:
    """Docstring"""
    # surf = BRepAdaptor_Surface(face, True)
    surf = BRep_Tool().Surface(face)

    # if surface.GetType() == GeomAbs_Plane:
    #     p = surface.Plane()
    #     d = p.Axis().Direction()
    #     if reverse:
    #         d = d.Reverse()

    #     return [(p.Location(), d)]

    # may not work, face may be mutable
    face_normal_map[face] = []

    u_min, u_max, v_min, v_max = shapeanalysis_GetFaceUVBounds(face)

    result = []

    u_count = v_count = 10
    u_interval = (u_max - u_min) // u_count
    v_interval = (v_max - v_min) // v_count

    # need to filter for points inside of polygon
    context = IntTools_Context()
    # promising...
    tmp = context.SurfaceData(face)

    # for whatever reason, this calculates a different value than _getfaceUVbounds
    # specifically, it doesn't return values <0
    uu, uuu, vv, vvv = context.UVBounds(face)

    for i in range(u_count + 1):
        u = u_min + i * u_interval

        for j in range(v_count + 1):

            v = v_min + j * v_interval

            props = GeomLProp_SLProps(surf, u, v, 1, 1e-6)

            # calculate 3d point on face
            tmp = gp_Pnt2d() # dummy var
            retval = BOPTools_AlgoTools3D.PointInFace(face, props.Value(), tmp, context)
            # if failed, skip
            if retval:
                continue

            # this returns false
            r = context.IsPointInFace(props.Value(), face, 1e-6)
            # if not r:
            #     continue
            # but this returns true
            r = context.IsValidPointForFace(props.Value(), face, 1e-6)

            if not r:
                continue

            n = gp_Dir()
            # z = BOPTools_AlgoTools3D.GetNormalToSurface(surf, u, v, n)

            normal = None
            if props.IsNormalDefined():
                normal = props.Normal()
                if face.Orientation() == TopAbs_REVERSED:
                    normal.Reverse()

            result.append((props.Value(), normal))
            # arrow = AIS_Line(Geom_Line(*result[-1]))

            # display_arrow(*result[-1])

            # display.DisplayShape(props.Value())

    return result


def selected(item: TopoDS_Shape):
    """Selection callback"""
    # display normals of selected face
    if face_normal_map.get(item):
        for n in face_normal_map[item]:
            display_arrow(*n)



if __name__ == "__main__":
    
    # shape = read_step_file('res/cylinder.step')
    # shape = read_step_file('res/cylinder_weird.step')
    shape = read_step_file('res/support_test.step')
    # shape = read_step_file('res/text_test.step')

    faces = TopologyExplorer(shape).faces()

    i = 0

    for f in faces:
        face_normal_map[f] = normals(f)
        i += 1
    
    print(f"Number of faces: {i+1}")

    display.DisplayShape(shape, update=True)
    
    display.Repaint()

    start_display()