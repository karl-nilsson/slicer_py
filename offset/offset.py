#!/usr/bin/env python3

import time
import sys

from OCC.Core.TopoDS import *
from OCC.Core.TopAbs import *
from OCC.Core.gp import *
from OCC.Core.BOPAlgo import *
from OCC.Core.BRep import BRep_Tool
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Section, BRepAlgoAPI_Common
from OCC.Core.BRepBuilderAPI import *
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakeOffset
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface, BRepAdaptor_Curve
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.GeomAbs import *
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
display, start_display, add_menu, add_function_to_menu = init_display(
    "qt-pyqt5")
QtCore, QtGui, QtWidgets, QtOpengl = get_qt_modules()

from OCC.Display.qtDisplay import qtViewer3d



def on_select(shapes: list[TopoDS_Shape]):
    '''Select callback, print shape details'''
    if len(shapes) < 1:
        return
    s = shapes[0]

    if s.ShapeType() == TopAbs_EDGE:

        tmp = BRepAdaptor_Curve(s)

        # display start and endpoints of curve
        start_point = tmp.Value(tmp.FirstParameter())
        end_point = tmp.Value(tmp.LastParameter())

        # default, orientation = forward
        start_color = 'Blue'
        end_color = 'Red'

        if s.Orientation() == TopAbs_REVERSED:
            start_color, end_color = end_color, start_color

        display.DisplayColoredShape(
            BRepBuilderAPI_MakeVertex(start_point).Vertex(), start_color)
        display.DisplayColoredShape(
            BRepBuilderAPI_MakeVertex(end_point).Vertex(), end_color)

        print(tmp.GetType().name)


def get_viewer():
    '''Get instance of viewer'''
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)
    widgets = app.topLevelWidgets()
    for w in widgets:
        if hasattr(w, "_menus"):
            viewer = w.findChild(qtViewer3d, "qt_viewer_3d")
            return viewer



def make_offsets(face: TopoDS_Face | TopoDS_Compound, num: int = 5, distance: float = 0.2):
    '''Offset wires'''

    result = []

    # recurse to sub-shapes
    if face.ShapeType() == TopAbs_COMPOUND:
        for fa in TopologyExplorer(face).faces():
            result.append(make_offsets(fa, num, distance))
        return result



    f = topods_Face(face)

    display.DisplayShape(f)

    # GeomAbs_Arc, _Tangent, or _Intersection
    offset = BRepOffsetAPI_MakeOffset(f, GeomAbs_Arc, False)

    result = []
    # perform offsets
    for i in range(num):
        offset.Perform(-distance * (i + 1))
        if offset.IsDone():
            result.append(offset.Shape())
            display.DisplayShape(offset.Shape(), update=True)
        else:
            pass

    return result



def slice_shape(shape: TopoDS_Shape | TopoDS_Compound | list | None):
    '''Split the shape into slices'''
    # keep track of time for perf
    init_time = time.time()
    # get the axis-aligned bounding box and dimensions of shape
    center, [dx, dy, dz], box_shp = get_aligned_boundingbox(shape)

    # create a splitting plane in the z center of the bounding box
    plane = gp_Pln(gp_Pnt(0., 0., center.Z()), gp.DZ())
    face = BRepBuilderAPI_MakeFace(plane).Shape()

    split_time = time.time()
    # perform intersection between plane and shape at center.z
    common = BRepAlgoAPI_Common(shape, face).Shape()

    print('offsetting wires')
    # loop over faces

    offset_time = time.time()
    wires = make_offsets(common, 10, 0.5)

    current_time = time.time()
    print('Splitting time: ', split_time - init_time)
    print('Offsetting time: ', offset_time - split_time)
    print('Display time: ', current_time - offset_time)
    print('Total time: ', current_time - init_time)
    viewer = get_viewer()
    viewer.sig_topods_selected.connect(on_select)
    start_display()


if __name__ == '__main__':

    'res/text_test.step'
    'res/cube2.step'
    s = read_step_file('res/holes.step')

    # display loaded shape, slightly transparent
    # sh = display.DisplayShape(s)[0]
    # display.Context.SetTransparency(sh, 0.8, True)

    slice_shape(s)

    display.Repaint()
    display.FitAll()
