#!/usr/bin/env python3

import time
import sys
import multiprocessing
import os

from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepTools import breptools_Read
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.TopAbs import *
from OCC.Core.gp import gp_Pln, gp_Dir, gp_Pnt
from OCC.Core.BOPAlgo import BOPAlgo_Splitter
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Section
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakeOffset
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.GeomAbs import GeomAbs_Arc, GeomAbs_Intersection, GeomAbs_OffsetCurve, GeomAbs_Plane

from OCC.Display.SimpleGui import init_display

from OCC.Extend.ShapeFactory import get_aligned_boundingbox
from OCC.Extend.TopologyUtils import TopologyExplorer
from OCC.Extend.DataExchange import read_step_file


def drange(start, stop, step):
    ''' mimic numpy arange method for float lists
    '''
    float_list = []
    r = start
    while r <= stop-step:
        float_list.append(r)
        r += step
    return float_list

def make_planes(li):
    # Create Plane defined by a point and the perpendicular direction
    slices = []
    for z in li:
        #print 'slicing index:', z, 'sliced by process:', os.getpid()
        plane = gp_Pln(gp_Pnt(0., 0., z), gp_Dir(0., 0., 1.))
        face = BRepBuilderAPI_MakeFace(plane).Shape()
        # add tuple to result
        slices.append(face)
    return slices

def make_offsets(face, num, distance):
    offset = BRepOffsetAPI_MakeOffset(face, GeomAbs_Arc, False)

    for w in TopologyExplorer(face).wires():
        offset.AddWire(w)
    result = []
    
    for i in range(num):
        offset.Perform(-1 * distance * i)
        if offset.IsDone():
            result.append(offset.Shape())

    return result

def select_planes(solid, z):

    result = []

    # all face planes should be facing downward, parallel to XY plane
    d = gp_Dir(0., 0., -1.)

    for f in TopologyExplorer(solid).faces():
        surf = BRepAdaptor_Surface(f, True)
        if surf.GetType() != GeomAbs_Plane:
            continue
        pln = surf.Plane()
        location = pln.Location()
        normal = pln.Axis().Direction()

        if location.Z() in z and d.IsParallel(normal, 0.1):
            print("adding face")
            result.append(f)
        

    return result


def slice(shape, n_procs, compare_by_number_of_processors=False):
    center, [dx, dy, dz], box_shp = get_aligned_boundingbox(shape)
    z_min = center.Z() - dz / 2
    z_max = center.Z() + dz / 2

    # slice height in mm
    slice_height = 1
    # number of shells (offsets)
    num_shells = 3
    # distance between offsets
    shell_thickness = 0.4

    # dictionary of slicing planes, key = z height, value = slicing plane
    z = drange(z_min, z_max, slice_height);

    splitter = BOPAlgo_Splitter()
    splitter.AddArgument(shape)
    for p in make_planes(z):
        # add slice to splitter algo
        splitter.AddTool(p)

    init_time = time.time()  # for total time computation

    splitter.Perform()

    display, start_display, add_menu, add_function_to_menu = init_display()
#    print('displaying original shape')
#    display.DisplayShape(shape, update=True)
    print('finding faces')
    exp = TopExp_Explorer(splitter.Shape(), TopAbs_SOLID)
    faces = []
    while exp.More():
        faces.extend(select_planes(exp.Current(), z))
#        display.DisplayShape(exp.Current(), update=True)
        exp.Next();

    print('offsetting wires')
    offset_wires = []
    for f in faces:
        offset_wires.extend(make_offsets(f, num_shells, shell_thickness))

    print('displaying offsets')
    for w in offset_wires:
        display.DisplayShape(w, update=True)

    # update viewer when all is added:
    display.Repaint()
    total_time = time.time() - init_time
    print("%s necessary to perform slice with %s processor(s)." % (total_time, n_procs))
    start_display()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(1)
    if not os.path.isfile(sys.argv[1]):
        sys.exit(1)
    

    shape = read_step_file(sys.argv[1])
    # use compare_by_number_of_processors=True to see speed up
    # per number of processor added
    try:
        nprocs = multiprocessing.cpu_count()
    except Exception as ex:  # travis fails to run cpu_count
        print(ex)
        nprocs = 1
    except SystemExit:
        pass
    slice(shape, nprocs, compare_by_number_of_processors=False)
