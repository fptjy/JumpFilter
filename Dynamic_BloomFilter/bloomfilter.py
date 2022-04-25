"""
Bloom Filter
"""

from mmh3 import hash as m3h


class BloomFilter(object):
    """description of class"""

    def __init__(self, m, k):
        self.m = m  # the length
        self.k = k  # the number of hash functions
        self.vector = [0] * m  # the array
        self.size = 0

    def __repr__(self):  # 重写__repr__()，定义打印class的信息
        return '<BloomFilter: m=' + str(self.m) + \
               ', k=' + str(self.k) + ', size=' + \
               str(self.size) + ' >'

    def insert(self, content):
        for j in range(self.k + 1):  # set the bits as 1s for membership
            hash_ = m3h(content, j + 1) % self.m
            self.vector[hash_] += 1
        self.size += 1
        return True

    def query(self, content):
        for j in range(self.k + 1):
            hash_ = m3h(content, j + 1) % self.m
            if self.vector[hash_] == 0:
                return False  # not a member of the set
        return True

    def delete(self, content):
        for j in range(self.k + 1):
            hash_ = m3h(content, j + 1) % self.m
            if self.vector[hash_] == 0:
                return False  # not a member of the set
        for j in range(self.k + 1):
            hash_ = m3h(content, j + 1) % self.m
            self.vector[hash_] -= 1
        self.size -= 1
        return True



