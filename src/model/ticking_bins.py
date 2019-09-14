import time
import random as rnd
import sqlite3

class BinDistributin:
    def __init__(self, mean=0.005):
        self.tick = 0
        self.mean = mean
        self.before = 0
    def make_tick(self):
        if rnd.uniform(0, 1) + self.before < self.mean:
            self.before = 4
            return True
        else:
            if self.before > 0:
                self.before -= 1
            return False


if __name__ == "__main__":
    bins = BinDistributin()
    while True:
        for i in range(4000):
            conn = sqlite3.connect('active_containers.db')
            c = conn.cursor()
            c.execute(f"INSERT OR IGNORE INTO active_bins VALUES (?)", (i,))
            conn.commit()
            c.close()
        time.sleep(30)