from copy import deepcopy
import pygame
from random import choice

W, H = 8, 16
TILE = 32
GAME_RES = 2 * W * TILE, H * TILE
FPS = 60
PREVIEW_AREA_X = W + W // 2
PREVIEW_AREA_Y = H // 2
GRID = [pygame.Rect(x * TILE, y * TILE, TILE, TILE) for x in range(W) for y in range(H)]
FIGURES_POS = [
    ([(-1, 0), (-2, 0), (0, 0), (1, 0)], pygame.Color(255, 0, 0)),
    ([(0, -1), (-1, -1), (-1, 0), (0, 0)], pygame.Color(0, 255, 0)),
    ([(-1, 0), (-1, 1), (0, 0), (0, -1)], pygame.Color(0, 0, 255)),
    ([(0, 0), (-1, 0), (0, 1), (-1, -1)], pygame.Color(255, 255, 0)),
    ([(0, 0), (0, -1), (0, 1), (-1, -1)], pygame.Color(0, 255, 255)),
    ([(0, 0), (0, -1), (0, 1), (1, -1)], pygame.Color(255, 0, 255)),
    ([(0, 0), (0, -1), (0, 1), (-1, 0)], pygame.Color(255, 255, 255)),
]
FIGURES = [
    ([pygame.Rect(x + W // 2, y + 1, 1, 1) for x, y in figure_shape], figure_color)
    for figure_shape, figure_color in FIGURES_POS
]

pygame.init()
display = pygame.display.set_mode(GAME_RES)

type Field = list[list[pygame.Color | None]]
type Figure = list[pygame.Rect]


def choose_figure():
    return deepcopy(choice(FIGURES))


def out_of_bounds(r: pygame.Rect, field: Field) -> bool:
    return r.x < 0 or r.x >= W or r.y >= H or field[r.y][r.x] is not None


def move_figure(figure: Figure, dx: int, field: Field):
    original_figure = deepcopy(figure)
    for rect in figure:
        rect.x += dx
        if out_of_bounds(rect, field):
            return original_figure
    return figure


def drop_figure(figure: Figure, field: Field):
    original_figure = deepcopy(figure)
    for rect in figure:
        rect.y += 1
        if out_of_bounds(rect, field):
            return original_figure, True
    return figure, False


def rotate_figure(figure: Figure, field: Field):
    center = figure[0]
    original_figure = deepcopy(figure)
    for rect in figure[1:]:
        x = rect.x - center.x
        y = rect.y - center.y
        rect.x = center.x - y
        rect.y = center.y + x
        if out_of_bounds(rect, field):
            return original_figure
    return figure


def clear_lines(field: Field):
    line = H - 1
    for row in range(H - 1, -1, -1):
        count = 0
        for i, col in enumerate(field[row]):
            if col is not None:
                count += 1
            field[line][i] = col
        if count < W:
            line -= 1


def draw_grid():
    for rect in GRID:
        pygame.draw.rect(display, (40, 40, 40), rect, 1)


def draw_tile(x: int, y: int, color: pygame.Color):
    pygame.draw.rect(
        display, color, pygame.Rect(x * TILE + 1, y * TILE + 1, TILE - 2, TILE - 2)
    )


def draw_figure(figure: Figure, figure_color: pygame.Color):
    for rect in figure:
        draw_tile(rect.x, rect.y, figure_color)


def draw_field(field: Field):
    for y, row in enumerate(field):
        for x, col in enumerate(row):
            if col is not None:
                draw_tile(x, y, col)


def draw_next_figure(next_figure: Figure, next_figure_color: pygame.Color):
    for rect in next_figure:
        draw_tile(
            PREVIEW_AREA_X + rect.x - next_figure[0].x,
            PREVIEW_AREA_Y + rect.y - next_figure[0].y,
            next_figure_color,
        )


def draw_score(score: int):
    font = pygame.font.SysFont("Press Start 2P, Courier New, monospace", 32)
    score_surf = font.render(f"Score: {score}", True, (255, 255, 255))
    score_rect = score_surf.get_rect()
    score_rect.topleft = (GAME_RES[0] - score_rect.width - 20, 20)
    display.blit(score_surf, score_rect)


def main():
    clock = pygame.time.Clock()
    field: Field = [[None for _ in range(W)] for _ in range(H)]
    drop_count, drop_speed, drop_limit = 0, 60, 2000
    next_figure, next_figure_color = choose_figure()
    figure, figure_color = choose_figure()
    score = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    figure = move_figure(figure, -1, field)
                elif event.key == pygame.K_RIGHT:
                    figure = move_figure(figure, 1, field)
                elif event.key == pygame.K_DOWN:
                    drop_limit = 100
                elif event.key == pygame.K_UP:
                    figure = rotate_figure(figure, field)

        drop_count += drop_speed
        if drop_count > drop_limit:
            drop_count = 0
            figure, bumped = drop_figure(figure, field)
            if bumped:
                for rect in figure:
                    field[rect.y][rect.x] = figure_color
                figure, figure_color = next_figure, next_figure_color
                next_figure, next_figure_color = choose_figure()
                drop_limit = 2000
                score += 1
                drop_speed += 1

        display.fill("black")
        clear_lines(field)
        draw_grid()
        draw_figure(figure, figure_color)
        draw_field(field)
        draw_next_figure(next_figure, next_figure_color)
        draw_score(score)

        pygame.display.flip()
        clock.tick(FPS)


main()
