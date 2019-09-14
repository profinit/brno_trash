import random as rnd
import heapq
import numpy as np
import sqlite3


class State:
    def __init__(self, matrix, num_trucks):
        assert matrix.ndim == 2
        assert matrix.shape[0] == matrix.shape[1]
        self.matrix = matrix
        self.closest = np.argsort(matrix, axis=1)
        self.num_position = matrix.shape[0]
        self.init_ratings()
        self.trucks = []
        self.init_trucks(num_trucks)

    def next(self):
        for truck in self.trucks:
            truck.next(self)

    def get_dist(self, a, b):
        return self.matrix[a][b]

    def get_h(self, a):
        # TODO: Implement some heuristic
        return 0

    def get_active_bins(self):
        conn = sqlite3.connect('active_containers.db')
        c = conn.cursor()
        result = c.execute(f"SELECT * from active_bins")
        result = [x[0] for x in result]
        c.close()

        return result

    def get_closest(self, a):
        return self.closest[a]

    def init_trucks(self, num_trucks):
        # TODO: Implement some clever init
        for i in range(num_trucks):
            pos = rnd.randint(0, self.num_position)
            self.trucks.append(Truck(pos, id))

    def init_ratings(self):
        pass

    def activate_bin(self, pos):
        conn = sqlite3.connect('active_containers.db')
        c = conn.cursor()
        c.execute(f"INSERT OR IGNORE INTO active_bins VALUES (?)", (pos,))
        conn.commit()
        c.close()

    def deactivate_bin(self, pos):
        conn = sqlite3.connect('active_containers.db')
        c = conn.cursor()
        c.execute(f"DELETE FROM active_bins WHERE bin_id=?", (pos,))
        conn.commit()
        c.close()

    def get_truck_positions(self):
        return [truck.pos for truck in self.trucks]

    def get_truck_id(self):
        return [truck.id for truck in self.trucks]


class Truck:
    def __init__(self, pos, id, strategy="a_star"):
        self.pos = pos
        self.id = id
        self.strategy = strategy
        self.path_dist = 0
        self.path = [pos]
        self.bins_counter = 0

    def next(self, status):
        # TODO A* or anything
        if self.strategy == "greedy":
            min_cost = -1
            min_pos = -1
            assert len(status.get_active_bins()) != 0
            for active in status.get_active_bins():
                dist = status.get_dist(self.pos, active)
                # TODO: Not returning for debugging
                if active == self.pos or active in self.path:
                    continue
                if min_cost == -1 or min_cost > dist:
                    min_cost = dist
                    min_pos = active
            # Deactivate bin and change pos
            status.deactivate_bin(min_pos)
            self.pos = min_pos
            self.path.append(self.pos)
            self.bins_counter += 1
            self.path_dist += min_cost
        elif self.strategy == "a_star":
            depth_limit = 10
            close_limit = 20
            # Current path, current depth, nodes of path
            heap = []
            current = (0, 0, [self.pos])
            visited = set([self.pos])
            actives = status.get_active_bins()

            while current[1] < depth_limit:
                current_node = current[2][-1]
                closest_nodes = status.get_closest(current_node)
                close_index = 0
                while close_index < close_limit:
                    node = closest_nodes[close_index]
                    visited.add(node)
                    if node in visited or node not in actives:
                        continue

                    dist = status.get_dist(current_node, node)
                    # add heuristic
                    dist += status.get_h(node)
                    path = current[2].append(node)
                    depth = current[1] + 1
                    heapq.heappush(heap, (dist, depth, path))

                current = heapq.heappop(heap)
            # shortest at this depth level
            self.pos = current[2][-1]
            self.path = current[2]
            self.bins_counter = len(current[2])
            self.path_dist = current[1]
        else:
            raise Exception("")


class BinActivator:
    def __init__(self, activate=100, strategy="random"):
        self.max_activate = activate
        self.strategy = strategy

    def activate(self, status):
        if self.strategy == "random":
            for i in [rnd.randint(0, status.num_position) for _ in range(rnd.randint(0, self.max_activate))]:
                status.activate_bin(i)
        elif self.strategy == "all":
            for i in range(status.num_position):
                status.activate_bin(i)  


if __name__ == "__main__":
    import pandas as pd

    df = pd.read_csv("distance_matrix.csv", header=None, delimiter="\t")
    df = df.iloc[:, :-1]
    state = State(df.values, 10)
    bin_activator = BinActivator()
    print(state.get_truck_positions())

    for i in range(10):
        bin_activator.activate(state)
        state.next()
        print(state.get_truck_positions())

    for truck in state.trucks:
        print(truck.path)
