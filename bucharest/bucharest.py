"""
ARAD -> BUCHAREST : FINAL INTERACTIVE SEARCH VISUALIZER
=======================================================

Algorithms included
-------------------
1. DFS  - Depth First Search
2. BFS  - Breadth First Search
3. UCS  - Uniform Cost Search
4. GBFS - Greedy Best First Search
5. A*   - A Star Search

Why GBFS is included
--------------------
The supplied heuristic table is the standard h(n) table for the
Romania-map problem. These h(n) values are used by the INFORMED
searches: GBFS and A*.

h(n) used
---------
Arad 366        Mehadia 241
Bucharest 0     Neamt 234
Craiova 160     Oradea 380
Drobeta 242     Pitesti 100
Eforie 161      Rimnicu Vilcea 193
Fagaras 176     Sibiu 253
Giurgiu 77      Timisoara 329
Hirsova 151     Urziceni 80
Iasi 226        Vaslui 199
Lugoj 244       Zerind 374

UI
--
LEFT  : one common map

RIGHT :
    algorithm buttons
    run-all / reset
    live status
    comparison table
    best-search card
    small clean legend

VISUAL COLOURS
--------------
DFS   = purple
BFS   = blue
UCS   = green
GBFS  = pink
A*    = orange

Current node    = yellow
Final path      = red
Frontier        = grey ring

During traversal, the CURRENT PATH is drawn in the selected
algorithm's colour.

After Bucharest is reached, the final solution route is drawn RED.

DFS NOTE
--------
DFS is implemented recursively and therefore the displayed
path-so-far is the actual DFS recursion stack.

The neighbour order is explicitly defined to make the result
deterministic:

Arad -> Zerind, Timisoara, Sibiu

Therefore this simulation gives:
Arad -> Zerind -> Oradea -> Sibiu -> Fagaras -> Bucharest

The exact DFS route can vary if a different neighbour ordering
is chosen; that is normal for DFS.

BEST SEARCH
-----------
The program determines the "best overall" only AFTER all searches
have completed.

For this Romania graph it compares:
    1. final path cost
    2. nodes expanded

Raw execution time is displayed, but on a graph this small it is
not used as the main "best" criterion because microsecond-level
timings vary by machine.

Install
-------
pip install matplotlib

Run
---
python romania_search_visualizer_final.py
"""

from __future__ import annotations

import heapq
import time
from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch, Patch
from matplotlib.widgets import Button


# ============================================================
# CONFIGURATION
# ============================================================

START = "Arad"
GOAL = "Bucharest"

# Distinct colours for every search.
ALGORITHM_COLORS = {
    "DFS": "#8E44AD",       # purple
    "BFS": "#3498DB",       # blue
    "UCS": "#27AE60",       # green
    "GBFS": "#D81B60",      # pink / magenta
    "A*": "#E67E22",        # orange
}

CURRENT_COLOR = "#FFD21F"      # yellow
FINAL_PATH_COLOR = "#E53935"   # red
FRONTIER_COLOR = "#95A5A6"     # grey
ROAD_COLOR = "#B8BEC5"
NODE_EDGE = "#20252B"
TEXT_COLOR = "#26323B"
MUTED_TEXT = "#6E7B87"
PANEL_BG = "#F4F6F8"


# ============================================================
# ROMANIA MAP
# ============================================================

EDGES: List[Tuple[str, str, int]] = [
    ("Oradea", "Zerind", 71),
    ("Zerind", "Arad", 75),
    ("Oradea", "Sibiu", 151),
    ("Arad", "Sibiu", 140),
    ("Arad", "Timisoara", 118),
    ("Timisoara", "Lugoj", 111),
    ("Lugoj", "Mehadia", 70),
    ("Mehadia", "Drobeta", 75),
    ("Drobeta", "Craiova", 120),
    ("Craiova", "Pitesti", 138),
    ("Craiova", "Rimnicu Vilcea", 146),
    ("Rimnicu Vilcea", "Sibiu", 80),
    ("Rimnicu Vilcea", "Pitesti", 97),
    ("Sibiu", "Fagaras", 99),
    ("Fagaras", "Bucharest", 211),
    ("Pitesti", "Bucharest", 101),
    ("Bucharest", "Giurgiu", 90),
    ("Bucharest", "Urziceni", 85),
    ("Urziceni", "Vaslui", 142),
    ("Vaslui", "Iasi", 92),
    ("Iasi", "Neamt", 87),
    ("Urziceni", "Hirsova", 98),
    ("Hirsova", "Eforie", 86),
]

# Map coordinates.
POS = {
    "Oradea": (1.00, 8.20),
    "Zerind": (0.72, 7.15),
    "Arad": (0.35, 6.00),
    "Timisoara": (0.40, 4.45),
    "Lugoj": (1.65, 3.52),
    "Mehadia": (1.70, 2.52),
    "Drobeta": (1.70, 1.48),
    "Craiova": (3.72, 0.92),
    "Sibiu": (3.00, 5.42),
    "Rimnicu Vilcea": (3.58, 4.10),
    "Fagaras": (5.35, 5.30),
    "Pitesti": (5.58, 3.74),
    "Bucharest": (7.48, 3.00),
    "Giurgiu": (6.90, 0.44),
    "Urziceni": (8.82, 3.52),
    "Hirsova": (10.40, 3.52),
    "Eforie": (11.00, 2.00),
    "Vaslui": (9.96, 6.00),
    "Iasi": (9.06, 7.50),
    "Neamt": (7.78, 8.34),
}


