from GraphAlgoInterface import GraphAlgoInterface
from DiGraph import DiGraph
import json
import matplotlib.pyplot as plt
from RangeClasses import Range
from RangeClasses import Range2D
from RangeClasses import Range2Range


# class that represent the algo that we do on each graph
class GraphAlgo(GraphAlgoInterface):
    def __init__(self, graph=DiGraph()):
        """
        init function to graphAlgo
        """
        self.graph = graph

    def get_graph(self) -> DiGraph:
        """
        return the graph inside graphAlgo
        """
        return self.graph

    def load_from_json(self, file_name: str) -> bool:
        """
        load a graph from a file into self.graph
        the function return True if it succeeded. False if not
        """
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
        """
        save a self.graph to file
        the function return True if it succeeded. False if not
        """
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
        """
        the function find the shortest path from one node to a diff one
        the function return a tuple of the total weight of the path and a list of the path
        the function None if the nodes are not in the graph or there is no path that connect them
        """
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
        """
        the function gets a node key and return a list of the nodes that are connected component with him
        the function return None if the nodes isn't in the graph
        """
        if id1 not in self.graph.nodes:
            return []
        for node in self.graph.nodes.values():
            node.tag = 0
        next_to_visit = [self.graph.nodes[id1]]
        while next_to_visit:
            node = next_to_visit.pop()
            if node.tag == 0:
                node.tag = 1
                for ni in node.out_edges:
                    next_to_visit.append(self.graph.nodes[ni])
        next_to_visit.clear()
        reversed_g = self.graph.reversed_graph()
        for node in reversed_g.nodes.values():
            node.tag = 0
        next_to_visit.append(reversed_g.nodes[id1])
        while next_to_visit:
            node = next_to_visit.pop(0)
            if node.tag == 0:
                node.tag = 1
                for ni in node.out_edges:
                    next_to_visit.append(reversed_g.nodes[ni])
        id1_connected_component = []
        for node_key in self.graph.nodes:
            if reversed_g.nodes[node_key].tag == 1 and self.graph.nodes[node_key].tag == 1:
                id1_connected_component.append(node_key)
        return id1_connected_component

    def connected_components(self) -> list:  # list of lists
        """
        the function return a list lists that each list is a connected component in thr graph
        """
        nodes_that_left = []  # the keys of the nodes that doesn't belong to another connected_component
        connected_components = []  # list of all the connected_components in this graph
        for node in self.graph.nodes:
            nodes_that_left.append(node)
        while nodes_that_left:
            n = nodes_that_left[0]
            n_connected_component = self.connected_component(n)  # the connected_component of n
            connected_components.append(n_connected_component)
            for key in n_connected_component:
                nodes_that_left.remove(key)
        return connected_components

    def graph_range(self) -> Range2D:
        """
        the function return the x,y ranges of self.graph which represented as Range2D obj
        the function return None if there are no nodes in the graph
        """
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
        """
        function for plot the graph. this function return None
        """
        def world_to_world(world1: tuple, world2: tuple, point: tuple) -> tuple:
            # 1: (x1,y1, x2,y2)
            dx1 = world1[2] - world1[0]
            dy1 = world1[3]-world1[1]
            ratiox = (point[0]-world1[0])/dx1
            ratioy = (point[1]-world1[1])/dy1
            dx2 = world2[2] - world2[0]
            dy2 = world2[3]-world2[1]
            return ratiox*dx2, ratioy*dy2
        x_vals = []
        y_vals = []
        xr = Range(0, 10)
        yr = Range(0, 10)
        dim = Range2D(xr, yr)
        r2r = Range2Range(self.graph_range(), dim)
        r = self.graph_range()
        world = (r.x_range.min, r.y_range.min, r.x_range.max, r.y_range.max)
        for node in self.graph.nodes.values():
            x, y = world_to_world(world, (0, 0, 10, 10), (node.getLocation()[0], node.getLocation()[1]))
            x_vals.append(x)
            y_vals.append(y)
            for out_edge_key in node.out_edges:
                x_neighbor, y_neighbor = r2r.world_to_frame(self.graph.nodes[out_edge_key].getLocation()[0],
                                                            self.graph.nodes[out_edge_key].getLocation()[1])
                delta_x = x_neighbor - x
                delta_y = y_neighbor - y
                plt.arrow(x, y, delta_x, delta_y, head_length=1, length_includes_head=True, width=0.009, head_width=0.09)
        plt.scatter(x_vals, y_vals)
        plt.show()
