from copy import deepcopy
import pygame
from random import choice

W, H = 8, 16
TILE = 30
GAME_RES = 2 * W * TILE, H * TILE
FPS = 60
PREVIEW_AREA_X = W * TILE + (GAME_RES[0] - W * TILE) // 2
PREVIEW_AREA_Y = GAME_RES[1] // 2
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
FIGURE_RECT = pygame.Rect(1, 1, TILE - 2, TILE - 2)

def choose_figure():
    return deepcopy(choice(FIGURES))

def out_of_bounds(r: pygame.Rect) -> bool:
    return r.x < 0 or r.x >= W or r.y >= H or field[r.y][r.x] is not None

def move_figure(figure: list[pygame.Rect], dx: int):
    original_figure = deepcopy(figure)
    for rect in figure:
        rect.x += dx
        if out_of_bounds(rect):
            return original_figure
    return figure

def drop_figure(figure: list[pygame.Rect]):
    original_figure = deepcopy(figure)
    for rect in figure:
        rect.y += 1
        if out_of_bounds(rect):
            return original_figure, True
    return figure, False

def rotate_figure(figure: list[pygame.Rect]):
    center = figure[0]
    original_figure = deepcopy(figure)
    for rect in figure[1:]:
        x = rect.x - center.x
        y = rect.y - center.y
        rect.x = center.x - y
        rect.y = center.y + x
        if out_of_bounds(rect):
            return original_figure
    return figure

def clear_lines(field: list[list[pygame.Color | None]]):
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
        pygame.draw.rect(game_sc, (40, 40, 40), rect, 1)

def draw_figure(figure: list[pygame.Rect]):
    for rect in figure:
        FIGURE_RECT.x = rect.x * TILE
        FIGURE_RECT.y = rect.y * TILE
        pygame.draw.rect(game_sc, figure_color, FIGURE_RECT)

def draw_field(field: list[list[pygame.Color | None]]):
    for y, row in enumerate(field):
        for x, col in enumerate(row):
            if col is not None:
                FIGURE_RECT.x, FIGURE_RECT.y = x * TILE, y * TILE
                pygame.draw.rect(game_sc, col, FIGURE_RECT)

def draw_next_figure(next_figure: list[pygame.Rect]):
    for rect in next_figure:
        FIGURE_RECT.x = int(PREVIEW_AREA_X + (rect.x - next_figure[0].x) * TILE)
        FIGURE_RECT.y = int(PREVIEW_AREA_Y + (rect.y - next_figure[0].y) * TILE)
        pygame.draw.rect(game_sc, next_figure_color, FIGURE_RECT)

def draw_score(score: int):
    font = pygame.font.SysFont("Press Start 2P, Courier New, monospace", 32)
    score_surf = font.render(f"Score: {score}", True, (255, 255, 255))
    score_rect = score_surf.get_rect()
    score_rect.topleft = (GAME_RES[0] - score_rect.width - 20, 20)
    game_sc.blit(score_surf, score_rect)

pygame.init()
game_sc = pygame.display.set_mode(GAME_RES)
clock = pygame.time.Clock()
field: list[list[pygame.Color | None]] = [[None for _ in range(W)] for _ in range(H)]
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
                figure = move_figure(figure, -1)
            elif event.key == pygame.K_RIGHT:
                figure = move_figure(figure, 1)
            elif event.key == pygame.K_DOWN:
                drop_limit = 100
            elif event.key == pygame.K_UP:
                figure = rotate_figure(figure)

    drop_count += drop_speed
    if drop_count > drop_limit:
        drop_count = 0
        figure, bumped = drop_figure(figure)
        if bumped:
            for rect in figure:
                field[rect.y][rect.x] = figure_color
            figure, figure_color = next_figure, next_figure_color
            next_figure, next_figure_color = choose_figure()
            drop_limit = 2000
            score += 1
            drop_speed += 1

    game_sc.fill("black")
    clear_lines(field)
    draw_grid()
    draw_figure(figure)
    draw_field(field)
    draw_next_figure(next_figure)
    draw_score(score)

    pygame.display.flip()
    clock.tick(FPS)