# ============================================================
# EXPLICIT NEIGHBOUR ORDER
# ============================================================
#
# This prevents arbitrary dictionary/set ordering from changing
# the visible search behaviour.
#
# DFS in particular depends on successor ordering.
#
NEIGHBOUR_ORDER = {
    "Arad": ["Zerind", "Timisoara", "Sibiu"],
    "Zerind": ["Arad", "Oradea"],
    "Oradea": ["Zerind", "Sibiu"],
    "Timisoara": ["Arad", "Lugoj"],
    "Lugoj": ["Timisoara", "Mehadia"],
    "Mehadia": ["Lugoj", "Drobeta"],
    "Drobeta": ["Mehadia", "Craiova"],
    "Craiova": ["Drobeta", "Rimnicu Vilcea", "Pitesti"],
    "Sibiu": ["Arad", "Oradea", "Fagaras", "Rimnicu Vilcea"],
    "Rimnicu Vilcea": ["Sibiu", "Craiova", "Pitesti"],
    "Fagaras": ["Sibiu", "Bucharest"],
    "Pitesti": ["Rimnicu Vilcea", "Craiova", "Bucharest"],
    "Bucharest": ["Fagaras", "Pitesti", "Giurgiu", "Urziceni"],
    "Giurgiu": ["Bucharest"],
    "Urziceni": ["Bucharest", "Vaslui", "Hirsova"],
    "Vaslui": ["Urziceni", "Iasi"],
    "Iasi": ["Vaslui", "Neamt"],
    "Neamt": ["Iasi"],
    "Hirsova": ["Urziceni", "Eforie"],
    "Eforie": ["Hirsova"],
}


# ============================================================
# HEURISTIC h(n)
# ============================================================

# Values from the supplied heuristic table.
HEURISTIC = {
    "Arad": 366,
    "Bucharest": 0,
    "Craiova": 160,
    "Drobeta": 242,
    "Eforie": 161,
    "Fagaras": 176,
    "Giurgiu": 77,
    "Hirsova": 151,
    "Iasi": 226,
    "Lugoj": 244,
    "Mehadia": 241,
    "Neamt": 234,
    "Oradea": 380,
    "Pitesti": 100,
    "Rimnicu Vilcea": 193,
    "Sibiu": 253,
    "Timisoara": 329,
    "Urziceni": 80,
    "Vaslui": 199,
    "Zerind": 374,
}


# ============================================================
# GRAPH CREATION
# ============================================================

def build_graph() -> Dict[str, List[Tuple[str, int]]]:
    edge_cost = {}

    for u, v, cost in EDGES:
        edge_cost[(u, v)] = cost
        edge_cost[(v, u)] = cost

    graph = {}

    for city, neighbours in NEIGHBOUR_ORDER.items():
        graph[city] = [
            (n, edge_cost[(city, n)])
            for n in neighbours
        ]

    return graph


GRAPH = build_graph()


# ============================================================
# RESULT OBJECT
# ============================================================

@dataclass
class SearchResult:
    name: str
    events: List[dict]
    expanded_order: List[str]
    path: List[str]
    cost: int
    time_ms: float


# ============================================================
# COMMON HELPERS
# ============================================================

def reconstruct_path(
    parent: Dict[str, Optional[str]],
    target: str,
) -> List[str]:
    if target not in parent:
        return []

    path: List[str] = []
    node: Optional[str] = target

    while node is not None:
        path.append(node)
        node = parent.get(node)

    path.reverse()

    if not path or path[0] != START:
        return []

    return path


def get_path_cost(path: List[str]) -> int:
    total = 0

    for u, v in zip(path, path[1:]):
        for neighbour, cost in GRAPH[u]:
            if neighbour == v:
                total += cost
                break

    return total


def make_event(
    expanded: List[str],
    current: str,
    path_so_far: List[str],
    frontier: List[str],
    parent: Dict[str, Optional[str]],
    finished: bool = False,
) -> dict:
    return {
        "expanded": list(expanded),
        "current": current,
        "path_so_far": list(path_so_far),
        "frontier": list(frontier),
        "parent": dict(parent),
        "finished": finished,
    }


# ============================================================
# DFS
# ============================================================

def run_dfs() -> SearchResult:
    t0 = time.perf_counter()

    visited = set()
    parent: Dict[str, Optional[str]] = {
        START: None
    }

    expanded: List[str] = []
    events: List[dict] = []

    found = False

    def dfs(
        node: str,
        current_path: List[str],
    ) -> bool:
        nonlocal found

        visited.add(node)
        expanded.append(node)

        events.append(
            make_event(
                expanded=expanded,
                current=node,
                path_so_far=current_path,
                frontier=[],
                parent=parent,
                finished=(node == GOAL),
            )
        )

        if node == GOAL:
            found = True
            return True

        for neighbour, _ in GRAPH[node]:
            if neighbour in visited:
                continue

            parent[neighbour] = node

            if dfs(
                neighbour,
                current_path + [neighbour],
            ):
                return True

        return False

    dfs(START, [START])

    elapsed = (time.perf_counter() - t0) * 1000
    path = reconstruct_path(parent, GOAL)

    return SearchResult(
        "DFS",
        events,
        expanded,
        path,
        get_path_cost(path),
        elapsed,
    )


# ============================================================
# BFS
# ============================================================

