import itertools as ite

w = 20
h = 10

class Foo:
    def __init__(self):
        pass
    def __iter__(self):
        return ite.product(range(w), range(h))





for i in range(30):
    print(i*10)