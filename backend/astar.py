import numpy as np
import heapq

class AStar:
    def __init__(self, grid):
        self.grid = grid  # 0=walkable, 1=obstacle

    def heuristic(self, a, b):
        return np.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)

    def find_path(self, start, end):
        neighbors = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # 4-directional movement
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, end)}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == end:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1]

            for dx, dy in neighbors:
                neighbor = (current[0] + dx, current[1] + dy)

                if (0 <= neighbor[0] < self.grid.shape[1] and
                    0 <= neighbor[1] < self.grid.shape[0] and
                    self.grid[neighbor[1], neighbor[0]] == 0):  # Access as [y][x]

                    tentative_g = g_score[current] + 1

                    if neighbor not in g_score or tentative_g < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g
                        f_score[neighbor] = tentative_g + self.heuristic(neighbor, end)
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return []  # No path found
