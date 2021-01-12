from GraphAlgoInterface import GraphAlgoInterface
from DiGraph import DiGraph
import json
import matplotlib.pyplot as plt
from RangeClasses import Range
from RangeClasses import Range2D
from RangeClasses import Range2Range
# import numpy as np


class GraphAlgo(GraphAlgoInterface):

    def __init__(self, graph: DiGraph):
        self.graph = graph

    def get_graph(self) -> DiGraph:
        return self.graph

    def load_from_json(self, file_name: str) -> bool:
        try:
            with open(file_name, "r") as file:
                data = json.load(file)
                for node in data["Nodes"]:
                    x, y, z = node["pos"].split(",")
                    p = (float(x), float(y), float(z))
                    self.graph.add_node(node["id"], p)
                for edge in data["Edges"]:
                    self.graph.add_edge(edge["src"], edge["dest"], edge["w"])
            return True
        except IOError as e:
            print(e)
            return False

    def save_to_json(self, file_name: str) -> bool:
        nodes = []
        edges = []
        for node in self.graph.nodes.values():
            x, y, z = node.getLocation()
            p = str(x) + "," + str(y) + "," + str(z)
            nodes.append({"id": node.getKey(), "pos": p})
            for dest in node.out_edges:
                edges.append({"src": node.getKey(), "w": node.out_edges[dest], "dest": dest})
        data = {"Nodes": nodes, "Edges": edges}
        try:
            with open(file_name, "w") as file:
                json.dump(data, fp=file)
            return True
        except IOError as e:
            print(e)
            return False

    def shortest_path(self, id1: int, id2: int) -> (float, list):
        if not self.graph:
            return None
        if id1 not in self.graph.nodes or id2 not in self.graph.nodes:
            return None

        src_node = self.graph.nodes.get(id1)
        stack = [src_node]
        prev = {}

        for node_key in self.graph.nodes:
            self.graph.nodes.get(node_key).tag = -1
        src_node.tag = 0
        while len(stack) > 0:
            node = stack.pop(0)
            for neighbor_key in node.getOutEdges():
                if self.graph.nodes[neighbor_key].getTag() == -1:
                    self.graph.nodes[neighbor_key].setTag(node.getTag() + node.out_edges[neighbor_key])
                    prev[neighbor_key] = node.getKey()
                    stack.append(self.graph.nodes[neighbor_key])
                    stack.sort(key=lambda x: x.tag, reverse=False)
                else:
                    if self.graph.nodes[neighbor_key].getTag() > node.getTag() + node.out_edges[neighbor_key]:
                        self.graph.nodes[neighbor_key].setTag(node.getTag() + node.out_edges[neighbor_key])
                        prev[neighbor_key] = node.getKey()
                        if self.graph.nodes[neighbor_key] in stack:
                            stack.remove(self.graph.nodes[neighbor_key])
                        stack.append(self.graph.nodes[neighbor_key])
                        stack.sort(key=lambda x: x.tag, reverse=False)
        if id2 not in prev:
            return None
        path = [id2]
        temp_key = id2
        while prev[temp_key] != id1:
            path.append(prev[temp_key])
            temp_key = prev[temp_key]
        path.append(id1)
        path.reverse()
        return self.graph.nodes[id2].tag, path

    def connected_component(self, id1: int) -> list:
        if id1 not in self.graph.nodes:
            return None
        visited = []
        next_to_visit = [self.graph.nodes[id1]]
        visited.append(id1)
        while len(next_to_visit) > 0:
            node = next_to_visit.pop(0)
            for ni in node.out_edges:
                if not visited.__contains__(ni):
                    visited.append(ni)
                    next_to_visit.append(self.graph.nodes[ni])
        visited_reverse = []
        next_to_visit.clear()
        visited_reverse.append(id1)
        reversed_g = self.graph.reversed_graph()
        next_to_visit.append(reversed_g.nodes[id1])
        while len(next_to_visit) > 0:
            node = next_to_visit.pop(0)
            for ni in node.out_edges:
                if not visited_reverse.__contains__(ni):
                    visited_reverse.append(ni)
                    next_to_visit.append(reversed_g.nodes[ni])
        id1_connected_component = []
        for node in visited:
            if visited_reverse.__contains__(node):
                id1_connected_component.append(node)
        return id1_connected_component

    def connected_components(self) -> list:  # list of lists
        nodes_that_left = []  # the keys of the nodes that doesn't belong to another connected_component
        connected_components = []  # list of all the connected_components in this graph
        for node in self.graph.nodes:
            nodes_that_left.append(node)
        while len(nodes_that_left) > 0:
            n = nodes_that_left[0]
            n_connected_component = sorted(self.connected_component(n))  # the connected_component of n
            connected_components.append(n_connected_component)
            for key in n_connected_component:
                nodes_that_left.remove(key)
        return connected_components



    def graph_range(self) -> Range2D:
        if len(self.graph.nodes) < 1:
            return None
        x0 = y0 = x1 = y1 = 0
        first = True
        for node in self.graph.nodes.values():
            if first:
                x0 = x1 = node.getLocation()[0]
                y0 = y1 = node.getLocation()[1]
                first = False
            x = node.getLocation()[0]
            y = node.getLocation()[1]
            if x < x0:
                x0 = x
            if x > x1:
                x1 = x
            if y < y0:
                y0 = y
            if y > y1:
                y1 = y
        x_range = Range(x0, x1)
        y_range = Range(y0, y1)
        dim = Range2D(x_range, y_range)
        return dim


    def plot_graph(self) -> None:
        x_vals = []
        y_vals = []
        for node in self.graph.nodes.values():
            x_vals.append(node.getLocation()[0])
            y_vals.append((node.getLocation()[1]))
            for out_edge_key in node.out_edges:
                delta_x = self.graph.nodes[out_edge_key].getLocation()[0] - node.getLocation()[0]
                if delta_x > 0:
                    delta_x = delta_x - 0.085
                if delta_x < 0:
                    delta_x = delta_x + 0.085
                delta_y = self.graph.nodes[out_edge_key].getLocation()[1] - node.getLocation()[1]
                if delta_y > 0:
                    delta_y = delta_y - 0.085
                if delta_y < 0:
                    delta_y = delta_y + 0.085
                plt.arrow(node.getLocation()[0], node.getLocation()[1], delta_x, delta_y,
                          head_length=0.1, head_width=0.1)
        plt.scatter(x_vals, y_vals)
        plt.show()

    def plot_graph2(self) -> None:
        x_vals = []
        y_vals = []
        xr = Range(0, 10)
        yr = Range(0, 10)
        dim = Range2D(xr, yr)
        r2r = Range2Range(self.graph_range(), dim)
        for node in self.graph.nodes.values():
            x, y = r2r.world_to_frame(node.getLocation()[0], node.getLocation()[1])
            x_vals.append(x)
            y_vals.append(y)
            for out_edge_key in node.out_edges:
                x_neighbor, y_neighbor = r2r.world_to_frame(self.graph.nodes[out_edge_key].getLocation()[0],
                                                            self.graph.nodes[out_edge_key].getLocation()[1])
                #    plt.plot([x,x_neighbor],[y,y_neighbor])
                delta_x = x_neighbor - x
                delta_y = y_neighbor - y
                p_x=delta_x/(delta_y+delta_x)

                if (delta_y > 0):
                    delta_y = delta_y - (1-p_x)*0.25
                if (delta_y < 0):
                    delta_y = delta_y + (1-p_x)*0.25
                if (delta_x > 0):
                    delta_x = delta_x - p_x*0.25
                if (delta_x < 0):
                    delta_x = delta_x + p_x*0.25
                plt.arrow(x, y, delta_x, delta_y,
                          head_length=0.25, head_width=0.15, width=0.000005)
        plt.scatter(x_vals, y_vals)
        plt.show()

