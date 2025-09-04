from copy import deepcopy
import pygame
from random import choice

W, H = 8, 16
TILE = 30
GAME_RES = 2 * W * TILE, H * TILE
FPS = 60

pygame.init()
game_sc = pygame.display.set_mode(GAME_RES)
clock = pygame.time.Clock()

grid = [pygame.Rect(x * TILE, y * TILE, TILE, TILE) for x in range(W) for y in range(H)]

figures_pos = [
    ([(-1, 0), (-2, 0), (0, 0), (1, 0)], pygame.Color(255, 0, 0)),
    ([(0, -1), (-1, -1), (-1, 0), (0, 0)], pygame.Color(0, 255, 0)),
    ([(-1, 0), (-1, 1), (0, 0), (0, -1)], pygame.Color(0, 0, 255)),
    ([(0, 0), (-1, 0), (0, 1), (-1, -1)], pygame.Color(255, 255, 0)),
    ([(0, 0), (0, -1), (0, 1), (-1, -1)], pygame.Color(0, 255, 255)),
    ([(0, 0), (0, -1), (0, 1), (1, -1)], pygame.Color(255, 0, 255)),
    ([(0, 0), (0, -1), (0, 1), (-1, 0)], pygame.Color(255, 255, 255)),
]

figures = [
    ([pygame.Rect(x + W // 2, y + 1, 1, 1) for x, y in figure_shape], figure_color)
    for figure_shape, figure_color in figures_pos
]
figure_rect = pygame.Rect(0, 0, TILE - 2, TILE - 2)
field: list[list[pygame.Color | None]] = [[None for _ in range(W)] for _ in range(H)]

anim_count, anim_speed, anim_limit = 0, 60, 2000

next_figure, next_figure_color = deepcopy(choice(figures))
figure, figure_color = deepcopy(choice(figures))

score = 0  # Add this near the top, after other variables

def out_of_bounds(r: pygame.Rect) -> bool:
    return r.x < 0 or r.x >= W or r.y >= H or field[r.y][r.x] is not None

# Preview area for next_figure (fixed right-center position)
preview_area_x = W * TILE + (GAME_RES[0] - W * TILE) // 2
preview_area_y = (GAME_RES[1] // 2)

def move_figure(figure: list[pygame.Rect], dx: int):
    original_figure = deepcopy(figure)
    for rect in figure:
        rect.x += dx
        if out_of_bounds(rect):
            figure = original_figure
            break
    return figure

while True:
    rotate = False
    game_sc.fill("black")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                figure = move_figure(figure, -1)
            elif event.key == pygame.K_RIGHT:
                figure = move_figure(figure, 1)
            elif event.key == pygame.K_DOWN:
                anim_limit = 100
            elif event.key == pygame.K_UP:
                rotate = True

    anim_count += anim_speed
    if anim_count > anim_limit:
        anim_count = 0
        original_figure = deepcopy(figure)
        for rect in figure:
            rect.y += 1
            if out_of_bounds(rect):
                for orig_rect in original_figure:
                    field[orig_rect.y][orig_rect.x] = figure_color
                figure, figure_color = next_figure, next_figure_color
                next_figure, next_figure_color = deepcopy(choice(figures))
                anim_limit = 2000
                score += 1
                anim_speed += 1
                break

    if rotate:
        center = figure[0]
        original_figure = deepcopy(figure)
        for rect in figure[1:]:
            x = rect.x - center.x
            y = rect.y - center.y
            rect.x = center.x - y
            rect.y = center.y + x
            if out_of_bounds(rect) or out_of_bounds(rect):
                figure = original_figure
                break

    line = H - 1
    for row in range(H - 1, -1, -1):
        count = 0
        for i, col in enumerate(field[row]):
            if col is not None:
                count += 1
            field[line][i] = col
        if count < W:
            line -= 1

    for rect in grid:
        pygame.draw.rect(game_sc, (40, 40, 40), rect, 1)

    for rect in figure:
        figure_rect.x = rect.x * TILE
        figure_rect.y = rect.y * TILE
        pygame.draw.rect(game_sc, figure_color, figure_rect)

    for y, row in enumerate(field):
        for x, col in enumerate(row):
            if col is not None:
                figure_rect.x, figure_rect.y = x * TILE, y * TILE
                pygame.draw.rect(game_sc, col, figure_rect)

    for rect in next_figure:
        figure_rect.x = int(preview_area_x + (rect.x - next_figure[0].x) * TILE)
        figure_rect.y = int(preview_area_y + (rect.y - next_figure[0].y) * TILE)
        pygame.draw.rect(game_sc, next_figure_color, figure_rect)

    font = pygame.font.SysFont("Press Start 2P, Courier New, monospace", 32)
    score_surf = font.render(f"Score: {score}", True, (255, 255, 255))
    score_rect = score_surf.get_rect()
    score_rect.topleft = (GAME_RES[0] - score_rect.width - 20, 20)
    game_sc.blit(score_surf, score_rect)

    pygame.display.flip()
    clock.tick(FPS)
