# /pkg/handlers/mesh_handler.py
import heapq


class HeapEntry:
    def __init__(self, node: str, priority: float):
        self.node = node
        self.priority = priority

    def __lt__(self, other):
        return self.priority < other.priority


class Graph:
    def __init__(self):
        self.nodes: dict[str: dict[str: float]] = {}

    def add_node(self, ni: str, neighbors: dict) -> dict:
        self.nodes[ni] = neighbors
        return self.nodes

    def update_graph(self, new_graph: dict[str: dict[str: float]]):
        self.nodes = new_graph

    def traceback_path(self, target: str, parents: dict) -> list:
        path = []
        while target:
            path.append(target)
            target = parents[target]
        return list(reversed(path))

    def shortest_path(self, start: str, target: str, length_lim: float):
        OPEN: list = [HeapEntry(start, 0.0)]
        CLOSED: set = set()
        parents: dict = {start: None}
        distance: dict = {start: 0.0}

        while OPEN:
            current = heapq.heappop(OPEN).node

            if current == target:
                return self.traceback_path(target, parents)

            if current in CLOSED:
                continue

            for child in self.nodes[current].keys():
                if child in CLOSED:
                    continue
                if self.nodes[current][child] >= length_lim:
                    continue
                tentative_distance = distance[current] + self.nodes[current][child]

                if child not in distance.keys() or distance[child] > tentative_distance:
                    distance[child] = tentative_distance
                    parents[child] = current
                    heap_entry = HeapEntry(child, tentative_distance)
                    heapq.heappush(OPEN, heap_entry)


class MeshHandler:
    def __init__(self, ni):
        self.graph = Graph()
        self.ni = ni

    def find_path(self, target: str) -> list:
        start: str = self.ni

        path = self.graph.shortest_path(start, target, 8.0)

        return path

    def connection_graph(self, graph: dict[str: dict[str: float]]):
        self.graph.update_graph(graph)
