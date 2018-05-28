from collections import deque

class UniQ(object):

    def __init__(self):
        self.deque = deque()
        self.seen = set()

    def en(self, x):
        if x not in self.seen:
            self.deque.append(x)
            self.seen.add(x)

    def de(self):
        return self.deque.popleft()

    def is_empty(self):
        return len(self.deque) == 0
