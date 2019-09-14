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
            self.trucks.append(Truck(pos))

    def init_rating(self):
        pass

    def activate_bin(self, pos):
        # TODO: better datastructure
        self.active_bin.append(pos)

    def deactivate_bin(self, pos):
        self.active_bin.remove(pos)


class Truck:
    def __init__(self, pos, strategy="greedy"):
        self.pos = pos
        self.strategy = strategy
        self.path = 0
        self.bins_counter = 0

    def next(self, status):
        # TODO A* or anything
        if self.strategy == "greedy":
            min_cost = -1
            min_pos = -1
            for active in status.get_active():
                dist = status.get_dist(self.pos, active)
                if min_cost == -1 or min_cost > dist:
                    min_cost = dist
                    min_pos = active
            # Deactivate bin and change pos
            status.deactivate_bin(min_pos)
            self.pos = min_pos
            self.bins_counter += 1
            self.path += min_cost
        else:
            raise Exception("")


class BinActivator:
    def __init__(self, activate=100, strategy="random"):
        self.max_activate = activate
        self.strategy = strategy

    def activate(self, Status):
        return [rnd.randint(0, Status.num_position) for _ in range(rnd.randint(0, self.max_activate))]
