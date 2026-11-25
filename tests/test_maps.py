import json

import pytest

import map_storage
from algorithms import bfs, dfs, astar
from presets import create_preset


@pytest.fixture
def temporary_map_file(tmp_path, monkeypatch):
    """将地图读写切换到临时目录，保护真实保存文件。"""
    path = tmp_path / "maps" / "saved_maze.json"
    monkeypatch.setattr(map_storage, "MAP_FILE", path)
    return path


def test_save_and_load(temporary_map_file):
    """保存再加载，障碍和起终点应完全一致。"""
    maze = [
        [0, 1, 0],
        [0, 0, 0],
        [1, 0, 0],
    ]
    start = (0, 0)
    end = (2, 2)

    map_storage.save_map(maze, start, end)
    loaded_maze, loaded_start, loaded_end = map_storage.load_map(3, 3)

    assert temporary_map_file.exists()
    assert loaded_maze == maze
    assert loaded_start == start
    assert loaded_end == end


def test_missing_file(temporary_map_file):
    """未保存过地图时，应报告文件不存在。"""
    with pytest.raises(FileNotFoundError):
        map_storage.load_map(3, 3)


def test_broken_file(temporary_map_file):
    """损坏的JSON文件应被拒绝。"""
    temporary_map_file.parent.mkdir(parents=True)
    temporary_map_file.write_text(
        "这不是合法的JSON",
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        map_storage.load_map(3, 3)


@pytest.mark.parametrize(
    "case",
    [
        "wrong_rows",
        "wrong_cols",
        "invalid_cell",
        "outside_start",
        "blocked_end",
        "same_endpoints",
    ],
)
def test_invalid_map(temporary_map_file, case):
    """不合法的尺寸、格子或起终点应被拒绝。"""
    data = {
        "maze": [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ],
        "start": [0, 0],
        "end": [2, 2],
    }

    if case == "wrong_rows":
        data["maze"].pop()
    elif case == "wrong_cols":
        data["maze"][0].pop()
    elif case == "invalid_cell":
        data["maze"][1][1] = 2
    elif case == "outside_start":
        data["start"] = [-1, 0]
    elif case == "blocked_end":
        data["maze"][2][2] = 1
    elif case == "same_endpoints":
        data["end"] = [0, 0]

    temporary_map_file.parent.mkdir(parents=True)
    temporary_map_file.write_text(
        json.dumps(data),
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        map_storage.load_map(3, 3)


@pytest.mark.parametrize("search", [bfs, astar])
@pytest.mark.parametrize(
    "preset_name, expected_steps",
    [
        ("empty", 38),
        ("detour", 72),
    ],
)
def test_preset_shortest_path(search, preset_name, expected_steps):
    """空白和绕行预设的最短路径长度应符合预期。"""
    maze, start, end, _ = create_preset(preset_name, 20, 20)
    path = search(maze, start, end)

    assert path
    assert path[0] == start
    assert path[-1] == end
    assert len(path) - 1 == expected_steps

    # 检查路线没有穿墙或跳格
    for row, col in path:
        assert 0 <= row < 20
        assert 0 <= col < 20
        assert maze[row][col] == 0

    for current, following in zip(path, path[1:]):
        assert (
            abs(current[0] - following[0])
            + abs(current[1] - following[1])
        ) == 1


@pytest.mark.parametrize("search", [bfs, dfs, astar])
def test_blocked_preset(search):
    """无解预设中，三种算法只能探索起点。"""
    maze, start, end, _ = create_preset("blocked", 20, 20)
    visit_order = []

    path = search(maze, start, end, visit_order)

    assert path == []
    assert visit_order == [start]


def test_preset_is_independent():
    """修改生成的地图，不应影响下一次生成结果。"""
    original, _, _, _ = create_preset("detour", 20, 20)
    edited, _, _, _ = create_preset("detour", 20, 20)

    edited[0][0] = 1

    regenerated, _, _, _ = create_preset("detour", 20, 20)

    assert original[0][0] == 0
    assert regenerated == original
    assert regenerated != edited