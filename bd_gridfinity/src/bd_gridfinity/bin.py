from turtle import width

from ocp_vscode import *

import bd_utils as bdu
from build123d import *

from . import baseplate
from .spec import *

tolerance_gap = 0.25 * MM

size = grid_unit - (tolerance_gap * 2)
corner_radius = baseplate.corner_radius - tolerance_gap

base_height_steps: list[tuple[float, float]] = [
    (0.25, 0),
    (2.15, 45),
    (1.8, 0),
    (0.8, 45),
]
base_height = sum([height for [height, taper] in base_height_steps])

floor_thickness = 1 * MM
assert floor_thickness < height_unit - base_height

lip_steps: list[tuple[float, float]] = [
    (0.7, 45),
    (1.8, 0),
    (1.9, 45),
]
lip_height = sum([height for [height, taper] in lip_steps])
lip_radius = 0.5 * MM
wall_width = sum([height for [height, taper] in lip_steps if taper == 45])


class Bin(BasePartObject):
    def __init__(
        self,
        x_units: int = 1,
        y_units: int = 1,
        height_units: int = 3,
        align: bdu.Align3Input | None = "**-",
    ):
        self.x_units = x_units
        self.y_units = y_units
        self.height_units = height_units
        self.body_height = height_units * height_unit - base_height

        super().__init__(
            self._build(),
            align=bdu.align3(align),  # type: ignore
        )

    @property
    def _top_face(self) -> Face:
        return bdu.axis_faces(Axis.Z)[-1]

    def _build(self) -> Part:
        with BuildPart() as builder:
            with GridLocations(
                x_spacing=grid_unit,
                y_spacing=grid_unit,
                x_count=self.x_units,
                y_count=self.y_units,
            ):
                BinBase(align="**+")

            with BuildPart() as body:
                with BuildSketch() as walls:
                    RectangleRounded(
                        width=self._get_body_size(self.x_units),
                        height=self._get_body_size(self.y_units),
                        radius=corner_radius,
                    )

                extrude(amount=self.body_height)
                offset(amount=-wall_width, openings=self._top_face)

            top_face = self._top_face
            with BuildSketch(
                Plane(origin=top_face.edges()[0] @ 0, x_dir=(1, 0, 0), z_dir=(0, -1, 0))
            ) as lip:
                with BuildLine() as lip_line:
                    l1 = Line((0, 0), (0, 4.4))
                    l2 = PolarLine(l1 @ 1, 1.9, -45, length_mode=LengthMode.HORIZONTAL)
                    l3 = PolarLine(l2 @ 1, -1.8, 90)
                    l4 = PolarLine(l3 @ 1, 0.7, -45, length_mode=LengthMode.HORIZONTAL)
                    l5 = Line(l4 @ 1, l1 @ 0)

                make_face()
                fillet(lip.vertices().sort_by(Axis.Y)[-1], lip_radius)

            sweep(path=top_face.outer_wire())

            # face = self._top_face
            # with BuildSketch(face) as lip:
            #     add(face)

            # extrude(amount=lip_steps[0][0], taper=lip_steps[0][1])

        return builder.part

    def _get_body_size(self, units: int) -> float:
        return units * size + ((units - 1) * tolerance_gap * 2)


class BinBase(BasePartObject):
    def __init__(
        self,
        align: bdu.Align3Input | None = "**-",
    ):
        super().__init__(
            self._build(),
            align=bdu.align3(align),  # type: ignore
        )

    def _build(self) -> Part:
        with BuildPart() as builder:
            with BuildSketch() as perimiter:
                RectangleRounded(
                    width=size,
                    height=size,
                    radius=corner_radius,
                )

            is_first = True
            for [amount, taper] in base_height_steps:
                to_extrude = perimiter.sketch if is_first else bdu.axis_faces(Axis.Z)[0]
                extrude(
                    to_extrude,
                    amount=amount,
                    taper=taper,
                    dir=bdu.Dir.DOWN,
                )
                is_first = False

            self._cut_magnet_holes()

        return builder.part

    def _cut_magnet_holes(self):
        face = bdu.axis_faces(Axis.Z)[0]
        with BuildSketch(face) as holes:
            with Locations(magnet_center):
                Circle((magnet_diameter + magnet_tolerance) / 2)

            mirror(about=Plane.XZ)
            mirror(about=Plane.YZ)

        edges = extrude(
            holes.sketch,
            amount=magnet_thickness,
            dir=bdu.Dir.UP,
            mode=Mode.SUBTRACT,
        ).edges()
        bottom_edges = edges.group_by(Axis.Z)[0]
        fillet(bottom_edges, magnet_hole_fillet)  # type: ignore
