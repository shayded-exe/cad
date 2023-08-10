from ocp_vscode import *

import bd_utils as bdu
from build123d import *

from .spec import *

height = 7.2 * MM

corner_radius = 4 * MM
wall_height_steps: list[tuple[float, float]] = [
    (2.15, 45),
    (1.8, 0),
    (0.7, 45),
    (0.25, 0),
]
wall_height = sum([height for [height, taper] in wall_height_steps])
assert wall_height > magnet_thickness
wall_width = sum([height for [height, taper] in wall_height_steps if taper == 45])
lip_width = 1.5 * MM
total_side_width = wall_width + lip_width
inner_wall_corner = bdu.vec2(grid_unit / 2 - wall_width)

magnet_pad_size = 9.6 * MM


class BaseplateUnit(BasePartObject):
    def __init__(
        self,
        align: bdu.Align3Input | None = '**-',
    ):
        super().__init__(
            self._build(),
            align=bdu.align3(align),  # type: ignore
        )

    @property
    def _main_work_face(self) -> Face:
        return bdu.axis_face_groups(Axis.Z)[1][0]

    def _build(self) -> Part:
        with BuildPart() as builder:
            Box(
                length=grid_unit,
                width=grid_unit,
                height=height,
                align=bdu.align3("***"),
            )

            self._cut_walls()
            self._cut_plate()
            self._cut_magnet_holes()

        return builder.part

    def _cut_walls(self):
        with BuildSketch(self._main_work_face) as perimiter:
            RectangleRounded(
                width=grid_unit,
                height=grid_unit,
                radius=corner_radius,
            )

        is_first = True
        for [amount, taper] in wall_height_steps:
            extrude(
                perimiter.sketch if is_first else self._main_work_face,
                amount=amount,
                taper=taper,
                dir=bdu.Dir.DOWN,
                mode=Mode.SUBTRACT,
            )
            is_first = False

    def _cut_plate(self):
        face = self._main_work_face
        with BuildSketch(face) as perimiter:
            add(face)
            offset(amount=-lip_width)

            with BuildSketch(face, mode=Mode.SUBTRACT) as pads:
                with Locations(inner_wall_corner):
                    Rectangle(
                        width=magnet_pad_size,
                        height=magnet_pad_size,
                        align=bdu.align2("++"),
                    )

                [inner_corner, *_] = pads.vertices().sort_by_distance((0, 0))
                fillet(inner_corner, radius=corner_radius)

                mirror(about=Plane.XZ)
                mirror(about=Plane.YZ)

        extrude(
            perimiter.sketch,
            dir=bdu.Dir.DOWN,
            until=Until.LAST,
            mode=Mode.SUBTRACT,
        )

    def _cut_magnet_holes(self):
        parent = BuildPart._get_context()
        with BuildPart(self._main_work_face, mode=Mode.SUBTRACT) as holes:
            holes.builder_parent = parent

            with Locations(magnet_center):
                Cylinder(
                    (magnet_diameter + magnet_tolerance) / 2,
                    magnet_thickness,
                    align=bdu.align3("**+"),
                )

            mirror(about=Plane.XZ)
            mirror(about=Plane.YZ)

        top_edges = holes.edges().group_by(Axis.Z)[-1]
        fillet(top_edges, magnet_hole_fillet)  # type: ignore


class Baseplate(BasePartObject):
    def __init__(
        self,
        x_units: int,
        y_units: int,
        align: bdu.Align3Input | None = '**-',
    ):
        self.x_units = x_units
        self.y_units = y_units

        super().__init__(
            self._build(),
            align=bdu.align3(align),  # type: ignore
        )

    def _build(self) -> Part:
        with BuildPart() as builder:
            with GridLocations(
                x_spacing=grid_unit,
                y_spacing=grid_unit,
                x_count=self.x_units,
                y_count=self.y_units,
            ):
                BaseplateUnit()

            self._cutout_dovetails()

        return builder.part

    def _cutout_dovetails(self) -> None:
        parent = BuildPart._get_context()
        with BuildPart(mode=Mode.SUBTRACT) as dovetails:
            dovetails.builder_parent = parent

            with GridLocations(
                grid_unit,
                (grid_unit * self.y_units),
                x_count=self.x_units,
                y_count=2,
            ):
                Dovetail()
            with GridLocations(
                (grid_unit * self.x_units),
                grid_unit,
                x_count=2,
                y_count=self.y_units,
            ):
                Dovetail(rotation=(0, 0, 90))


class Dovetail(BasePartObject):
    def __init__(
        self,
        rotation: RotationLike = (0, 0, 0),
        align: bdu.Align3Input | None = '**-',
        mode: Mode = Mode.ADD,
    ):
        self._width = 10 * MM
        self._height = total_side_width - 1
        self._depth = 2 * MM
        self._angle = 70

        super().__init__(
            self._build(),
            rotation=rotation,
            align=bdu.align3(align),  # type: ignore
            mode=mode,
        )

    def _build(self) -> Part:
        with BuildPart() as builder:
            with BuildSketch():
                Trapezoid(
                    width=self._width,
                    height=self._height,
                    left_side_angle=60,
                    rotation=180,
                    align=bdu.align2("*+"),
                )
                mirror(about=Plane.XZ)

            extrude(amount=self._depth)

        return builder.part
