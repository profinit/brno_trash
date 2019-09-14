import random as rnd


class State:
    def __init__(self, matrix, num_trucks):
        assert matrix.ndim == 2
        assert matrix.shape[0] == matrix.shape[1]
        self.matrix = matrix
        self.num_position = matrix.shape[0]
        self.init_ratings()
        self.trucks = []
        self.init_trucks(num_trucks)
        self.active_bin = []

    def next(self):
        for truck in self.trucks:
            truck.next(self)

    def get_dist(self, a, b):
        return self.matrix[a][b]

    def get_h(self, a):
        # TODO: Implement some heuristic
        return 0

    def get_active(self):
        return self.active_bin

    def init_trucks(self, num_trucks):
        # TODO: Implement some clever init
        for i in range(num_trucks):
            pos = rnd.randint(0, self.num_position)
            self.trucks.append(Truck(pos, id))

    def init_ratings(self):
        pass

    def activate_bin(self, pos):
        # TODO: better datastructure
        self.active_bin.append(pos)

    def deactivate_bin(self, pos):
        self.active_bin.remove(pos)

    def get_truck_positions(self):
        return [truck.pos for truck in self.trucks]

    def get_truck_id(self):
        return [truck.id for truck in self.trucks]


class Truck:
    def __init__(self, pos, id, strategy="greedy"):
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
            assert len(status.get_active()) != 0
            for active in status.get_active():
                dist = status.get_dist(self.pos, active)
                if min_cost == -1 or min_cost > dist:
                    min_cost = dist
                    min_pos = active
            # Deactivate bin and change pos
            status.deactivate_bin(min_pos)
            self.pos = min_pos
            self.path.append(self.pos)
            self.bins_counter += 1
            self.path_dist += min_cost
        else:
            raise Exception("")


class BinActivator:
    def __init__(self, activate=100, strategy="random"):
        self.max_activate = activate
        self.strategy = strategy

    def activate(self, status):
        for i in  [rnd.randint(0, status.num_position) for _ in range(rnd.randint(0, self.max_activate))]:
            status.activate_bin(i)

if __name__ ==  "__main__":
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
            