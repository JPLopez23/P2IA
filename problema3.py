import pygame
import sys
import random
from generador_laberinto import kruskal_full, prim_full, Maze
from algoritmos_busqueda import bfs, dfs, ucs, astar

ROWS, COLS    = 45, 55
K             = 25
CELL          = 9
MIN_MANHATTAN = 10
EXPLORE_SPEED = 35

ALGOS = [("BFS", bfs), ("DFS", dfs), ("UCS", ucs), ("A*", astar)]

ALGO_COLORS = {
    "BFS": (70,  130, 220),
    "DFS": (200,  80,  80),
    "UCS": (80,  180, 100),
    "A*":  (220, 160,  30),
}
PATH_COLORS = {
    "BFS": (140, 200, 255),
    "DFS": (255, 150, 150),
    "UCS": (150, 255, 180),
    "A*":  (255, 230, 100),
}

BG         = (18,  18,  18)
WALL_COLOR = (160, 160, 160)
CELL_BG    = (35,  35,  35)
TEXT_COL   = (230, 230, 230)
TITLE_COL  = (255, 200,  60)
PANEL_BG   = (28,  28,  28)
TABLE_HDR  = (50,  50,  70)
TABLE_ROW  = (38,  38,  50)
TABLE_ALT  = (32,  32,  44)
BORDER_COL = (80,  80, 110)
START_COL  = (0,   220,  80)
GOAL_COL   = (220,  60,  60)
RANK_COLS  = {1: (255, 215, 0), 2: (192, 192, 192), 3: (205, 127, 50), 4: (140, 80, 80)}

W_GRID = COLS * CELL
H_GRID = ROWS * CELL
GAP    = 12
TABLE_W = 310
BOTTOM_H = 52

WIN_W = W_GRID * 2 + GAP * 3 + TABLE_W
WIN_H = H_GRID * 2 + GAP * 3 + BOTTOM_H

MAZE_OX = [GAP, W_GRID + GAP * 2, GAP, W_GRID + GAP * 2]
MAZE_OY = [GAP, GAP, H_GRID + GAP * 2, H_GRID + GAP * 2]
TABLE_OX = W_GRID * 2 + GAP * 3
TABLE_OY = GAP


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def random_pair(rows, cols, min_dist):
    while True:
        r1, c1 = random.randrange(rows), random.randrange(cols)
        r2, c2 = random.randrange(rows), random.randrange(cols)
        if manhattan((r1, c1), (r2, c2)) >= min_dist:
            return (r1, c1), (r2, c2)


def generate_scenario():
    gen_fn = random.choice([kruskal_full, prim_full])
    maze = gen_fn(ROWS, COLS)
    start, goal = random_pair(ROWS, COLS, MIN_MANHATTAN)
    results = {}
    for name, fn in ALGOS:
        path, explored, stats = fn(maze, start, goal)
        results[name] = {"path": path or [], "explored": explored, "stats": stats}
    return maze, start, goal, results


def rank_scenario(results):
    order = sorted(ALGOS, key=lambda x: results[x[0]]["stats"]["nodes_explored"])
    return {name: rank + 1 for rank, (name, _) in enumerate(order)}


def draw_maze_surf(maze):
    surf = pygame.Surface((W_GRID, H_GRID))
    surf.fill(CELL_BG)
    for r in range(maze.rows):
        for c in range(maze.cols):
            x, y = c * CELL, r * CELL
            if maze.has_wall(r, c, Maze.N):
                pygame.draw.line(surf, WALL_COLOR, (x, y),        (x + CELL, y),        1)
            if maze.has_wall(r, c, Maze.S):
                pygame.draw.line(surf, WALL_COLOR, (x, y + CELL), (x + CELL, y + CELL), 1)
            if maze.has_wall(r, c, Maze.W):
                pygame.draw.line(surf, WALL_COLOR, (x, y),        (x, y + CELL),        1)
            if maze.has_wall(r, c, Maze.E):
                pygame.draw.line(surf, WALL_COLOR, (x + CELL, y), (x + CELL, y + CELL), 1)
    return surf


def paint_cells(surf, cells, color):
    for r, c in cells:
        pygame.draw.rect(surf, color, (c * CELL + 1, r * CELL + 1, CELL - 1, CELL - 1))


def draw_text(surface, text, x, y, font, color=TEXT_COL, center=False, right=False):
    s = font.render(text, True, color)
    rect = s.get_rect()
    if center:
        rect.centerx = x
        rect.y = y
    elif right:
        rect.right = x
        rect.y = y
    else:
        rect.x = x
        rect.y = y
    surface.blit(s, rect)


