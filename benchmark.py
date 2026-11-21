from time import perf_counter

from algorithms import bfs, dfs, astar


def compare_algorithms(maze, start, end, repeats=100):
    """在同一张地图上比较算法，不包含动画播放。"""
    algorithms = [
        ("BFS", bfs),
        ("DFS", dfs),
        ("A*", astar),
    ]

    results = []

    for name, search in algorithms:
        # 单独记录探索数量，不将记录动画顺序的开销计入耗时
        visit_order = []
        path = search(maze, start, end, visit_order)

        # 预热一次
        search(maze, start, end)

        begin = perf_counter()

        for _ in range(repeats):
            search(maze, start, end)

        average_ms = (perf_counter() - begin) * 1000 / repeats

        results.append({
            "name": name,
            "steps": len(path) - 1 if path else None,
            "explored": len(visit_order),
            "average_ms": average_ms,
        })

    print("\n========== 当前迷宫性能对比 ==========")
    print(f"起点：{start}，终点：{end}")
    print(f"每种算法运行 {repeats} 次，耗时不包含动画与绘图")
    print(f"{'算法':<8}\t路径步数\t探索节点\t平均耗时(ms)")

    for result in results:
        steps = (
            str(result["steps"])
            if result["steps"] is not None
            else "无解"
        )

        print(
            f'{result["name"]:<8}\t'
            f'{steps}\t\t'
            f'{result["explored"]}\t\t'
            f'{result["average_ms"]:.4f}'
        )

    print("======================================\n")

    return results