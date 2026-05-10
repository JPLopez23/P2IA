import pygame
import sys
import itertools
from generador_laberinto import kruskal, prim, Maze

ROWS, COLS = 25, 30
CELL = 20
MARGIN = 40
FPS_MAX = 60
STEPS_PER_FRAME = 3

BG          = (18,  18,  18)
WALL_COLOR  = (200, 200, 200)
CELL_OPEN   = (40,  40,  40)
CELL_ACTIVE = (255, 160,  0)
CELL_DONE   = (60,  100, 160)
TEXT_COLOR  = (230, 230, 230)
TITLE_COLOR = (255, 200,  60)

W_MAZE = COLS * CELL
H_MAZE = ROWS * CELL
WIN_W  = W_MAZE * 2 + MARGIN + 80
WIN_H  = H_MAZE + 120


def draw_maze(surface, maze, ox, oy, highlights=None):
    highlights = highlights or {}
    for r in range(maze.rows):
        for c in range(maze.cols):
            x = ox + c * CELL
            y = oy + r * CELL
            color = highlights.get((r, c), CELL_OPEN)
            pygame.draw.rect(surface, color, (x, y, CELL, CELL))

            if maze.has_wall(r, c, Maze.N):
                pygame.draw.line(surface, WALL_COLOR, (x, y), (x + CELL, y), 2)
            if maze.has_wall(r, c, Maze.S):
                pygame.draw.line(surface, WALL_COLOR, (x, y + CELL), (x + CELL, y + CELL), 2)
            if maze.has_wall(r, c, Maze.W):
                pygame.draw.line(surface, WALL_COLOR, (x, y), (x, y + CELL), 2)
            if maze.has_wall(r, c, Maze.E):
                pygame.draw.line(surface, WALL_COLOR, (x + CELL, y), (x + CELL, y + CELL), 2)


def draw_text(surface, text, x, y, font, color=TEXT_COLOR, center=False):
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.centerx = x
        rect.y = y
    else:
        rect.x = x
        rect.y = y
    surface.blit(surf, rect)


def run():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Problema 1 – Generación de Laberintos: Kruskal vs Prim")
    clock = pygame.time.Clock()
    font_title = pygame.font.SysFont("Arial", 22, bold=True)
    font_info  = pygame.font.SysFont("Arial", 16)

    def new_generators():
        gen_k = kruskal(ROWS, COLS)
        gen_p = prim(ROWS, COLS)
        maze_k = Maze(ROWS, COLS)
        maze_p = Maze(ROWS, COLS)
        return gen_k, gen_p, maze_k, maze_p

    gen_k, gen_p, maze_k, maze_p = new_generators()

    visited_k = set()
    visited_p = set()
    last_k = None
    last_p = None
    done_k = False
    done_p = False
    paused = False
    step_k = 0
    step_p = 0

    ox_k = 40
    ox_p = ox_k + W_MAZE + MARGIN
    oy   = 80

    while True:
        clock.tick(FPS_MAX)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.quit(); sys.exit()
                if event.key == pygame.K_SPACE:
                    paused = not paused
                if event.key == pygame.K_r:
                    gen_k, gen_p, maze_k, maze_p = new_generators()
                    visited_k.clear(); visited_p.clear()
                    last_k = last_p = None
                    done_k = done_p = False
                    step_k = step_p = 0

        if not paused:
            for _ in range(STEPS_PER_FRAME):
                if not done_k:
                    try:
                        maze_k, info = next(gen_k)
                        r1, c1, r2, c2 = info
                        visited_k.add((r1, c1))
                        visited_k.add((r2, c2))
                        last_k = (r2, c2)
                        step_k += 1
                    except StopIteration:
                        done_k = True
                        last_k = None

                if not done_p:
                    try:
                        maze_p, (nr, nc) = next(gen_p)
                        visited_p.add((nr, nc))
                        last_p = (nr, nc)
                        step_p += 1
                    except StopIteration:
                        done_p = True
                        last_p = None

        screen.fill(BG)

        draw_text(screen, "KRUSKAL", ox_k + W_MAZE // 2, 12, font_title, TITLE_COLOR, center=True)
        draw_text(screen, "PRIM",    ox_p + W_MAZE // 2, 12, font_title, TITLE_COLOR, center=True)

        hl_k = {cell: CELL_DONE for cell in visited_k}
        if last_k:
            hl_k[last_k] = CELL_ACTIVE

        hl_p = {cell: CELL_DONE for cell in visited_p}
        if last_p:
            hl_p[last_p] = CELL_ACTIVE

        draw_maze(screen, maze_k, ox_k, oy, hl_k)
        draw_maze(screen, maze_p, ox_p, oy, hl_p)

        state_k = "LISTO" if done_k else ("PAUSADO" if paused else "generando...")
        state_p = "LISTO" if done_p else ("PAUSADO" if paused else "generando...")
        y_info = oy + H_MAZE + 10
        draw_text(screen, f"Pasos: {step_k}  [{state_k}]",  ox_k, y_info, font_info)
        draw_text(screen, f"Pasos: {step_p}  [{state_p}]",  ox_p, y_info, font_info)

        hint = "ESPACIO=pausar  R=reiniciar  Q=salir"
        draw_text(screen, hint, WIN_W // 2, y_info + 26, font_info, center=True)

        pygame.display.flip()

if __name__ == "__main__":
    run()
