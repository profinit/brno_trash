import random as rnd
import pandas as pd
import numpy as np
import requests
import sqlite3

MIN_BIN_LIMIT = 500
MAX_BIN_LIMIT = 2000

class State:
    def __init__(self, matrix, num_trucks, tick_length=60):
        assert matrix.ndim == 2
        assert matrix.shape[0] == matrix.shape[1]
        self.matrix = matrix
        self.closest = np.argsort(matrix, axis=1)
        self.num_position = matrix.shape[0]
        self.init_ratings()
        self.trucks = []
        self.no_truck_add_period = 0

        self.init_trucks(num_trucks)
        self.tick_length = tick_length

    def next(self):
        self.update_trucks()

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

    def get_active_bins_positions(self):
        active_bins = self.get_active_bins()
        df = pd.read_csv("stanoviste.csv")
        return df.iloc[active_bins]

    def id_to_pos(self, id):
        df = pd.read_csv("stanoviste.csv")
        row =  df.iloc[id]
        return (row['lat'], row['long'])

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

    def update_trucks(self):
        self.no_truck_add_period -= 1
        if self.no_truck_add_period > 0:
            return

        active_bins = self.get_active_bins()
        if len(active_bins) < MIN_BIN_LIMIT:
            self.trucks = self.trucks[:-1]
            self.no_truck_add_period = 10

        if len(active_bins) > MAX_BIN_LIMIT:
            pos = rnd.randint(0, self.num_position)
            self.trucks.append(Truck(pos, id))
            self.no_truck_add_period = 10

    # Expects two tuples (lat,long), (lat,long)
    def get_route(self, from_pos, to_pos):
        query = f"http://172.16.20.100:5000/route/v1/driving/{from_pos[1]},{from_pos[0]};{to_pos[1]},{to_pos[0]}?geometries=geojson"
        response = requests.get(query)
        return response.json()["routes"][0]["geometry"]

class Truck:
    def __init__(self, pos, id, strategy="a_star"):
        self.pos = pos
        self.id = id
        self.strategy = strategy
        self.path_dist = 0
        self.path = [pos]
        self.bins_counter = 0
        self.eta = 0

    def next(self, status):
        if self.eta > 0:
            self.eta -= status.tick_length
            return

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
            self.eta = min_cost

        elif self.strategy == "a_star":
            depth_limit = 6
            close_limit = 10
            # Current path, current depth, nodes of path
            heap = []
            current = (0, 0, [self.pos])
            actives = status.get_active_bins()

            while current[1] < depth_limit:
                current_node = current[2][-1]
                closest_nodes = status.get_closest(current_node)
                close_index = 0
                close_visited = 0
                while close_visited < close_limit:
                    close_index += 1
                    assert close_index < status.num_position
                    node = closest_nodes[close_index]
                    if node in current[2] or node not in actives:
                        continue

                    close_visited += 1
                    dist = current[0] + status.get_dist(current_node, node)
                    # add heuristic
                    dist += status.get_h(node)
                    path = np.append(current[2], node)
                    depth = current[1] + 1
                    heap.append((dist, depth, path))

                current = heap[0]
                for c in heap:
                    if c[0] < current[0]:
                        current = c
                heap.remove(current)

            # shortest at this depth level
            self.path_dist += status.get_dist(self.pos, current[1])
            self.eta = status.get_dist(self.pos, current[1])

            self.pos = current[2][1]
            self.path = np.append(self.path, current[2][1])

            self.bins_counter += 1
            status.deactivate_bin(self.pos)

        else:
            raise Exception("")


class BinActivator:
    def __init__(self, activate=100, strategy="all"):
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
    df = pd.read_csv("distance_matrix.csv", header=None, delimiter="\t")
    df = df.iloc[:, :-1]
    state = State(df.values, 10)
    bin_activator = BinActivator()

    bin_activator.activate(state)
    for i in range(100):
        state.next()

    for truck in state.trucks:
        print(truck.path)
