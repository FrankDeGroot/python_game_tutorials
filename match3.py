import pygame as pg
from random import choice
from typing import Callable, NamedTuple

FIELD_WIDTH, FIELD_HEIGHT = FIELD_COUNT = 16, 16
CELL_SIZE = 32
CELL_DIM = [CELL_SIZE, CELL_SIZE]
AREA_SIZE = [count * CELL_SIZE for count in FIELD_COUNT]
COLORS = [
    pg.Color(0, 0, 255),
    pg.Color(0, 255, 0),
    pg.Color(0, 255, 255),
    pg.Color(255, 0, 0),
    pg.Color(255, 0, 255),
    pg.Color(255, 255, 0),
]

type Row = list[pg.Color]
type Field = list[Row]
type Selected = Cell | None
type Match = list[Cell]


class Cell(NamedTuple):
    col: int
    row: int


def random_field():
    return [[choice(COLORS) for _ in range(FIELD_WIDTH)] for _ in range(FIELD_HEIGHT)]


def draw_field(surface: pg.Surface, field: Field):
    for row_index, row in enumerate(field):
        for col_index, color in enumerate(row):
            pg.draw.rect(
                surface,
                color,
                pg.Rect(
                    col_index * CELL_SIZE, row_index * CELL_SIZE, CELL_SIZE, CELL_SIZE
                ),
            )


def to_index(pos: list[int]):
    col, row = [c // CELL_SIZE for c in pos]
    return Cell(col, row)


def is_adjacent(cell1: Cell, cell2: Cell):
    diff = [abs(p1 - p2) for p1, p2 in zip(cell1, cell2)]
    return sum(diff) == 1


def maybe_cell_color(field: Field, cell: Cell):
    if cell.row < 0 or cell.row >= FIELD_HEIGHT:
        return None
    row = field[cell.row]
    if cell.col < 0 or cell.col >= FIELD_WIDTH:
        return None
    return row[cell.col]


def sure_cell_color(field: Field, cell: Cell):
    return field[cell.row][cell.col]


def set_color(field: Field, cell: Cell, color: pg.Color):
    field[cell.row][cell.col] = color


def swap_colors(field: Field, cell1: Cell, cell2: Cell):
    color1 = sure_cell_color(field, cell1)
    color2 = sure_cell_color(field, cell2)
    set_color(field, cell1, color2)
    set_color(field, cell2, color1)


def while_same_color(field: Field, start: Cell, dir: Callable[[Cell], Cell]):
    color = sure_cell_color(field, start)
    cell = start
    while True:
        cell = dir(cell)
        if maybe_cell_color(field, cell) != color:
            break
        yield cell


def up(c: Cell):
    return Cell(c.col, c.row - 1)


def down(c: Cell):
    return Cell(c.col, c.row + 1)


def left(c: Cell):
    return Cell(c.col - 1, c.row)


def right(c: Cell):
    return Cell(c.col + 1, c.row)


def get_matches(field: Field, cell: Cell):
    def blup(dir: Callable[[Cell], Cell]):
        return list(c for c in while_same_color(field, cell, dir))

    hor = blup(left) + [cell] + blup(right)
    ver = blup(up) + [cell] + blup(down)
    return [s for s in [hor, ver] if len(s) > 2]


def remove_matches(field: Field, selected: Selected, pos: list[int]):
    if selected:
        next_selected = to_index(pos)
        if is_adjacent(selected, next_selected):
            swap_colors(field, selected, next_selected)
            matches = [
                match
                for cell in [selected, next_selected]
                for match in get_matches(field, cell)
            ]
            if matches:
                for match in matches:
                    for cell in match:
                        set_color(field, cell, pg.Color(0, 0, 0))
            else:
                swap_colors(field, selected, next_selected)
            return None
        else:
            return to_index(pos)
    else:
        return to_index(pos)


def main():
    pg.init()
    surface = pg.display.set_mode(AREA_SIZE)
    clock = pg.time.Clock()
    field = random_field()
    selected: Selected = None
    while True:
        for event in pg.event.get():
            match event.type:
                case pg.QUIT:
                    exit()
                case pg.MOUSEBUTTONDOWN:
                    selected = remove_matches(field, selected, event.pos)
                case _:
                    pass
        draw_field(surface, field)
        if selected:
            pg.draw.rect(
                surface,
                "white",
                pg.Rect(
                    [c * CELL_SIZE for c in selected],
                    CELL_DIM,
                ),
            )
            pg.draw.rect(
                surface,
                sure_cell_color(field, selected),
                pg.Rect(
                    [s * CELL_SIZE + 2 for s in selected], [c - 4 for c in CELL_DIM]
                ),
            )
        pg.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