# def graph1test() -> None:
#     x_val = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
#     y_val = [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
#     fig, ax = plt.subplots()
#
#     plt.annotate(xy=(5, 5), xytext=(1, 1), text="text", arrowprops=dict(facecolor='black', shrink=1))
#     ax.scatter(x_val, y_val)
#     # ax.annotate(33, (5, 5))
#     plt.plot(x_val, y_val)
#
#     # plt.grid()
#     # plt.legend()
#     plt.show()
#
# def graph2test() -> None:
#     x_val = [0, 1, 2, 7, 4, 5, 6, 3, 8, 9]
#     y_val = [0, 1, 4, 49, 16, 25, 36, 9, 64, 81]
#     fig, ax = plt.subplots()
#
#     # plt.annotate(xy=(5, 5), xytext=(1, 1), text="text", arrowprops=dict(facecolor='black', shrink=1))
#     ax.scatter(x_val, y_val)
#     # ax.annotate(33, (5, 5))
#     plt.plot(x_val, y_val)
#     ax.scatter(5.5, 15, color='yellow')
#     ax.scatter(5, 10, color='yellow')
#
#     # plt.grid()
#     # plt.legend()
#     plt.show()
#
#
# def graph3test() -> None:
#     x_val = [1, 5]
#     y_val = [1, 5]
#     fig, ax = plt.subplots()
#     # plt.plot(x_val, y_val, color="red")
#     plt.scatter(x_val, y_val, color="red")
#     x_val = [5, 3]
#     y_val = [1, 3]
#     # plt.plot(x_val, y_val, color="yellow")
#     plt.scatter(x_val, y_val, color="yellow")
#     plt.arrow(1, 1, 3, 3, head_length=0.1, head_width=0.1)
#     plt.arrow(3, 5, -2, -2, head_length=0.1, head_width=0.1)
#
#     plt.show()


# if __name__ == '__main__':
# graph1test()
# graph2test()
# graph3test()
# print("hey")
