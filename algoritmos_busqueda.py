import heapq
import time
from collections import deque


def _reconstruct(parent, start, goal):
    path = []
    node = goal
    while node != start:
        path.append(node)
        node = parent[node]
    path.append(start)
    path.reverse()
    return path


def bfs(maze, start, goal):
    """Búsqueda en amplitud (BFS)."""
    t0 = time.perf_counter()
    queue = deque([start])
    visited = {start}
    parent = {start: None}
    explored_order = [start]

    while queue:
        node = queue.popleft()
        if node == goal:
            break
        r, c = node
        for nr, nc in maze.passable_neighbors(r, c):
            if (nr, nc) not in visited:
                visited.add((nr, nc))
                parent[(nr, nc)] = node
                queue.append((nr, nc))
                explored_order.append((nr, nc))

    elapsed = (time.perf_counter() - t0) * 1000

    if goal not in parent:
        return None, explored_order, {"path_length": 0, "nodes_explored": len(explored_order), "time_ms": elapsed}

    path = _reconstruct(parent, start, goal)
    stats = {
        "path_length": len(path) - 1,
        "nodes_explored": len(explored_order),
        "time_ms": elapsed,
    }
    return path, explored_order, stats


def dfs(maze, start, goal):
    """Búsqueda en profundidad (DFS)."""
    t0 = time.perf_counter()
    stack = [start]
    visited = {start}
    parent = {start: None}
    explored_order = [start]

    while stack:
        node = stack.pop()
        if node == goal:
            break
        r, c = node
        for nr, nc in maze.passable_neighbors(r, c):
            if (nr, nc) not in visited:
                visited.add((nr, nc))
                parent[(nr, nc)] = node
                stack.append((nr, nc))
                explored_order.append((nr, nc))

    elapsed = (time.perf_counter() - t0) * 1000

    if goal not in parent:
        return None, explored_order, {"path_length": 0, "nodes_explored": len(explored_order), "time_ms": elapsed}

    path = _reconstruct(parent, start, goal)
    stats = {
        "path_length": len(path) - 1,
        "nodes_explored": len(explored_order),
        "time_ms": elapsed,
    }
    return path, explored_order, stats


def ucs(maze, start, goal):
    """Búsqueda de costo uniforme (UCS)."""
    t0 = time.perf_counter()
    heap = [(0, start)]
    dist = {start: 0}
    parent = {start: None}
    explored_order = []
    visited = set()

    while heap:
        cost, node = heapq.heappop(heap)
        if node in visited:
            continue
        visited.add(node)
        explored_order.append(node)
        if node == goal:
            break
        r, c = node
        for nr, nc in maze.passable_neighbors(r, c):
            new_cost = cost + 1
            if (nr, nc) not in dist or new_cost < dist[(nr, nc)]:
                dist[(nr, nc)] = new_cost
                parent[(nr, nc)] = node
                heapq.heappush(heap, (new_cost, (nr, nc)))

    elapsed = (time.perf_counter() - t0) * 1000

    if goal not in parent:
        return None, explored_order, {"path_length": 0, "nodes_explored": len(explored_order), "time_ms": elapsed}

    path = _reconstruct(parent, start, goal)
    stats = {
        "path_length": len(path) - 1,
        "nodes_explored": len(explored_order),
        "time_ms": elapsed,
    }
    return path, explored_order, stats


def _manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(maze, start, goal):
    """Búsqueda A* con heurística de distancia Manhattan."""
    t0 = time.perf_counter()
    heap = [(0 + _manhattan(start, goal), 0, start)]
    g_score = {start: 0}
    parent = {start: None}
    explored_order = []
    visited = set()

    while heap:
        f, g, node = heapq.heappop(heap)
        if node in visited:
            continue
        visited.add(node)
        explored_order.append(node)
        if node == goal:
            break
        r, c = node
        for nr, nc in maze.passable_neighbors(r, c):
            new_g = g + 1
            if (nr, nc) not in g_score or new_g < g_score[(nr, nc)]:
                g_score[(nr, nc)] = new_g
                parent[(nr, nc)] = node
                h = _manhattan((nr, nc), goal)
                heapq.heappush(heap, (new_g + h, new_g, (nr, nc)))

    elapsed = (time.perf_counter() - t0) * 1000

    if goal not in parent:
        return None, explored_order, {"path_length": 0, "nodes_explored": len(explored_order), "time_ms": elapsed}

    path = _reconstruct(parent, start, goal)
    stats = {
        "path_length": len(path) - 1,
        "nodes_explored": len(explored_order),
        "time_ms": elapsed,
    }
    return path, explored_order, stats


ALGORITHMS = {
    "BFS": bfs,
    "DFS": dfs,
    "UCS": ucs,
    "A*": astar,
}
