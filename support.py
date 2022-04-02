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
    surface = BRepAdaptor_Surface(face, True)

    # if surface.GetType() == GeomAbs_Plane:
    #     p = surface.Plane()
    #     d = p.Axis().Direction()
    #     if reverse:
    #         d = d.Reverse()

    #     return [(p.Location(), d)]

    umin, umax, vmin, vmax = shapeanalysis_GetFaceUVBounds(surface)

    result = []

    for i in range(umin, umax, (umax - umin) / 10):
        for j in range(vmin, vmax, (vmax - vmin) / 10):
            props = GeomLProp_SLProps(surface, i, j, 1, 1e-6)
            
            n = None
            if props.IsNormalDefined:
                n = props.Normal()
                if reverse:
                    n.Reverse()

            result += (props.Value(), n)




def exit(event=None):
    sys.exit()


if __name__ == "__main__":
    
    shape = read_step_file('res/bridge_test.step')

    faces = TopologyExplorer(shape).faces()

    for f in faces:
        surface = BRepAdaptor_Surface(f, True)
        normals(surface, f.Orientation == TopAbs_REVERSED)


    start_display()