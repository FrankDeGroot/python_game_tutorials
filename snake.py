import pygame as pg
from random import randrange

WINDOW_SIZE = 750
TILE_SIZE = 50
RANGE = (TILE_SIZE // 2, WINDOW_SIZE - TILE_SIZE // 2, TILE_SIZE)

def get_random_position() -> tuple[int, int]:
    return (randrange(*RANGE), randrange(*RANGE))

snake = pg.rect.Rect([0, 0, TILE_SIZE - 2, TILE_SIZE - 2])
snake.center = get_random_position()
length = 1
segments = [snake.copy()]
snake_dir = (0, 0)
time, time_step = 0, 110
food = snake.copy()
food.center = get_random_position()
screen = pg.display.set_mode([WINDOW_SIZE] * 2)
clock = pg.time.Clock()

while True:
    for event in pg.event.get():
        match event.type:
            case pg.QUIT:
                exit()
            case pg.KEYDOWN:
                (x, y) = snake_dir
                match event.key:
                    case pg.K_w if y <= 0:
                        snake_dir = (0, -TILE_SIZE)
                    case pg.K_s if y >= 0:
                        snake_dir = (0, TILE_SIZE)
                    case pg.K_a if x <= 0:
                        snake_dir = (-TILE_SIZE, 0)
                    case pg.K_d if x >= 0:
                        snake_dir = (TILE_SIZE, 0)
                    case _:
                        pass
            case _:
                pass
    screen.fill('black')
    self_eating = pg.Rect.collidelist(snake, segments[:-1]) != -1
    if snake.left < 0 or snake.right > WINDOW_SIZE or snake.top < 0 or snake.bottom > WINDOW_SIZE or self_eating:
        snake.center, food.center = get_random_position(), get_random_position()
        length, snake_dir = 1, (0, 0)
        segments = [snake.copy()]     
    if snake.center == food.center:
        food.center = get_random_position()
        length += 1
    pg.draw.rect(screen, 'red', food)
    [pg.draw.rect(screen, 'green', segment) for segment in segments]
    time_now = pg.time.get_ticks()
    if time_now - time > time_step:
        time = time_now
        snake.move_ip(snake_dir)
        segments.append(snake.copy())
        segments = segments[-length:]
    pg.display.flip()
    clock.tick(60)