# %%
from bd_utils.debug import add_show
from ocp_vscode import *

import bd_utils as bdu
from build123d import *

# %%
bdu.init_show()
bdu.reset_camera()

width = 115
tent_angle = Vector(-3, -25)  # (tilt, tent)
height_offset = 0  # otherwise rubber foot hits table
bottom_expansion = 10
length_ratio = 0.4

wall_thickness = 14

screw_hole_r = (7 / 2) + 0.1
screw_hole_depth = 4.2

fillet_r = 8
bottom_chamfer = 10


def build_left_half():
    with BuildPart() as left_half:
        length = 135 - 25

        # profile
        with BuildSketch(mode=Mode.PRIVATE) as sk_profile:
            Rectangle(length, width, align=bdu.align2("--"))
        sk_profile = sk_profile.sketch

        # bottom
        with BuildSketch() as sk_bottom:
            add(sk_profile)
            offset(amount=bottom_expansion, kind=Kind.INTERSECTION)
            fillet(sk_bottom.vertices(), fillet_r)

        # top
        with BuildSketch(Rot(*tent_angle), mode=Mode.PRIVATE) as sk_top:
            add(sk_profile)
            fillet(sk_top.vertices(), fillet_r)
        sk_top = sk_top.sketch
        # offset top so lowest point is aligned with z=0
        bbox = sk_top.faces()[0].bounding_box()
        z_offset = abs(bbox.min.Z) + height_offset
        sk_top.move(Location((0, 0, z_offset)))
        add(sk_top)

        # create the solid
        loft()

        # cut through
        face_top = left_half.faces().sort_by(Axis.Z)[-1]
        plane_top = Plane(
            origin=(0, 0, z_offset),
            x_dir=(1, 0, 0),
            z_dir=face_top.normal_at(),
        )
        with BuildSketch(plane_top) as sk_cut:
            add(sk_profile)
            offset(amount=-wall_thickness)
            fillet(sk_cut.vertices(), fillet_r)
        extrude(dir=(0, 0, -1), until=Until.LAST, mode=Mode.SUBTRACT)

        # cut screw holes
        with Locations(plane_top):
            l1 = Vector(7.5 + 96, 7.4)
            with Locations(
                l1,
                l1 + (-2, 23.5 + 55 + 22.5),
            ) as locs:
                Hole(screw_hole_r, screw_hole_depth)

        # cut off left
        split(bisect_by=Plane.YZ.offset(length * (1 - length_ratio)))

        # cut scoop
        with Locations(Pos((0, bbox.max.Y / 2 + 5, 5))) as locs:
            Box(
                length=200,
                width=70,
                height=100,
                align=bdu.align3("-*-"),
                mode=Mode.SUBTRACT,
            )

        chamfer_edges = left_half.edges().filter_by(Axis.X).group_by(Axis.Z)[1]
        chamfer(chamfer_edges, bottom_chamfer)  # type: ignore
    left_half.part.label = "left_half"
    return left_half.part


def build_right_half():
    with BuildPart() as right_half:
        length = 154 - 25

        # profile
        with BuildSketch(mode=Mode.PRIVATE) as sk_profile:
            Rectangle(length, width, align=bdu.align2("+-"))
        sk_profile = sk_profile.sketch

        # bottom
        with BuildSketch() as sk_bottom:
            add(sk_profile)
            offset(amount=bottom_expansion, kind=Kind.INTERSECTION)
            fillet(sk_bottom.vertices(), fillet_r)

        # top
        tent_angle.Y *= -1
        with BuildSketch(Rot(*tent_angle), mode=Mode.PRIVATE) as sk_top:
            add(sk_profile)
            fillet(sk_top.vertices(), fillet_r)
        sk_top = sk_top.sketch
        # offset top so lowest point is aligned with z=0
        bbox = sk_top.faces()[0].bounding_box()
        z_offset = abs(bbox.min.Z) + height_offset
        sk_top.move(Location((0, 0, z_offset)))
        add(sk_top)

        # create the solid
        loft()

        # cut through
        face_top = right_half.faces().sort_by(Axis.Z)[-1]
        plane_top = Plane(
            origin=(0, 0, z_offset),
            x_dir=(1, 0, 0),
            z_dir=face_top.normal_at(),
        )
        with BuildSketch(plane_top) as sk_cut:
            add(sk_profile)
            offset(amount=-wall_thickness)
            fillet(sk_cut.vertices(), fillet_r)
        extrude(dir=(0, 0, -1), until=Until.LAST, mode=Mode.SUBTRACT)

        # cut screw holes
        with Locations(plane_top):
            l1 = Vector(-(7.6 + 115), 7.4)
            with Locations(
                l1,
                l1 + (12, 23.5 + 59 + 18.5),
            ) as locs:
                Hole(screw_hole_r, screw_hole_depth)

        # cut off left
        split(bisect_by=Plane.YZ.offset(-length * (1 - length_ratio)), keep=Keep.BOTTOM)

        # cut scoop
        with Locations(Pos((0, bbox.max.Y / 2 + 5, 5))) as locs:
            Box(
                length=200,
                width=70,
                height=100,
                align=bdu.align3("+*-"),
                mode=Mode.SUBTRACT,
            )

        chamfer_edges = right_half.edges().filter_by(Axis.X).group_by(Axis.Z)[1]
        chamfer(chamfer_edges, bottom_chamfer)  # type: ignore
    right_half.part.label = "right_half"
    return right_half.part


left_half = build_left_half()
right_half = build_right_half()

bdu.add_show(left_half)
bdu.add_show(right_half)
bdu.show_selected()

bbox = left_half.bounding_box()
print("### Left half")
print(f"Tent angle = {tent_angle}")
print(f"Height = {bbox.size.Z}\n")

bbox = right_half.bounding_box()
print("### Right half")
print(f"Tent angle = {tent_angle}")
print(f"Height = {bbox.size.Z}\n")


# %%
ENABLE_EXPORT = False
ENABLE_EXPORT = True

if ENABLE_EXPORT:
    left_half.export_step("export/uhk_stand_left_half.step")
    right_half.export_step("export/uhk_stand_right_half.step")
    print("EXPORTED")
