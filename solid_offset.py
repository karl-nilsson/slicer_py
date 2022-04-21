from OCC.Core.BRep import BRep_Tool_Surface
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Section, BRepAlgoAPI_Fuse
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakeWire,
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_GTransform,
)
from OCC.Core.BRepFeat import (
    BRepFeat_MakePrism,
    BRepFeat_MakeDPrism,
    BRepFeat_SplitShape,
    BRepFeat_MakeLinearForm,
    BRepFeat_MakeRevol,
)
from OCC.Core.BRepLib import breplib_BuildCurves3d
from OCC.Core.BRepOffset import BRepOffset_Skin
from OCC.Core.BRepOffsetAPI import (
    BRepOffsetAPI_MakeThickSolid,
    BRepOffsetAPI_MakeOffsetShape,
)
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakePrism
from OCC.Display.SimpleGui import init_display
from OCC.Core.GCE2d import GCE2d_MakeLine
from OCC.Core.Geom import Geom_Plane
from OCC.Core.Geom2d import Geom2d_Circle
from OCC.Core.GeomAbs import GeomAbs_Arc
from OCC.Core.TopTools import TopTools_ListOfShape
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.gp import (
    gp_Pnt2d,
    gp_Circ2d,
    gp_Ax2d,
    gp_Dir2d,
    gp_Pnt,
    gp_Pln,
    gp_Vec,
    gp_OX,
    gp_Trsf,
    gp_GTrsf,
)
from OCC.Extend.DataExchange import read_step_file


from OCC.Extend.TopologyUtils import TopologyExplorer

display, start_display, add_menu, add_function_to_menu = init_display()

def offset_shape(s: TopoDS_Shape):
    offsetB = BRepOffsetAPI_MakeOffsetShape(
        s, -20, 0.01, BRepOffset_Skin, False, False, GeomAbs_Arc
    )
    offB = display.DisplayColoredShape(s, "BLUE")[0]
    display.Context.SetTransparency(offB, 0.3, True)
    display.DisplayColoredShape(offsetB.Shape(), "GREEN")
    display.FitAll()

if __name__ == "__main__":

    # shape = read_step_file('res/concave_solid_offset.step')
    shape = read_step_file('res/cube.step')

    offset_shape(shape)

    start_display()
