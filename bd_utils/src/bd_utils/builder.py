import build123d as bd


def get_part_or_fail() -> bd.BuildPart:
    part = bd.BuildPart._get_context("get_part_or_fail")
    if part is None:
        raise ValueError("part must be provided")

    return part


def axis_faces(
    axis: bd.Axis, part: bd.BuildPart | None = None
) -> bd.ShapeList[bd.Face]:
    part = part or get_part_or_fail()

    return part.faces().filter_by(axis).sort_by(axis)


def axis_face_groups(
    axis: bd.Axis, part: bd.BuildPart | None = None
) -> list[bd.ShapeList[bd.Face]]:
    part = part or get_part_or_fail()
    faces = part.faces().filter_by(axis).group_by(axis)

    return faces  # type: ignore


# def with_parent(builder: bd_common.Builder) -> bd_common.Builder:
#     parent = bd_common.Builder._get_context()
#     builder.__enter__ = ...
