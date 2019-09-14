import random as rnd

class State:
    def __init__(self, matrix, num_trucks):
        assert matrix.ndim == 2
        assert matrix.shape[0] == matrix.shape[1]
        self.matrix = matrix
        self.num_position = matrix.shape[0]
        self.init_ratings()
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

    def init_trucks(self, num_trucks):
        # TODO: Implement some clever init
        for i in range(num_trucks):
            pos = rnd.randint(0, self.num_position)
            self.trucks.append(Truck(pos))

    def init_rating(self):
        pass

    def active_bin(self, pos):
        # TODO: better datastructure
        self.active_bin.append(pos)


class    Truck:
    def __init__(self, pos, strategy="greedy"):
        self.pos = pos

    def next(self, status):
        # TODO A* or etwas
        if strategy == "greedy":
        else:
            raise Exception("")
