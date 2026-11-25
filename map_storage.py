import json
from pathlib import Path


# 地图保存在项目目录下，不受终端当前目录影响
MAP_FILE = Path(__file__).resolve().parent / "maps" / "saved_maze.json"


def save_map(maze, start, end):
    """保存障碍和起终点，不保存搜索颜色。"""
    data = {
        "maze": maze,
        "start": list(start),
        "end": list(end),
    }

    MAP_FILE.parent.mkdir(parents=True, exist_ok=True)

    # 先写临时文件，成功后再替换旧地图
    temp_file = MAP_FILE.with_suffix(".tmp")
    temp_file.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temp_file.replace(MAP_FILE)


def load_map(rows, cols):
    """读取并检查地图，检查通过后才返回。"""
    data = json.loads(MAP_FILE.read_text(encoding="utf-8"))

    if not isinstance(data, dict):
        raise ValueError("地图文件格式不正确")

    maze = data.get("maze")

    if not isinstance(maze, list) or len(maze) != rows:
        raise ValueError("地图行数不匹配")

    for row in maze:
        if not isinstance(row, list) or len(row) != cols:
            raise ValueError("地图列数不匹配")

        if any(type(cell) is not int or cell not in (0, 1) for cell in row):
            raise ValueError("地图格子只能是0或1")

    def read_position(name):
        position = data.get(name)

        if (
            not isinstance(position, list)
            or len(position) != 2
            or any(type(value) is not int for value in position)
        ):
            raise ValueError("起点或终点格式不正确")

        row, col = position

        if not (0 <= row < rows and 0 <= col < cols):
            raise ValueError("起点或终点超出地图范围")

        if maze[row][col] != 0:
            raise ValueError("起点或终点不能位于障碍上")

        return (row, col)

    start = read_position("start")
    end = read_position("end")

    if start == end:
        raise ValueError("起点与终点不能重叠")

    return maze, start, end