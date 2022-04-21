# Support generation


## Steps

1. Identify overhanging faces/regions
    - consider meshing solid (netgen), then using result to identify overhangs
    - [subdivide faces](https://dev.opencascade.org/doc/overview/html/occt_user_guides__shape_healing.html#occt_shg_4_3_6)
1. Group adjacent overhanging faces
1. blahblah


- BRepOffsetAPI_MakeEvolved
- BRepOffsetAPI_MakePipe
- BRepFeat_MakePipe

Resources:
[cura](https://github.com/Ultimaker/Cura/issues/3557)