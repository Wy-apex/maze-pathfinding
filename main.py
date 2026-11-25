import pygame
from benchmark import compare_algorithms
from algorithms import bfs, dfs, astar
from map_storage import save_map, load_map
from presets import create_preset
pygame.init()

ROWS = 20
COLS = 20
CELL_SIZE = 30

MAZE_WIDTH = COLS * CELL_SIZE
MAZE_HEIGHT = ROWS * CELL_SIZE
PANEL_WIDTH = 280

screen = pygame.display.set_mode(
    (MAZE_WIDTH + PANEL_WIDTH, MAZE_HEIGHT)
)

# 直接加载微软雅黑，避免扫描系统字体
font_path = r"C:\Windows\Fonts\msyh.ttc"
font = pygame.font.Font(font_path, 18)
title_font = pygame.font.Font(font_path, 24)
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
# 保存当前地图的性能对比结果
comparison_results = []

# 表格字体稍小，适合侧边栏
table_font = pygame.font.Font(font_path, 14)
VISITED_COLOR = (135, 195, 245)

# 每隔30毫秒显示一个探索格子
# 数值是每个探索格子的播放间隔，越小越快
SPEED_INTERVALS = [200, 100, 60, 30, 15]
speed_index = 3
ANIMATION_INTERVAL = SPEED_INTERVALS[speed_index]

animation = {
    "running": False,
    "order": [],
    "index": 0,
    "path": [],
    "last_tick": 0,
    "name": "BFS",
    "paused": False,
}

TITLE = "Maze | S/E: start/end | Space: BFS | D: DFS | A: A* | P: compare | C: clear"
pygame.display.set_caption(TITLE)


def clear_result():
    """取消动画、清除结果，并恢复非暂停状态。"""
    path_cells.clear()
    visited_cells.clear()
    comparison_results.clear()

    animation["running"] = False
    animation["paused"] = False
    animation["order"] = []
    animation["index"] = 0
    animation["path"] = []
    animation["last_tick"] = 0

    pygame.display.set_caption(TITLE)

# 每个按钮包含：位置、文字、对应操作
button_specs = [
    ("运行 BFS（空格）", pygame.K_SPACE),
    ("运行 DFS（D）", pygame.K_d),
    ("运行 A*（A）", pygame.K_a),
    ("性能对比（P）", pygame.K_p),
    ("重置搜索 · 保留地图", "reset"),
    ("清空障碍（C）", pygame.K_c),
    ("保存地图（F5）", pygame.K_F5),
    ("加载地图（F9）", pygame.K_F9),
]

buttons = [
    (
        pygame.Rect(MAZE_WIDTH + 20, 65 + index * 41, 240, 34),
        label,
        action,
    )
    for index, (label, action) in enumerate(button_specs)
]


def draw_comparison():
    """在侧边栏下方显示当前地图的性能结果。"""
    left = MAZE_WIDTH + 16

    title = font.render("当前地图 · 性能对比", True, (35, 45, 65))
    screen.blit(title, (left, 400))

    # 各列在面板内的位置
    columns = [left, left + 43, left + 92, left + 154]
    headers = ["算法", "步数", "探索数", "耗时(ms)"]

    for x, label in zip(columns, headers):
        text = table_font.render(label, True, (65, 75, 95))
        screen.blit(text, (x, 434))

    for index, result in enumerate(comparison_results):
        y = 460 + index * 28

        background = (255, 255, 255) if index % 2 == 0 else (222, 231, 243)
        pygame.draw.rect(
            screen,
            background,
            (left - 4, y - 3, PANEL_WIDTH - 24, 26),
            border_radius=4,
        )

        steps = (
            str(result["steps"])
            if result["steps"] is not None
            else "无解"
        )

        values = [
            result["name"],
            steps,
            str(result["explored"]),
            f'{result["average_ms"]:.4f}',
        ]

        for x, value in zip(columns, values):
            text = table_font.render(value, True, (35, 45, 65))
            screen.blit(text, (x, y))

    notes = [
        "100次平均，不含动画和绘图",
        "修改地图或重置后清除本表",
    ]

    for index, line in enumerate(notes):
        text = table_font.render(line, True, (65, 75, 95))
        screen.blit(text, (left, 550 + index * 21))

