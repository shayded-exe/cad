from typing import Literal, LiteralString, TypeAlias, overload

import build123d as bd

AlignChar: TypeAlias = Literal["-", "*", "+"]
Align2: TypeAlias = tuple[bd.Align, bd.Align]
Align3: TypeAlias = tuple[bd.Align, bd.Align, bd.Align]
Align2Input: TypeAlias = bd.Align | Align2 | LiteralString
Align3Input: TypeAlias = bd.Align | Align3 | LiteralString


@overload
def align2(input: Align2Input) -> Align2: ...
@overload
def align2(input: None) -> None: ...
def align2(input: Align2Input | None) -> Align2 | None:
    match input:
        case bd.Align():
            return (input, input)
        case tuple():
            return input
        case str() if len(input) == 2:
            return tuple(map(char_to_align, input))
        case None:
            return None
        case _:
            raise Exception(f"Invalid align input {input}")


@overload
def align3(input: Align3Input) -> Align3: ...
@overload
def align3(input: None) -> None: ...
def align3(input: Align3Input | None) -> Align3 | None:
    match input:
        case bd.Align():
            return (input, input, input)
        case tuple():
            return input
        case str() if len(input) == 3:
            return tuple(map(char_to_align, input))
        case None:
            return None
        case _:
            raise Exception(f"Invalid align input {input}")


def char_to_align(char: str) -> bd.Align:
    match char:
        case "-":
            return bd.Align.MIN
        case "*":
            return bd.Align.CENTER
        case "+":
            return bd.Align.MAX
        case _:
            raise Exception(f"Invalid align shorthand {char}")


def vec2(value: float) -> bd.Vector:
    return bd.Vector(value, value)


def vec3(value: float) -> bd.Vector:
    return bd.Vector(value, value, value)


class Dir:
    UP = (0, 0, 1)
    DOWN = (0, 0, -1)
    RIGHT = (1, 0, 0)
    LEFT = (-1, 0, 0)
    FORWARD = (1, 0, 0)
    BACK = (-1, 0, 0)