def run_bfs() -> SearchResult:
    t0 = time.perf_counter()

    queue = deque([START])
    discovered = {START}
    parent: Dict[str, Optional[str]] = {
        START: None
    }

    expanded: List[str] = []
    events: List[dict] = []

    while queue:
        current = queue.popleft()
        current_path = reconstruct_path(
            parent,
            current,
        )

        expanded.append(current)

        events.append(
            make_event(
                expanded,
                current,
                current_path,
                list(queue),
                parent,
                current == GOAL,
            )
        )

        if current == GOAL:
            break

        for neighbour, _ in GRAPH[current]:
            if neighbour not in discovered:
                discovered.add(neighbour)
                parent[neighbour] = current
                queue.append(neighbour)

    elapsed = (time.perf_counter() - t0) * 1000
    path = reconstruct_path(parent, GOAL)

    return SearchResult(
        "BFS",
        events,
        expanded,
        path,
        get_path_cost(path),
        elapsed,
    )


# ============================================================
# UCS
# ============================================================

def run_ucs() -> SearchResult:
    t0 = time.perf_counter()

    # (g, tie_breaker, node)
    pq: List[Tuple[int, int, str]] = [
        (0, 0, START)
    ]

    counter = 0
    best_g = {START: 0}

    parent: Dict[str, Optional[str]] = {
        START: None
    }

    closed = set()
    expanded: List[str] = []
    events: List[dict] = []

    while pq:
        g, _, current = heapq.heappop(pq)

        if g != best_g.get(
            current,
            float("inf"),
        ):
            continue

        if current in closed:
            continue

        closed.add(current)
        expanded.append(current)

        current_path = reconstruct_path(
            parent,
            current,
        )

        events.append(
            make_event(
                expanded,
                current,
                current_path,
                [item[2] for item in pq],
                parent,
                current == GOAL,
            )
        )

        if current == GOAL:
            break

        for neighbour, road_cost in GRAPH[current]:
            candidate = g + road_cost

            if candidate < best_g.get(
                neighbour,
                float("inf"),
            ):
                best_g[neighbour] = candidate
                parent[neighbour] = current

                counter += 1

                heapq.heappush(
                    pq,
                    (
                        candidate,
                        counter,
                        neighbour,
                    ),
                )

    elapsed = (time.perf_counter() - t0) * 1000
    path = reconstruct_path(parent, GOAL)

    return SearchResult(
        "UCS",
        events,
        expanded,
        path,
        get_path_cost(path),
        elapsed,
    )


# ============================================================
# GREEDY BEST-FIRST SEARCH
# ============================================================

def run_gbfs() -> SearchResult:
    t0 = time.perf_counter()

    # Priority is ONLY h(n).
    # This is what makes Greedy Best First Search different from A*.
    pq: List[Tuple[int, int, str]] = [
        (HEURISTIC[START], 0, START)
    ]

    counter = 0
    discovered = {START}

    parent: Dict[str, Optional[str]] = {
        START: None
    }

    expanded: List[str] = []
    events: List[dict] = []

    while pq:
        _, _, current = heapq.heappop(pq)

        current_path = reconstruct_path(
            parent,
            current,
        )

        expanded.append(current)

        events.append(
            make_event(
                expanded,
                current,
                current_path,
                [item[2] for item in pq],
                parent,
                current == GOAL,
            )
        )

        if current == GOAL:
            break

        for neighbour, _ in GRAPH[current]:
            if neighbour in discovered:
                continue

            discovered.add(neighbour)
            parent[neighbour] = current

            counter += 1

            heapq.heappush(
                pq,
                (
                    HEURISTIC[neighbour],
                    counter,
                    neighbour,
                ),
            )

    elapsed = (time.perf_counter() - t0) * 1000
    path = reconstruct_path(parent, GOAL)

    return SearchResult(
        "GBFS",
        events,
        expanded,
        path,
        get_path_cost(path),
        elapsed,
    )


# ============================================================
# A*
# ============================================================

def run_astar() -> SearchResult:
    t0 = time.perf_counter()

    # Priority is f(n) = g(n) + h(n).
    pq: List[Tuple[int, int, int, str]] = [
        (
            HEURISTIC[START],
            0,
            0,
            START,
        )
    ]

    counter = 0
    g_score = {START: 0}

    parent: Dict[str, Optional[str]] = {
        START: None
    }

    closed = set()
    expanded: List[str] = []
    events: List[dict] = []

    while pq:
        _, g, _, current = heapq.heappop(pq)

        if g != g_score.get(
            current,
            float("inf"),
        ):
            continue

        if current in closed:
            continue

        closed.add(current)
        expanded.append(current)

        current_path = reconstruct_path(
            parent,
            current,
        )

        events.append(
            make_event(
                expanded,
                current,
                current_path,
                [item[3] for item in pq],
                parent,
                current == GOAL,
            )
        )

        if current == GOAL:
            break

        for neighbour, road_cost in GRAPH[current]:
            candidate_g = g + road_cost

            if candidate_g < g_score.get(
                neighbour,
                float("inf"),
            ):
                g_score[neighbour] = candidate_g
                parent[neighbour] = current

                f = candidate_g + HEURISTIC[neighbour]

                counter += 1

                heapq.heappush(
                    pq,
                    (
                        f,
                        candidate_g,
                        counter,
                        neighbour,
                    ),
                )

    elapsed = (time.perf_counter() - t0) * 1000
    path = reconstruct_path(parent, GOAL)

    return SearchResult(
        "A*",
        events,
        expanded,
        path,
        get_path_cost(path),
        elapsed,
    )


