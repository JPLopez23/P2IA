import random
import numpy as np

class Maze:
    """
    Representa un laberinto como una cuadrícula de celdas.
    Cada celda tiene 4 paredes: N=0, S=1, E=2, W=3
    walls[row][col] es una lista de 4 booleanos (True = existe pared)
    """
    N, S, E, W = 0, 1, 2, 3
    OPPOSITE = {N: S, S: N, E: W, W: E}
    DR = {N: -1, S: 1, E: 0, W: 0}
    DC = {N: 0, S: 0, E: 1, W: -1}

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.walls = [[{self.N, self.S, self.E, self.W} for _ in range(cols)] for _ in range(rows)]

    def remove_wall(self, r, c, direction):
        self.walls[r][c].discard(direction)
        nr = r + self.DR[direction]
        nc = c + self.DC[direction]
        if 0 <= nr < self.rows and 0 <= nc < self.cols:
            self.walls[nr][nc].discard(self.OPPOSITE[direction])

    def has_wall(self, r, c, direction):
        return direction in self.walls[r][c]

    def neighbors(self, r, c):
        result = []
        for d in [self.N, self.S, self.E, self.W]:
            nr = r + self.DR[d]
            nc = c + self.DC[d]
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                result.append((nr, nc, d))
        return result

    def passable_neighbors(self, r, c):
        result = []
        for d in [self.N, self.S, self.E, self.W]:
            if d not in self.walls[r][c]:
                nr = r + self.DR[d]
                nc = c + self.DC[d]
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    result.append((nr, nc))
        return result


class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        return True


def kruskal(rows, cols):
    """Genera un laberinto usando el algoritmo de Kruskal paso a paso."""
    maze = Maze(rows, cols)
    uf = UnionFind(rows * cols)

    edges = []
    for r in range(rows):
        for c in range(cols):
            if r + 1 < rows:
                edges.append((r, c, Maze.S))
            if c + 1 < cols:
                edges.append((r, c, Maze.E))

    random.shuffle(edges)

    for r, c, d in edges:
        nr = r + Maze.DR[d]
        nc = c + Maze.DC[d]
        u = r * cols + c
        v = nr * cols + nc
        if uf.union(u, v):
            maze.remove_wall(r, c, d)
            yield maze, (r, c, nr, nc)


def kruskal_full(rows, cols):
    maze = None
    for maze, _ in kruskal(rows, cols):
        pass
    return maze


def prim(rows, cols, start_r=0, start_c=0):
    """Genera un laberinto usando el algoritmo de Prim paso a paso."""
    maze = Maze(rows, cols)
    visited = [[False] * cols for _ in range(rows)]
    visited[start_r][start_c] = True

    frontier = []

    def add_frontier(r, c):
        for nr, nc, d in maze.neighbors(r, c):
            if not visited[nr][nc]:
                frontier.append((nr, nc, Maze.OPPOSITE[d], r, c))

    add_frontier(start_r, start_c)

    while frontier:
        idx = random.randrange(len(frontier))
        frontier[idx], frontier[-1] = frontier[-1], frontier[idx]
        nr, nc, d, fr, fc = frontier.pop()

        if visited[nr][nc]:
            continue

        visited[nr][nc] = True
        maze.remove_wall(fr, fc, Maze.OPPOSITE[d])
        add_frontier(nr, nc)
        yield maze, (nr, nc)


def prim_full(rows, cols):
    maze = None
    for maze, _ in prim(rows, cols):
        pass
    return maze