def draw_panel():
    """绘制中文操作面板。"""
    panel_rect = pygame.Rect(
        MAZE_WIDTH, 0, PANEL_WIDTH, MAZE_HEIGHT
    )
    pygame.draw.rect(screen, (232, 237, 245), panel_rect)

    title = title_font.render(
        "迷宫寻路实验室", True, (35, 45, 65)
    )
    screen.blit(title, (MAZE_WIDTH + 20, 20))

    preset_hint = table_font.render(
        "F1 空白  /  F2 绕行  /  F3 无解",
        True,
        (65, 75, 95),
    )
    screen.blit(preset_hint, (MAZE_WIDTH + 20, 48))

    mouse_position = pygame.mouse.get_pos()

    for rect, label, action in buttons:
        hovered = rect.collidepoint(mouse_position)
        color = (210, 226, 250) if hovered else (255, 255, 255)

        pygame.draw.rect(screen, color, rect, border_radius=8)
        pygame.draw.rect(
            screen, (175, 190, 210), rect, 1, border_radius=8
        )

        text = font.render(label, True, (35, 45, 65))
        screen.blit(text, text.get_rect(center=rect.center))

    if comparison_results:
        draw_comparison()
        return

    if animation["running"]:
        playback_status = (
            "已暂停" if animation["paused"] else "播放中"
        )
    else:
        playback_status = "待运行 / 已结束"

    instructions = [
        "左键画墙，右键擦除；S/E设端点",
        f"F6 暂停/继续：{playback_status}",
        f"↑ 加快 / ↓ 减慢：速度 {speed_index + 1}/5",
        "英文输入法；性能结果见终端",
    ]

    for index, line in enumerate(instructions):
        text = font.render(line, True, (65, 75, 95))
        screen.blit(
            text, (MAZE_WIDTH + 20, 405 + index * 23)
        )

    legend = [
        (START_COLOR, "起点"),
        (END_COLOR, "终点"),
        (VISITED_COLOR, "已探索"),
        (PATH_COLOR, "路径"),
    ]

    for index, (color, label) in enumerate(legend):
        x = MAZE_WIDTH + 20 + (index % 2) * 125
        y = 505 + (index // 2) * 34

        pygame.draw.rect(
            screen, color, (x, y, 18, 18), border_radius=3
        )
        text = font.render(label, True, (65, 75, 95))
        screen.blit(text, (x + 26, y - 3))

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for rect, label, action in buttons:
                    if rect.collidepoint(event.pos):
                        if action == "reset":
                            clear_result()
                        else:
                            # 复用原有快捷键处理逻辑
                            pygame.event.post(
                                pygame.event.Event(
                                    pygame.KEYDOWN,
                                    key=action,
                                )
                            )
                        break

        elif event.type == pygame.KEYDOWN:
            if event.key in (
                pygame.K_F1,
                pygame.K_F2,
                pygame.K_F3,
            ):
                preset_names = {
                    pygame.K_F1: "empty",
                    pygame.K_F2: "detour",
                    pygame.K_F3: "blocked",
                }

                maze, start, end, preset_title = create_preset(
                    preset_names[event.key],
                    ROWS,
                    COLS,
                )

                clear_result()
                pygame.display.set_caption(
                    f"已切换：{preset_title}"
                )
                print(f"已切换预设：{preset_title}")

            elif event.key == pygame.K_F6:
                if animation["running"]:
                    animation["paused"] = not animation["paused"]
                    animation["last_tick"] = pygame.time.get_ticks()

                    name = animation["name"]
                    if animation["paused"]:
                        pygame.display.set_caption(
                            f"{name} | 已暂停，按F6继续"
                        )
                    else:
                        pygame.display.set_caption(
                            f"{name} | 搜索过程播放中"
                        )

            elif event.key in (pygame.K_UP, pygame.K_DOWN):
                if event.key == pygame.K_UP:
                    speed_index = min(
                        speed_index + 1,
                        len(SPEED_INTERVALS) - 1,
                    )
                else:
                    speed_index = max(speed_index - 1, 0)

                ANIMATION_INTERVAL = SPEED_INTERVALS[speed_index]
                animation["last_tick"] = pygame.time.get_ticks()

            elif event.key == pygame.K_F5:
                try:
                    save_map(maze, start, end)
                except OSError as error:
                    pygame.display.set_caption("保存失败，请查看终端")
                    print(f"保存失败：{error}")
                else:
                    pygame.display.set_caption("地图已保存")
                    print("地图已保存到 maps/saved_maze.json")

            elif event.key == pygame.K_F9:
                try:
                    loaded_maze, loaded_start, loaded_end = load_map(
                        ROWS, COLS
                    )
                except FileNotFoundError:
                    pygame.display.set_caption("还没有地图，请先保存")
                    print("还没有保存的地图，请先点击保存地图")
                except (OSError, ValueError) as error:
                    pygame.display.set_caption("加载失败，请查看终端")
                    print(f"加载失败：{error}")
                else:
                    maze = loaded_maze
                    start = loaded_start
                    end = loaded_end
                    clear_result()
                    pygame.display.set_caption("地图已加载")
                    print("地图加载成功")

            elif event.key == pygame.K_c:
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

                results = compare_algorithms(maze, start, end)
                comparison_results.extend(results)

                pygame.display.set_caption(
                    "性能对比完成，请查看右侧表格"
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
                animation["paused"] = False
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
    if animation["running"] and not animation["paused"]:
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
                animation["paused"] = False
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

    draw_panel()
    pygame.display.flip()
    clock.tick(60)
pygame.quit()