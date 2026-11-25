def create_preset(name, rows, cols):
    """每次创建一张新地图，避免修改预设原始数据。"""
    if rows < 5 or cols < 5:
        raise ValueError("预设地图至少需要5行5列")

    maze = [[0 for _ in range(cols)] for _ in range(rows)]
    start = (0, 0)
    end = (rows - 1, cols - 1)

    if name == "empty":
        title = "空白地图"

    elif name == "detour":
        title = "绕行地图"

        first_wall = cols // 3
        second_wall = 2 * cols // 3

        # 第一道墙的缺口靠下
        for row in range(rows):
            if row != rows - 2:
                maze[row][first_wall] = 1

        # 第二道墙的缺口靠上，迫使路线折返
        for row in range(rows):
            if row != 1:
                maze[row][second_wall] = 1

    elif name == "blocked":
        title = "无解地图"

        # 起点位于左上角，封住仅有的两个出口
        maze[0][1] = 1
        maze[1][0] = 1

    else:
        raise ValueError("未知的预设地图")

    return maze, start, end, title