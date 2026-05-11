import pygame
import sys
from generador_laberinto import kruskal_full, prim_full, Maze
from algoritmos_busqueda import bfs, dfs, ucs, astar

ROWS, COLS = 60, 80
CELL = 11
FPS_MAX = 60
EXPLORE_SPEED = 50

START = (0, 0)
GOAL  = (ROWS - 1, COLS - 1)

BG           = (18,  18,  18)
WALL_COLOR   = (180, 180, 180)
CELL_BG      = (35,  35,  35)
EXPLORED_COL = (60,  100, 180)
PATH_COL     = (255, 200,  0)
START_COL    = (0,   220,  80)
GOAL_COL     = (220,  60,  60)
TEXT_COLOR   = (230, 230, 230)
TITLE_COLOR  = (255, 200,  60)
PANEL_BG     = (28,  28,  28)

W_MAZE = COLS * CELL
H_MAZE = ROWS * CELL
PANEL_H = 110
WIN_W  = W_MAZE + 2
WIN_H  = H_MAZE + PANEL_H + 2


def draw_maze_bg(surface, maze, ox, oy):
    for r in range(maze.rows):
        for c in range(maze.cols):
            x = ox + c * CELL
            y = oy + r * CELL
            pygame.draw.rect(surface, CELL_BG, (x, y, CELL, CELL))
            if maze.has_wall(r, c, Maze.N):
                pygame.draw.line(surface, WALL_COLOR, (x, y), (x + CELL, y), 1)
            if maze.has_wall(r, c, Maze.S):
                pygame.draw.line(surface, WALL_COLOR, (x, y + CELL), (x + CELL, y + CELL), 1)
            if maze.has_wall(r, c, Maze.W):
                pygame.draw.line(surface, WALL_COLOR, (x, y), (x, y + CELL), 1)
            if maze.has_wall(r, c, Maze.E):
                pygame.draw.line(surface, WALL_COLOR, (x + CELL, y), (x + CELL, y + CELL), 1)


def draw_cell(surface, r, c, ox, oy, color):
    x = ox + c * CELL + 1
    y = oy + r * CELL + 1
    pygame.draw.rect(surface, color, (x, y, CELL - 1, CELL - 1))


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


ALG_NAMES = {pygame.K_1: "BFS", pygame.K_2: "DFS", pygame.K_3: "UCS", pygame.K_4: "A*"}
ALG_FUNCS = {"BFS": bfs, "DFS": dfs, "UCS": ucs, "A*": astar}
GEN_NAMES = {pygame.K_g: "Kruskal", pygame.K_p: "Prim"}


def generate_maze(gen_name):
    if gen_name == "Kruskal":
        return kruskal_full(ROWS, COLS)
    return prim_full(ROWS, COLS)


def run():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Problema 2 – Resolución de Laberinto 60×80")
    clock = pygame.time.Clock()
    font_title = pygame.font.SysFont("Arial", 17, bold=True)
    font_info  = pygame.font.SysFont("Arial", 14)

    gen_name = "Kruskal"
    alg_name = "A*"
    maze = generate_maze(gen_name)

    explored_order = []
    path = []
    stats = {}
    anim_idx = 0
    phase = "idle"
    paused = False

    maze_surf = pygame.Surface((W_MAZE + 2, H_MAZE + 2))

    def rebuild_maze_surf():
        maze_surf.fill(BG)
        draw_maze_bg(maze_surf, maze, 1, 1)

    def start_search():
        nonlocal explored_order, path, stats, anim_idx, phase
        fn = ALG_FUNCS[alg_name]
        path, explored_order, stats = fn(maze, START, GOAL)
        path = path or []
        anim_idx = 0
        phase = "exploring"

    rebuild_maze_surf()
    oy = 0

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
                    maze = generate_maze(gen_name)
                    rebuild_maze_surf()
                    explored_order = []; path = []; stats = {}
                    anim_idx = 0; phase = "idle"; paused = False
                if event.key in ALG_NAMES:
                    alg_name = ALG_NAMES[event.key]
                    explored_order = []; path = []; stats = {}
                    anim_idx = 0; phase = "idle"; paused = False
                if event.key in GEN_NAMES:
                    gen_name = GEN_NAMES[event.key]
                    maze = generate_maze(gen_name)
                    rebuild_maze_surf()
                    explored_order = []; path = []; stats = {}
                    anim_idx = 0; phase = "idle"; paused = False
                if event.key == pygame.K_RETURN:
                    if phase == "idle":
                        start_search()

        if phase == "exploring" and not paused:
            for _ in range(EXPLORE_SPEED):
                if anim_idx < len(explored_order):
                    anim_idx += 1
                else:
                    phase = "done"
                    break

        screen.fill(BG)
        screen.blit(maze_surf, (0, oy))

        for i in range(min(anim_idx, len(explored_order))):
            r, c = explored_order[i]
            draw_cell(screen, r, c, 1, oy + 1, EXPLORED_COL)

        if phase == "done":
            for r, c in path:
                draw_cell(screen, r, c, 1, oy + 1, PATH_COL)

        draw_cell(screen, START[0], START[1], 1, oy + 1, START_COL)
        draw_cell(screen, GOAL[0],  GOAL[1],  1, oy + 1, GOAL_COL)

        panel_y = H_MAZE + 2
        pygame.draw.rect(screen, PANEL_BG, (0, panel_y, WIN_W, PANEL_H))

        title = f"Laberinto 60×80 | Generador: {gen_name} | Algoritmo: {alg_name}"
        draw_text(screen, title, WIN_W // 2, panel_y + 6, font_title, TITLE_COLOR, center=True)

        if stats:
            s1 = f"Longitud del camino: {stats['path_length']} pasos"
            s2 = f"Nodos explorados: {stats['nodes_explored']}"
            s3 = f"Tiempo: {stats['time_ms']:.2f} ms"
            draw_text(screen, s1, 20,  panel_y + 30, font_info)
            draw_text(screen, s2, 220, panel_y + 30, font_info)
            draw_text(screen, s3, 440, panel_y + 30, font_info)

        status = ""
        if phase == "idle":
            status = "ENTER=iniciar búsqueda"
        elif phase == "exploring":
            pct = int(anim_idx / max(len(explored_order), 1) * 100)
            status = f"Explorando... {pct}%  {'(PAUSADO)' if paused else ''}"
        elif phase == "done":
            status = "COMPLETO"

        draw_text(screen, status, WIN_W // 2, panel_y + 54, font_info, center=True)
        hint = "1=BFS  2=DFS  3=UCS  4=A*  |  G=Kruskal  P=Prim  |  R=nuevo  ESPACIO=pausar  Q=salir"
        draw_text(screen, hint, WIN_W // 2, panel_y + 78, font_info, color=(160, 160, 160), center=True)

        pygame.display.flip()

if __name__ == "__main__":
    run()