SEARCH_FUNCTIONS = {
    "DFS": run_dfs,
    "BFS": run_bfs,
    "UCS": run_ucs,
    "GBFS": run_gbfs,
    "A*": run_astar,
}


# ============================================================
# VISUALIZER
# ============================================================

class SearchVisualizer:

    def __init__(self) -> None:
        self.fig = plt.figure(
            figsize=(19, 10.5),
            facecolor="white",
        )

        # ----------------------------------------------------
        # LEFT: ONE COMMON MAP
        # ----------------------------------------------------
        self.ax_map = self.fig.add_axes(
            [0.025, 0.095, 0.62, 0.805],
            facecolor="white",
        )

        # ----------------------------------------------------
        # RIGHT: PANEL
        # ----------------------------------------------------
        self.ax_panel = self.fig.add_axes(
            [0.665, 0.055, 0.315, 0.865],
            facecolor=PANEL_BG,
        )

        self.ax_panel.set_xticks([])
        self.ax_panel.set_yticks([])

        for spine in self.ax_panel.spines.values():
            spine.set_color("#D7DEE4")
            spine.set_linewidth(1)

        # Results store.
        self.results: Dict[str, SearchResult] = {}

        # Current animation state.
        self.current_result: Optional[SearchResult] = None
        self.current_name: Optional[str] = None
        self.animation: Optional[FuncAnimation] = None
        self.animating = False

        # Run-all queue.
        self.run_all_queue: List[str] = []

        # Build UI.
        self._build_header()
        self._build_controls()
        self._build_results()
        self._build_best_card()
        self._build_legend()

        self._draw_map()

    # ========================================================
    # HEADER
    # ========================================================

    def _build_header(self) -> None:
        self.fig.text(
            0.025,
            0.958,
            "ARAD  →  BUCHAREST",
            fontsize=21,
            fontweight="bold",
            color=TEXT_COLOR,
            ha="left",
        )

        self.fig.text(
            0.025,
            0.925,
            "Interactive Search Algorithm Simulation",
            fontsize=11,
            color=MUTED_TEXT,
            ha="left",
        )

    # ========================================================
    # CONTROLS
    # ========================================================

    def _build_controls(self) -> None:
        self.ax_panel.text(
            0.06,
            0.955,
            "SEARCH CONTROLS",
            fontsize=13.5,
            fontweight="bold",
            color=TEXT_COLOR,
            transform=self.ax_panel.transAxes,
            va="top",
        )

        self.ax_panel.text(
            0.06,
            0.918,
            "Run one search or run all five in sequence.",
            fontsize=8.9,
            color=MUTED_TEXT,
            transform=self.ax_panel.transAxes,
            va="top",
        )

        self.buttons: Dict[str, Button] = {}

        positions = {
            "DFS": (0.06, 0.815),
            "BFS": (0.53, 0.815),
            "UCS": (0.06, 0.744),
            "GBFS": (0.53, 0.744),
            "A*": (0.06, 0.673),
        }

        for name, (x, y) in positions.items():
            btn_ax = self.fig.add_axes(
                [
                    0.665 + 0.315 * x,
                    0.055 + 0.865 * y,
                    0.315 * 0.37,
                    0.865 * 0.052,
                ]
            )

            button = Button(
                btn_ax,
                name,
                color="white",
                hovercolor=ALGORITHM_COLORS[name],
            )

            button.label.set_color(
                ALGORITHM_COLORS[name]
            )
            button.label.set_fontweight("bold")
            button.label.set_fontsize(9.2)

            button.on_clicked(
                lambda event, alg=name:
                self.start_search(alg)
            )

            self.buttons[name] = button

        # RUN ALL
        run_all_ax = self.fig.add_axes(
            [
                0.665 + 0.315 * 0.53,
                0.055 + 0.865 * 0.673,
                0.315 * 0.37,
                0.865 * 0.052,
            ]
        )

        self.run_all_button = Button(
            run_all_ax,
            "RUN ALL",
            color="#263238",
            hovercolor="#455A64",
        )

        self.run_all_button.label.set_color("white")
        self.run_all_button.label.set_fontweight("bold")
        self.run_all_button.label.set_fontsize(9)

        self.run_all_button.on_clicked(
            self.run_all
        )

        # RESET
        reset_ax = self.fig.add_axes(
            [
                0.665 + 0.315 * 0.06,
                0.055 + 0.865 * 0.608,
                0.315 * 0.84,
                0.865 * 0.037,
            ]
        )

        self.reset_button = Button(
            reset_ax,
            "RESET MAP + RESULTS",
            color="white",
            hovercolor="#E9EDF0",
        )

        self.reset_button.label.set_color("#455A64")
        self.reset_button.label.set_fontweight("bold")
        self.reset_button.label.set_fontsize(7.8)

        self.reset_button.on_clicked(
            self.reset
        )

        self.status_text = self.ax_panel.text(
            0.06,
            0.565,
            "Status: Ready",
            fontsize=9.1,
            fontweight="bold",
            color="#54606A",
            transform=self.ax_panel.transAxes,
            va="top",
        )

    # ========================================================
    # RESULTS TABLE
    # ========================================================

    def _build_results(self) -> None:
        self.ax_panel.text(
            0.06,
            0.525,
            "RESULTS",
            fontsize=12.8,
            fontweight="bold",
            color=TEXT_COLOR,
            transform=self.ax_panel.transAxes,
        )

        self.ax_panel.text(
            0.06,
            0.498,
            "Final path • expanded nodes • execution time • cost",
            fontsize=8.1,
            color=MUTED_TEXT,
            transform=self.ax_panel.transAxes,
        )

        self.ax_table = self.fig.add_axes(
            [0.675, 0.335, 0.295, 0.145]
        )

        self.ax_table.axis("off")

        self._draw_empty_table()

    def _format_path(self, path: List[str]) -> str:
        text = " → ".join(path)

        # One controlled line break, never one city per line.
        if len(text) <= 49:
            return text

        mid = len(path) // 2

        return (
            " → ".join(path[:mid])
            + "\n"
            + " → ".join(path[mid:])
        )

    def _draw_empty_table(self) -> None:
        self.ax_table.clear()
        self.ax_table.axis("off")

        self.ax_table.text(
            0.5,
            0.52,
            "No simulations completed yet.",
            ha="center",
            va="center",
            fontsize=8.9,
            color="#7A8791",
        )

        self.ax_table.text(
            0.5,
            0.37,
            "Use the search buttons above.",
            ha="center",
            va="center",
            fontsize=7.8,
            color="#9AA4AC",
        )

    def update_table(self) -> None:
        self.ax_table.clear()
        self.ax_table.axis("off")

        order = [
            "DFS",
            "BFS",
            "UCS",
            "GBFS",
            "A*",
        ]

        rows = []

        for name in order:
            result = self.results.get(name)

            if result is None:
                continue

            rows.append(
                [
                    name,
                    self._format_path(result.path),
                    str(len(result.expanded_order)),
                    f"{result.time_ms:.4f}",
                    str(result.cost),
                ]
            )

        if not rows:
            self._draw_empty_table()
            self.fig.canvas.draw_idle()
            return

        table = self.ax_table.table(
            cellText=rows,
            colLabels=[
                "SEARCH",
                "FINAL PATH",
                "NODES",
                "TIME (ms)",
                "COST",
            ],
            loc="center",
            cellLoc="center",
            colLoc="center",
            colWidths=[
                0.14,
                0.47,
                0.10,
                0.15,
                0.10,
            ],
        )

        table.auto_set_font_size(False)
        table.set_fontsize(6.7)
        table.scale(1, 1.75)

        # Header.
        for col in range(5):
            cell = table[(0, col)]

            cell.set_facecolor("#263238")
            cell.set_edgecolor("white")
            cell.set_linewidth(0.7)

            cell.set_text_props(
                color="white",
                fontweight="bold",
                ha="center",
                va="center",
            )

        # Body.
        row_names = [
            row[0]
            for row in rows
        ]

        for row_idx, name in enumerate(
            row_names,
            start=1,
        ):
            for col_idx in range(5):
                cell = table[(row_idx, col_idx)]

                cell.set_edgecolor("#D5DDE3")
                cell.set_linewidth(0.65)

                if col_idx == 0:
                    cell.set_facecolor(
                        ALGORITHM_COLORS[name]
                    )

                    cell.set_text_props(
                        color="white",
                        fontweight="bold",
                        ha="center",
                        va="center",
                    )

                else:
                    cell.set_facecolor("white")

                    cell.set_text_props(
                        color=TEXT_COLOR,
                        ha="left"
                        if col_idx == 1
                        else "center",
                        va="center",
                    )

        self.fig.canvas.draw_idle()

    # ========================================================
    # BEST SEARCH CARD
    # ========================================================

    def _build_best_card(self) -> None:
        self.ax_best = self.fig.add_axes(
            [0.675, 0.235, 0.295, 0.075],
            facecolor="white",
        )

        self.ax_best.set_xticks([])
        self.ax_best.set_yticks([])

        for spine in self.ax_best.spines.values():
            spine.set_color("#D5DDE3")
            spine.set_linewidth(1)

        self.ax_best.text(
            0.035,
            0.79,
            "BEST SEARCH",
            fontsize=9.4,
            fontweight="bold",
            color=TEXT_COLOR,
            transform=self.ax_best.transAxes,
        )

        self.best_main = self.ax_best.text(
            0.035,
            0.48,
            "Run all searches to compare.",
            fontsize=8.4,
            fontweight="bold",
            color="#54606A",
            transform=self.ax_best.transAxes,
        )

        self.best_detail = self.ax_best.text(
            0.035,
            0.18,
            "Based on path cost first, then nodes expanded.",
            fontsize=6.8,
            color=MUTED_TEXT,
            transform=self.ax_best.transAxes,
        )

    def update_best_card(self) -> None:
        # Only announce "best overall" when all five have completed.
        required = [
            "DFS",
            "BFS",
            "UCS",
            "GBFS",
            "A*",
        ]

        if not all(
            name in self.results
            for name in required
        ):
            self.best_main.set_text(
                f"{len(self.results)}/5 searches completed."
            )
            self.best_main.set_color(
                "#54606A"
            )

            self.best_detail.set_text(
                "Complete all simulations to determine the best."
            )

            self.fig.canvas.draw_idle()
            return

        candidates = list(
            self.results.values()
        )

        # Main objective: lowest route cost.
        best_cost = min(
            r.cost
            for r in candidates
        )

        cost_winners = [
            r
            for r in candidates
            if r.cost == best_cost
        ]

        # Tie-breaker: fewer expanded nodes.
        best_nodes = min(
            len(r.expanded_order)
            for r in cost_winners
        )

        winners = [
            r
            for r in cost_winners
            if len(r.expanded_order) == best_nodes
        ]

        best = winners[0]

        self.best_main.set_text(
            f"{best.name}   |   cost {best.cost}   |   "
            f"{len(best.expanded_order)} nodes"
        )

        self.best_main.set_color(
            ALGORITHM_COLORS[best.name]
        )

        self.best_detail.set_text(
            "Best overall here = lowest path cost, "
            "then fewest expanded nodes."
        )

        self.ax_best.patch.set_facecolor(
            "#FFFDF7"
        )

        self.fig.canvas.draw_idle()

    # ========================================================
    # SMALL LEGEND
    # ========================================================

    def _build_legend(self) -> None:
        self.ax_legend = self.fig.add_axes(
            [0.675, 0.065, 0.295, 0.15],
            facecolor="white",
        )

        self.ax_legend.set_xticks([])
        self.ax_legend.set_yticks([])

        for spine in self.ax_legend.spines.values():
            spine.set_color("#D5DDE3")
            spine.set_linewidth(1)

        self.ax_legend.set_title(
            "LEGEND",
            loc="left",
            fontsize=9.4,
            fontweight="bold",
            color=TEXT_COLOR,
            pad=6,
        )

        handles = [
            Patch(
                facecolor=ALGORITHM_COLORS["DFS"],
                edgecolor="black",
                label="DFS explored/path",
            ),
            Patch(
                facecolor=ALGORITHM_COLORS["BFS"],
                edgecolor="black",
                label="BFS explored/path",
            ),
            Patch(
                facecolor=ALGORITHM_COLORS["UCS"],
                edgecolor="black",
                label="UCS explored/path",
            ),
            Patch(
                facecolor=ALGORITHM_COLORS["GBFS"],
                edgecolor="black",
                label="GBFS explored/path",
            ),
            Patch(
                facecolor=ALGORITHM_COLORS["A*"],
                edgecolor="black",
                label="A* explored/path",
            ),
            Line2D(
                [0],
                [0],
                marker="o",
                color="none",
                markerfacecolor=CURRENT_COLOR,
                markeredgecolor="black",
                markersize=8,
                label="Current node",
            ),
            Line2D(
                [0],
                [0],
                color=FINAL_PATH_COLOR,
                linewidth=4,
                label="Final path",
            ),
            Line2D(
                [0],
                [0],
                marker="o",
                color="none",
                markerfacecolor="white",
                markeredgecolor=FRONTIER_COLOR,
                markeredgewidth=1.8,
                markersize=8,
                label="Frontier",
            ),
        ]

        self.ax_legend.legend(
            handles=handles,
            loc="center",
            ncol=2,
            frameon=False,
            fontsize=6.8,
            handlelength=1.6,
            handletextpad=0.6,
            labelspacing=0.65,
            columnspacing=1.5,
        )

    # ========================================================
    # MAP
    # ========================================================

    def _draw_map(self) -> None:
        self.ax_map.clear()

        # Roads.
        for u, v, cost in EDGES:
            x1, y1 = POS[u]
            x2, y2 = POS[v]

            self.ax_map.plot(
                [x1, x2],
                [y1, y2],
                color=ROAD_COLOR,
                linewidth=2.25,
                zorder=1,
            )

            mx = (x1 + x2) / 2
            my = (y1 + y2) / 2

            self.ax_map.text(
                mx,
                my + 0.095,
                str(cost),
                fontsize=7.7,
                color="#65717C",
                ha="center",
                va="center",
                bbox=dict(
                    boxstyle="round,pad=0.06",
                    facecolor="white",
                    edgecolor="none",
                    alpha=0.88,
                ),
                zorder=2,
            )

        # Nodes.
        for city, (x, y) in POS.items():
            fill = "white"

            if city == START:
                fill = "#E3F2FD"

            if city == GOAL:
                fill = "#FFF3CD"

            self.ax_map.scatter(
                [x],
                [y],
                s=610,
                facecolor=fill,
                edgecolor=NODE_EDGE,
                linewidth=1.45,
                zorder=3,
            )

        # Labels.
        offsets = {
            "Oradea": (0.09, 0.09),
            "Zerind": (0.09, 0.08),
            "Arad": (0.10, 0.10),
            "Timisoara": (0.09, 0.09),
            "Lugoj": (0.09, 0.09),
            "Mehadia": (0.09, 0.09),
            "Drobeta": (0.09, 0.09),
            "Craiova": (0.09, 0.09),
            "Sibiu": (0.09, 0.09),
            "Rimnicu Vilcea": (0.09, 0.09),
            "Fagaras": (0.09, 0.09),
            "Pitesti": (0.09, 0.09),
            "Bucharest": (0.09, 0.09),
            "Giurgiu": (0.09, -0.27),
            "Urziceni": (0.09, 0.09),
            "Hirsova": (0.09, 0.09),
            "Eforie": (0.09, -0.27),
            "Vaslui": (0.09, 0.09),
            "Iasi": (0.09, 0.09),
            "Neamt": (0.09, 0.09),
        }

        for city, (x, y) in POS.items():
            dx, dy = offsets.get(
                city,
                (0.09, 0.09),
            )

            self.ax_map.text(
                x + dx,
                y + dy,
                city,
                fontsize=8.8,
                fontweight="bold"
                if city in (START, GOAL)
                else "normal",
                color=TEXT_COLOR,
                zorder=5,
            )

        sx, sy = POS[START]
        gx, gy = POS[GOAL]

        self.ax_map.text(
            sx,
            sy + 0.50,
            "START",
            color="#1976D2",
            fontsize=7.8,
            fontweight="bold",
            ha="center",
        )

        self.ax_map.text(
            gx,
            gy + 0.50,
            "GOAL",
            color="#B7791F",
            fontsize=7.8,
            fontweight="bold",
            ha="center",
        )

        self.ax_map.set_xlim(-0.50, 11.72)
        self.ax_map.set_ylim(0.0, 8.90)
        self.ax_map.set_aspect("equal")
        self.ax_map.axis("off")

    # ========================================================
    # DRAW AN ANIMATION FRAME
    # ========================================================

    def draw_frame(self, frame: int) -> None:
        result = self.current_result

        if result is None:
            self._draw_map()
            return

        event = result.events[frame]
        colour = ALGORITHM_COLORS[result.name]

        self._draw_map()

        expanded = set(event["expanded"])
        path_so_far = event["path_so_far"]
        path_set = set(path_so_far)
        frontier = set(event["frontier"])
        current = event["current"]

        # ----------------------------------------------------
        # 1. PATH-SO-FAR IN ALGORITHM COLOUR
        # ----------------------------------------------------
        if len(path_so_far) >= 2:
            for u, v in zip(
                path_so_far,
                path_so_far[1:],
            ):
                x1, y1 = POS[u]
                x2, y2 = POS[v]

                self.ax_map.plot(
                    [x1, x2],
                    [y1, y2],
                    color=colour,
                    linewidth=6.0,
                    solid_capstyle="round",
                    zorder=6,
                )

            for city in path_so_far:
                x, y = POS[city]

                self.ax_map.scatter(
                    [x],
                    [y],
                    s=670,
                    facecolor=colour,
                    edgecolor="white",
                    linewidth=2.0,
                    zorder=7,
                )

        # ----------------------------------------------------
        # 2. OTHER EXPLORED NODES
        # ----------------------------------------------------
        for city in expanded:
            if city in path_set:
                continue

            x, y = POS[city]

            self.ax_map.scatter(
                [x],
                [y],
                s=670,
                facecolor=colour,
                edgecolor="white",
                linewidth=2.0,
                alpha=0.92,
                zorder=7,
            )

        # ----------------------------------------------------
        # 3. FRONTIER
        # ----------------------------------------------------
        for city in frontier:
            if city in expanded:
                continue

            x, y = POS[city]

            self.ax_map.scatter(
                [x],
                [y],
                s=735,
                facecolor="none",
                edgecolor=FRONTIER_COLOR,
                linewidth=2.3,
                zorder=8,
            )

        # ----------------------------------------------------
        # 4. CURRENT NODE
        # ----------------------------------------------------
        x, y = POS[current]

        self.ax_map.scatter(
            [x],
            [y],
            s=730,
            facecolor=CURRENT_COLOR,
            edgecolor="black",
            linewidth=2.6,
            zorder=10,
        )

        # ----------------------------------------------------
        # 5. FINAL PATH
        # ----------------------------------------------------
        if event["finished"]:
            final_path = reconstruct_path(
                event["parent"],
                GOAL,
            )

            for u, v in zip(
                final_path,
                final_path[1:],
            ):
                x1, y1 = POS[u]
                x2, y2 = POS[v]

                self.ax_map.plot(
                    [x1, x2],
                    [y1, y2],
                    color=FINAL_PATH_COLOR,
                    linewidth=6.6,
                    solid_capstyle="round",
                    zorder=11,
                )

            for city in final_path:
                x, y = POS[city]

                self.ax_map.scatter(
                    [x],
                    [y],
                    s=715,
                    facecolor=FINAL_PATH_COLOR,
                    edgecolor="white",
                    linewidth=2.6,
                    zorder=12,
                )

            bx, by = POS[GOAL]

            self.ax_map.scatter(
                [bx],
                [by],
                s=275,
                facecolor=CURRENT_COLOR,
                edgecolor="black",
                linewidth=1.8,
                zorder=13,
            )

        # ----------------------------------------------------
        # SEARCH LABEL
        # ----------------------------------------------------
        self.ax_map.text(
            0.5,
            1.01,
            f"{result.name} SEARCH",
            transform=self.ax_map.transAxes,
            ha="center",
            va="bottom",
            fontsize=15.5,
            fontweight="bold",
            color=colour,
        )

        # ----------------------------------------------------
        # STATUS STRIP
        # ----------------------------------------------------
        path_text = " → ".join(path_so_far)

        if len(path_text) > 78:
            path_text = path_text[:75] + "..."

        status = (
            f"Step {frame + 1}/{len(result.events)}"
            f"   |   Current: {current}"
            f"   |   Nodes: {len(expanded)}\n"
            f"Path so far: {path_text}"
        )

        self.ax_map.text(
            0.5,
            -0.030,
            status,
            transform=self.ax_map.transAxes,
            ha="center",
            va="top",
            fontsize=8.6,
            color=TEXT_COLOR,
            bbox=dict(
                boxstyle="round,pad=0.34",
                facecolor="white",
                edgecolor=colour,
                linewidth=1.3,
            ),
        )

        self.fig.canvas.draw_idle()

    # ========================================================
    # START SEARCH
    # ========================================================

    def start_search(
        self,
        algorithm: str,
    ) -> None:
        if self.animating:
            return

        self._stop_animation()

        self.current_name = algorithm
        self.current_result = (
            SEARCH_FUNCTIONS[algorithm]()
        )
        self.animating = True

        self.status_text.set_text(
            f"Status: Running {algorithm}..."
        )
        self.status_text.set_color(
            ALGORITHM_COLORS[algorithm]
        )

        # Clear any run-all queue when manually selecting.
        self.run_all_queue.clear()

        # Button appearance.
        for name, button in self.buttons.items():
            if name == algorithm:
                button.ax.set_facecolor(
                    ALGORITHM_COLORS[name]
                )
                button.label.set_color("white")
            else:
                button.ax.set_facecolor("white")
                button.label.set_color(
                    ALGORITHM_COLORS[name]
                )

        self.draw_frame(0)

        self.animation = FuncAnimation(
            self.fig,
            self._animate,
            frames=range(
                len(self.current_result.events)
            ),
            interval=650,
            repeat=False,
            blit=False,
            cache_frame_data=False,
        )

    # ========================================================
    # RUN ALL
    # ========================================================

    def run_all(
        self,
        _event=None,
    ) -> None:
        if self.animating:
            return

        self.results.clear()
        self.update_table()
        self.update_best_card()

        # Deterministic order.
        self.run_all_queue = [
            "DFS",
            "BFS",
            "UCS",
            "GBFS",
            "A*",
        ]

        self._run_next()

    def _run_next(self) -> None:
        if not self.run_all_queue:
            self.status_text.set_text(
                "Status: All 5 simulations completed."
            )
            self.status_text.set_color(
                "#263238"
            )

            self.update_best_card()
            self.fig.canvas.draw_idle()
            return

        algorithm = self.run_all_queue.pop(0)

        # We intentionally don't clear results between searches.
        # This allows the side table to fill as the simulations finish.
        self._start_for_run_all(algorithm)

    def _start_for_run_all(
        self,
        algorithm: str,
    ) -> None:
        if self.animating:
            return

        self._stop_animation()

        self.current_name = algorithm
        self.current_result = (
            SEARCH_FUNCTIONS[algorithm]()
        )
        self.animating = True

        self.status_text.set_text(
            f"Status: Running {algorithm}..."
            f"   |   {5 - len(self.run_all_queue)} / 5"
        )

        self.status_text.set_color(
            ALGORITHM_COLORS[algorithm]
        )

        for name, button in self.buttons.items():
            if name == algorithm:
                button.ax.set_facecolor(
                    ALGORITHM_COLORS[name]
                )
                button.label.set_color("white")
            else:
                button.ax.set_facecolor("white")
                button.label.set_color(
                    ALGORITHM_COLORS[name]
                )

        self.draw_frame(0)

        self.animation = FuncAnimation(
            self.fig,
            self._animate,
            frames=range(
                len(self.current_result.events)
            ),
            interval=650,
            repeat=False,
            blit=False,
            cache_frame_data=False,
        )

    # ========================================================
    # ANIMATION CALLBACK
    # ========================================================

    def _animate(
        self,
        frame: int,
    ):
        if self.current_result is None:
            return []

        self.draw_frame(frame)

        if frame == (
            len(self.current_result.events) - 1
        ):
            self._finish_current()

        return []

    # ========================================================
    # FINISH CURRENT SEARCH
    # ========================================================

    def _finish_current(self) -> None:
        if not self.animating:
            return

        self.animating = False

        if self.current_result is None:
            return

        result = self.current_result

        self.results[result.name] = result

        self.update_table()
        self.update_best_card()

        self.status_text.set_text(
            f"Status: {result.name} completed"
            f"   |   Cost = {result.cost}"
        )

        self.status_text.set_color(
            ALGORITHM_COLORS[result.name]
        )

        self.draw_frame(
            len(result.events) - 1
        )

        # Continue RUN ALL.
        if self.run_all_queue:
            timer = self.fig.canvas.new_timer(
                interval=500
            )

            timer.single_shot = True

            timer.add_callback(
                self._run_next
            )

            timer.start()

    # ========================================================
    # RESET
    # ========================================================

    def reset(
        self,
        _event=None,
    ) -> None:
        self._stop_animation()

        self.results.clear()
        self.current_result = None
        self.current_name = None
        self.run_all_queue.clear()

        for name, button in self.buttons.items():
            button.ax.set_facecolor(
                "white"
            )

            button.label.set_color(
                ALGORITHM_COLORS[name]
            )

        self.status_text.set_text(
            "Status: Ready"
        )

        self.status_text.set_color(
            "#54606A"
        )

        self._draw_map()
        self.update_table()
        self.update_best_card()

        self.fig.canvas.draw_idle()

    # ========================================================
    # STOP ANIMATION
    # ========================================================

    def _stop_animation(self) -> None:
        if self.animation is not None:
            try:
                self.animation.event_source.stop()
            except Exception:
                pass

        self.animation = None
        self.animating = False

    # ========================================================
    # SHOW
    # ========================================================

    def show(self) -> None:
        plt.show()


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    app = SearchVisualizer()
    app.show()


if __name__ == "__main__":
    main()
