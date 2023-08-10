from typing import Any

import build123d as bd
import ocp_vscode as ocp

_to_show: list[tuple[Any, str | None]] = []


def init_show(
    axes=True,
    axes0=True,
    glass=True,
    helper_scale=2,
    reset_camera=False,
    collapse="R",
    **extra_defaults: Any,
):
    global _to_show
    _to_show = []

    ocp.reset_show()
    ocp.show_clear()
    ocp.set_defaults(
        axes=axes,
        axes0=axes0,
        glass=glass,
        helper_scale=helper_scale,
        reset_camera=reset_camera,
        collapse=collapse,
        **extra_defaults,
    )


def reset_camera():
    ocp.set_defaults(reset_camera=True)


def add_show(cad_obj: Any, name: str | None = None):
    _to_show.append((cad_obj, name))


def show_selected():
    import inspect

    locals = inspect.currentframe().f_back.f_locals  # type: ignore
    keys = list(locals.keys())
    values = list(locals.values())

    def get_name(value: Any) -> str | None:
        try:
            return keys[values.index(value)]
        except Exception:
            return None

    ocp.show(
        *[obj for obj, _ in _to_show],
        names=[get_name(obj) or name for obj, name in _to_show],
    )



def show_labeled():
    pass


def show_builders():
    show_classes = (bd.BuildPart, bd.BuildSketch, bd.BuildLine)
    to_show = [kv for kv in locals().items() if isinstance(kv[1], show_classes)]
    ocp.show(
        *[value for (_, value) in to_show],
        names=[name for (name, _) in to_show],
    )