def draw_scenario_table(screen, results, ranks, anim_complete, font_hdr, font_row, ox, oy):
    w = TABLE_W
    row_h = 34
    col_w = [70, 62, 62, 62, 50]
    headers = ["Algo", "Dist", "Nodos", "Tiempo", "Rank"]

    draw_text(screen, "Comparación por escenario", ox + w // 2, oy, font_hdr, TITLE_COL, center=True)
    oy += 28

    total_h = row_h * (len(ALGOS) + 1) + 4
    pygame.draw.rect(screen, BORDER_COL, (ox, oy, w, total_h), 1)

    pygame.draw.rect(screen, TABLE_HDR, (ox + 1, oy + 1, w - 2, row_h - 1))
    cx = ox + 4
    for i, h in enumerate(headers):
        draw_text(screen, h, cx + col_w[i] // 2, oy + 9, font_hdr, TITLE_COL, center=True)
        cx += col_w[i]
    oy += row_h

    algo_order = sorted([n for n, _ in ALGOS], key=lambda n: ranks[n])

    for idx, name in enumerate(algo_order):
        st = results[name]["stats"]
        rank = ranks[name]
        row_color = TABLE_ROW if idx % 2 == 0 else TABLE_ALT
        pygame.draw.rect(screen, row_color, (ox + 1, oy + 1, w - 2, row_h - 1))

        values = [
            name,
            str(st["path_length"]) if anim_complete else "...",
            str(st["nodes_explored"]) if anim_complete else "...",
            f"{st['time_ms']:.2f}" if anim_complete else "...",
            f"#{rank}" if anim_complete else "...",
        ]
        colors_row = [
            ALGO_COLORS[name],
            TEXT_COL, TEXT_COL, TEXT_COL,
            RANK_COLS.get(rank, TEXT_COL),
        ]

        cx = ox + 4
        for i, val in enumerate(values):
            draw_text(screen, val, cx + col_w[i] // 2, oy + 9, font_row, colors_row[i], center=True)
            cx += col_w[i]

        pygame.draw.line(screen, BORDER_COL, (ox + 1, oy + row_h), (ox + w - 1, oy + row_h), 1)
        oy += row_h

    return oy


def draw_summary_table(screen, scenarios, all_ranks, font_title, font_hdr, font_row):
    screen.fill(BG)
    title = "TABLA RESUMEN  –  Ranking promedio (K=25 laberintos  45×55)"
    draw_text(screen, title, WIN_W // 2, 28, font_title, TITLE_COL, center=True)

    col_labels = ["Algoritmo", "Rank Prom.", "# Veces 1°", "# Veces 4°", "Dist Prom.", "Nodos Prom."]
    col_x = [80, 240, 360, 470, 580, 700]
    row_h = 42
    y0 = 90

    pygame.draw.rect(screen, TABLE_HDR, (60, y0 - 6, 720, row_h))
    for i, lbl in enumerate(col_labels):
        draw_text(screen, lbl, col_x[i], y0 + 4, font_hdr, TITLE_COL)

    pygame.draw.line(screen, BORDER_COL, (60, y0 + row_h - 2), (780, y0 + row_h - 2), 1)

    algo_names = [n for n, _ in ALGOS]
    avg_rank   = {n: sum(r[n] for r in all_ranks) / K for n in algo_names}
    best_count = {n: sum(1 for r in all_ranks if r[n] == 1) for n in algo_names}
    worst_count= {n: sum(1 for r in all_ranks if r[n] == 4) for n in algo_names}
    avg_dist   = {n: sum(sc[3][n]["stats"]["path_length"] for sc in scenarios) / K for n in algo_names}
    avg_nodes  = {n: sum(sc[3][n]["stats"]["nodes_explored"] for sc in scenarios) / K for n in algo_names}

    for i, name in enumerate(sorted(algo_names, key=lambda n: avg_rank[n])):
        y = y0 + row_h * (i + 1) + 6
        bg = TABLE_ROW if i % 2 == 0 else TABLE_ALT
        pygame.draw.rect(screen, bg, (61, y - 4, 718, row_h - 2))
        c = ALGO_COLORS[name]
        draw_text(screen, name,                  col_x[0], y, font_row, c)
        draw_text(screen, f"{avg_rank[name]:.2f}",   col_x[1], y, font_row, RANK_COLS.get(i+1, TEXT_COL))
        draw_text(screen, str(best_count[name]),  col_x[2], y, font_row)
        draw_text(screen, str(worst_count[name]), col_x[3], y, font_row)
        draw_text(screen, f"{avg_dist[name]:.1f}",   col_x[4], y, font_row)
        draw_text(screen, f"{avg_nodes[name]:.0f}",  col_x[5], y, font_row)

    draw_text(screen, "R = ver escenarios    Q = salir",
              WIN_W // 2, WIN_H - 50, font_row, (150, 150, 150), center=True)
    pygame.display.flip()


def run():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Problema 3 – Comparación BFS / DFS / UCS / A*  |  45×55  K=25")
    clock = pygame.time.Clock()

    font_title = pygame.font.SysFont("Arial", 17, bold=True)
    font_hdr   = pygame.font.SysFont("Arial", 13, bold=True)
    font_row   = pygame.font.SysFont("Arial", 13)
    font_hint  = pygame.font.SysFont("Arial", 12)

    print("Generando 25 laberintos...")
    scenarios = []
    for i in range(K):
        scenarios.append(generate_scenario())
        print(f"  {i+1}/{K}")
    all_ranks = [rank_scenario(sc[3]) for sc in scenarios]
    print("Listo.")

    idx    = 0
    paused = False
    anim_idx = 0
    show_summary = False

    def max_explored():
        _, _, _, results = scenarios[idx]
        return max(len(results[n]["explored"]) for n, _ in ALGOS)

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.quit(); sys.exit()
                if event.key == pygame.K_SPACE:
                    paused = not paused
                if event.key == pygame.K_n and not show_summary:
                    idx = (idx + 1) % K
                    anim_idx = 0; paused = False
                if event.key == pygame.K_b and not show_summary:
                    idx = (idx - 1) % K
                    anim_idx = 0; paused = False
                if event.key == pygame.K_s:
                    show_summary = True
                if event.key == pygame.K_r:
                    show_summary = False
                    idx = 0; anim_idx = 0; paused = False

        if show_summary:
            draw_summary_table(screen, scenarios, all_ranks, font_title, font_hdr, font_row)
            continue

        if not paused:
            mx = max_explored()
            if anim_idx < mx:
                anim_idx = min(anim_idx + EXPLORE_SPEED, mx)

        maze, start, goal, results = scenarios[idx]
        ranks = all_ranks[idx]
        anim_complete = (anim_idx >= max_explored())

        screen.fill(BG)

        for i, (name, _) in enumerate(ALGOS):
            ox, oy = MAZE_OX[i], MAZE_OY[i]
            explored = results[name]["explored"]
            path     = results[name]["path"]

            surf = draw_maze_surf(maze)
            shown = min(anim_idx, len(explored))
            paint_cells(surf, explored[:shown], ALGO_COLORS[name])
            if anim_complete:
                paint_cells(surf, path, PATH_COLORS[name])

            sr, sc2 = start
            gr, gc2 = goal
            pygame.draw.rect(surf, START_COL, (sc2*CELL+1, sr*CELL+1, CELL-1, CELL-1))
            pygame.draw.rect(surf, GOAL_COL,  (gc2*CELL+1, gr*CELL+1, CELL-1, CELL-1))

            screen.blit(surf, (ox, oy))

            rank = ranks[name]
            lbl = f"{name}  –  Rank #{rank}"
            draw_text(screen, lbl, ox, oy - 14, font_hdr, ALGO_COLORS[name])

        draw_scenario_table(screen, results, ranks, anim_complete,
                            font_hdr, font_row, TABLE_OX, TABLE_OY)

        ty = TABLE_OY + 28 + 34 * (len(ALGOS) + 1) + 20
        draw_text(screen, f"Escenario {idx+1} / {K}", TABLE_OX, ty, font_hdr, TEXT_COL)
        ty += 22
        sr, sc2 = start; gr, gc2 = goal
        draw_text(screen, f"Inicio: ({sr},{sc2})", TABLE_OX, ty, font_row)
        ty += 18
        draw_text(screen, f"Meta:  ({gr},{gc2})", TABLE_OX, ty, font_row)
        ty += 18
        md = manhattan(start, goal)
        draw_text(screen, f"Manhattan: {md}", TABLE_OX, ty, font_row)

        if paused:
            ty += 22
            draw_text(screen, "PAUSADO", TABLE_OX, ty, font_hdr, (255, 80, 80))

        by = WIN_H - BOTTOM_H
        pygame.draw.rect(screen, PANEL_BG, (0, by, WIN_W, BOTTOM_H))
        hint = "N=siguiente  B=anterior  S=tabla resumen  ESPACIO=pausar  Q=salir"
        draw_text(screen, hint, WIN_W // 2, by + 16, font_hint, (150, 150, 150), center=True)

        pygame.display.flip()

if __name__ == "__main__":
    run()
