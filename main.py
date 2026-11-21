import pygame
from benchmark import compare_algorithms
from algorithms import bfs, dfs, astar
pygame.init()

ROWS = 20
COLS = 20
CELL_SIZE = 30

screen = pygame.display.set_mode(
    (COLS * CELL_SIZE, ROWS * CELL_SIZE)
)
clock = pygame.time.Clock()

WHITE = (245, 247, 250)
GRID_COLOR = (205, 210, 220)
WALL_COLOR = (45, 55, 72)
START_COLOR = (40, 180, 100)
END_COLOR = (230, 75, 75)
PATH_COLOR = (255, 210, 65)

maze = [[0 for _ in range(COLS)] for _ in range(ROWS)]
start = (0, 0)
end = (ROWS - 1, COLS - 1)

# 保存搜索结果，用于绘制黄色路径
path_cells = set()
# 已播放的探索格子
visited_cells = set()
VISITED_COLOR = (135, 195, 245)

# 每隔30毫秒显示一个探索格子
ANIMATION_INTERVAL = 30

animation = {
    "running": False,
    "order": [],
    "index": 0,
    "path": [],
    "last_tick": 0,
    "name": "BFS",
}

TITLE = "Maze | S/E: start/end | Space: BFS | D: DFS | A: A* | P: compare | C: clear"
pygame.display.set_caption(TITLE)


def clear_result():
    """地图改变时，取消动画并清除旧结果。"""
    path_cells.clear()
    visited_cells.clear()

    animation["running"] = False
    animation["order"] = []
    animation["index"] = 0
    animation["path"] = []
    animation["last_tick"] = 0

    pygame.display.set_caption(TITLE)

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                maze = [
                    [0 for _ in range(COLS)]
                    for _ in range(ROWS)
                ]
                clear_result()

            elif event.key in (pygame.K_s, pygame.K_e):
                mouse_x, mouse_y = pygame.mouse.get_pos()
                row = mouse_y // CELL_SIZE
                col = mouse_x // CELL_SIZE

                if 0 <= row < ROWS and 0 <= col < COLS:
                    position = (row, col)

                    if event.key == pygame.K_s and position != end:
                        start = position
                        maze[row][col] = 0
                        clear_result()

                    elif event.key == pygame.K_e and position != start:
                        end = position
                        maze[row][col] = 0
                        clear_result()

            elif event.key == pygame.K_p:
                clear_result()
                compare_algorithms(maze, start, end)
                pygame.display.set_caption(
                    "Comparison complete | See VS Code terminal"
                )

            elif event.key in (
                pygame.K_SPACE, pygame.K_d, pygame.K_a
            ):
                clear_result()

                order = []

                if event.key == pygame.K_SPACE:
                    name = "BFS"
                    path = bfs(maze, start, end, order)

                elif event.key == pygame.K_d:
                    name = "DFS"
                    path = dfs(maze, start, end, order)

                else:
                    name = "A*"
                    path = astar(maze, start, end, order)

                animation["name"] = name
                animation["order"] = order
                animation["path"] = path
                animation["index"] = 0
                animation["running"] = True
                animation["last_tick"] = pygame.time.get_ticks()

                pygame.display.set_caption(
                    f"{name} | Exploring... | C: clear"
                )   
                 # 鼠标编辑障碍
    if pygame.mouse.get_focused():
        left, middle, right = pygame.mouse.get_pressed()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        row = mouse_y // CELL_SIZE
        col = mouse_x // CELL_SIZE

        if 0 <= row < ROWS and 0 <= col < COLS:
            if (row, col) not in (start, end):
                if left and maze[row][col] != 1:
                    maze[row][col] = 1
                    clear_result()

                elif right and maze[row][col] != 0:
                    maze[row][col] = 0
                    clear_result()

    # 按记录顺序播放搜索过程，不阻塞鼠标和键盘操作
    if animation["running"]:
        now = pygame.time.get_ticks()

        if now - animation["last_tick"] >= ANIMATION_INTERVAL:
            animation["last_tick"] = now

            index = animation["index"]
            order = animation["order"]

            if index < len(order):
                visited_cells.add(order[index])
                animation["index"] += 1

            if animation["index"] >= len(order):
                animation["running"] = False
                path_cells.update(animation["path"])
                name = animation["name"]

                if animation["path"]:
                    steps = len(animation["path"]) - 1

                    pygame.display.set_caption(
                        f"{name} | Steps: {steps} | C: clear"
                    )

                    if name in ("BFS", "A*"):
                        print(f"{name} 找到最短路径，共 {steps} 步")
                    else:
                        print(f"{name} 找到可行路径，共 {steps} 步")
                else:
                    pygame.display.set_caption(
                        f"{name} | No path found | C: clear"
                    )
                    print(f"{name}：起点与终点之间没有可通行的路径")
    # 绘制迷宫及搜索结果
    screen.fill(WHITE)

    for row in range(ROWS):
        for col in range(COLS):
            position = (row, col)
            color = WHITE

            if maze[row][col] == 1:
                color = WALL_COLOR
            elif position in path_cells:
                color = PATH_COLOR
            elif position in visited_cells:
                color = VISITED_COLOR

            # 起终点颜色覆盖路径颜色，保持容易辨认
            if position == start:
                color = START_COLOR
            elif position == end:
                color = END_COLOR

            rect = pygame.Rect(
                col * CELL_SIZE,
                row * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, GRID_COLOR, rect, 1)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()