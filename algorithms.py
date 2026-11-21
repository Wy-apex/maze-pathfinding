from collections import deque
import heapq

def bfs(maze, start, end, visit_order=None):
    """返回最短路径；无解时返回空列表。"""
    rows = len(maze)
    cols = len(maze[0])

    queue = deque([start])
    parent = {start: None}

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while queue:
        current = queue.popleft()

        # 记录探索顺序，供界面播放动画
        if visit_order is not None:
            visit_order.append(current)

        if current == end:
            path = []

            while current is not None:
                path.append(current)
                current = parent[current]

            path.reverse()
            return path

        row, col = current

        for dr, dc in directions:
            next_row = row + dr
            next_col = col + dc
            neighbor = (next_row, next_col)

            if not (0 <= next_row < rows and 0 <= next_col < cols):
                continue

            if maze[next_row][next_col] == 1:
                continue

            if neighbor in parent:
                continue

            parent[neighbor] = current
            queue.append(neighbor)

    return []

def dfs(maze, start, end, visit_order=None):
    """深度优先搜索：返回一条可行路径，不保证最短。"""
    rows = len(maze)
    cols = len(maze[0])

    # 栈：后放进去的格子先探索
    stack = [start]
    parent = {start: None}

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while stack:
        current = stack.pop()

        if visit_order is not None:
            visit_order.append(current)

        if current == end:
            path = []

            while current is not None:
                path.append(current)
                current = parent[current]

            path.reverse()
            return path

        row, col = current

        for dr, dc in directions:
            next_row = row + dr
            next_col = col + dc
            neighbor = (next_row, next_col)

            if not (0 <= next_row < rows and 0 <= next_col < cols):
                continue

            if maze[next_row][next_col] == 1:
                continue

            if neighbor in parent:
                continue

            parent[neighbor] = current
            stack.append(neighbor)

    return []

def astar(maze, start, end, visit_order=None):
    """A*搜索：使用曼哈顿距离，返回最短路径。"""
    rows = len(maze)
    cols = len(maze[0])

    def heuristic(position):
        return (
            abs(position[0] - end[0])
            + abs(position[1] - end[1])
        )

    # 优先队列条目：(总估计代价, 剩余距离估计, 已走步数, 坐标)
    # 总估计代价相同时，优先选择剩余距离估计更小的格子
    frontier = [(heuristic(start), heuristic(start), 0, start)]

    parent = {start: None}
    g_score = {start: 0}
    closed = set()

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while frontier:
        _, _, current_g, current = heapq.heappop(frontier)

        # 跳过已经处理过或已经被更短路线替代的记录
        if current in closed:
            continue
        if current_g != g_score[current]:
            continue

        closed.add(current)

        if visit_order is not None:
            visit_order.append(current)

        if current == end:
            path = []

            while current is not None:
                path.append(current)
                current = parent[current]

            path.reverse()
            return path

        row, col = current

        for dr, dc in directions:
            next_row = row + dr
            next_col = col + dc
            neighbor = (next_row, next_col)

            if not (0 <= next_row < rows and 0 <= next_col < cols):
                continue

            if maze[next_row][next_col] == 1:
                continue

            if neighbor in closed:
                continue

            new_g = current_g + 1

            if new_g < g_score.get(neighbor, float("inf")):
                g_score[neighbor] = new_g
                parent[neighbor] = current

                h = heuristic(neighbor)
                heapq.heappush(
                    frontier,
                    (new_g + h, h, new_g, neighbor),
                )

    return []

if __name__ == "__main__":
    test_maze = [
        [0, 1, 0],
        [0, 1, 0],
        [0, 0, 0],
    ]

    path = bfs(test_maze, (0, 0), (0, 2))
    print("找到的路径：", path)
    print("路径步数：", len(path) - 1 if path else "无解")

    blocked_maze = [
        [0, 1, 0],
        [1, 1, 0],
        [0, 0, 0],
    ]

    print("无解迷宫的结果：", bfs(blocked_maze, (0, 0), (0, 2)))