import random
import numpy as np


class Spielfeld:
    def __init__(self, laenge, hoehe):
        self.laenge = laenge
        self.hoehe = hoehe
        self.spielfeld = np.full((laenge, hoehe), "*", dtype=object)

    def __str__(self):
        return str(self.spielfeld)


if __name__ == "__main__":
    s = Spielfeld(3, 4)
    print(s)