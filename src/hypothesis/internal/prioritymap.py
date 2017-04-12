class PriorityMap(object):
    __slots__ = ('__keys_to_indices', '__heap')

    def __init__(self):
        self.__keys_to_indices = {}
        self.__heap = []

    def __len__(self):
        assert len(self.__heap) == len(self.__keys_to_indices)
        return len(self.__keys_to_indices)

    def __getitem__(self, key):
        i = self.__keys_to_indices[key]
        k, v = self.__heap[i]
        assert k == key
        return v

    def __setitem__(self, key, value):
        try:
            i = self.__keys_to_indices[key]
            k, v = self.__heap[i]
            assert k == key
            self.__heap[i] = (k, value)
        except KeyError:
            i = len(self.__heap)
            self.__heap.append((key, value))
            self.__keys_to_indices[key] = i
        self.__adjust_index(i)

    def keys(self):
        return self.__keys_to_indices.keys()

    def peek(self):
        if not self.__heap:
            raise IndexError("Cannot peek into empty heap")
        return self.__heap[0]

    def pop(self):
        if not self.__heap:
            raise IndexError("Cannot pop from empty heap")
        self.__swap(0, len(self.__heap) - 1)
        result = self.__heap.pop()
        del self.__keys_to_indices[result[0]]
        if self.__heap:
            self.__adjust_index(0)
        return result

    def __adjust_index(self, i):
        while i > 0:
            j = (i - 1) // 2
            if self.__in_order(j, i):
                break
            else:
                self.__swap(i, j)
                i = j

        while True:
            children = [
                j
                for j in (i * 2 + 1, i * 2 + 2)
                if j < len(self.__heap)
            ]
            if not children:
                break
            if len(children) == 2 and not self.__in_order(*children):
                children.reverse()
            for j in children:
                if not self.__in_order(i, j):
                    self.__swap(i, j)
                    i = j
                    break
            else:
                break

    def __in_order(self, i, j):
        return self.__heap[i][1] <= self.__heap[j][1]

    def __swap(self, i, j):
        if i == j:
            return
        self.__heap[i], self.__heap[j] = self.__heap[j], self.__heap[i]
        for t in (i, j):
            self.__keys_to_indices[self.__heap[t][0]] = t
