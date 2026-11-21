import pytest

from algorithms import bfs, dfs, astar


ALGORITHMS = [bfs, dfs, astar]


def assert_valid_path(maze, path, start, end):
    """检查路径端点、边界、障碍和相邻步是否合法。"""
    assert path, "有解迷宫应返回路径"
    assert path[0] == start, "路径必须从起点开始"
    assert path[-1] == end, "路径必须在终点结束"

    rows = len(maze)
    cols = len(maze[0])

    for row, col in path:
        assert 0 <= row < rows and 0 <= col < cols, "路径不能越界"
        assert maze[row][col] == 0, "路径不能穿墙"

    for current, following in zip(path, path[1:]):
        distance = (
            abs(current[0] - following[0])
            + abs(current[1] - following[1])
        )
        assert distance == 1, "每步只能向上下左右移动一格"


@pytest.mark.parametrize("search", ALGORITHMS)
def test_path_through_gap(search):
    """三种算法都应找到穿过墙上缺口的合法路径。"""
    maze = [
        [0, 1, 0],
        [0, 1, 0],
        [0, 0, 0],
    ]

    path = search(maze, (0, 0), (0, 2))
    assert_valid_path(maze, path, (0, 0), (0, 2))


@pytest.mark.parametrize("search", ALGORITHMS)
def test_no_path(search):
    """起点被阻断时，应返回空列表。"""
    maze = [
        [0, 1, 0],
        [1, 1, 0],
        [0, 0, 0],
    ]

    assert search(maze, (0, 0), (0, 2)) == []


@pytest.mark.parametrize("search", ALGORITHMS)
def test_same_start_and_end(search):
    """起点等于终点时，路径只有一个格子，步数为0。"""
    maze = [
        [0, 0],
        [0, 0],
    ]

    assert search(maze, (0, 0), (0, 0)) == [(0, 0)]


@pytest.mark.parametrize("search", ALGORITHMS)
def test_cannot_move_diagonally(search):
    """对角线相邻不能替代上下左右通行。"""
    maze = [
        [0, 1],
        [1, 0],
    ]

    assert search(maze, (0, 0), (1, 1)) == []


@pytest.mark.parametrize("search", [bfs, astar])
def test_shortest_path_with_detour(search):
    """墙迫使路径绕行，最短距离为8步。"""
    maze = [
        [0, 1, 0],
        [0, 1, 0],
        [0, 1, 0],
        [0, 0, 0],
    ]

    path = search(maze, (0, 0), (0, 2))

    assert_valid_path(maze, path, (0, 0), (0, 2))
    assert len(path) - 1 == 8


@pytest.mark.parametrize("search", ALGORITHMS)
def test_search_does_not_change_maze(search):
    """算法不能修改地图，否则同地图对比会受到影响。"""
    maze = [
        [0, 1, 0],
        [0, 0, 0],
    ]
    original = [row[:] for row in maze]

    search(maze, (0, 0), (0, 2))

    assert maze == original