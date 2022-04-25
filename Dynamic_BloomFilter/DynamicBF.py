import bloomfilter
import math


class Dynamic_BF(object):
    """
    Dynamic Bloom Filter class.

    Implements dynamic filter with elastic capacity.
    """

    def __init__(self, n, m, k, fp_threshold):
        """
        Initialize Dynamic Bloom Filter object.

        :param n: the size of data
        :param m: the size of a single BF block
        :param k: the number of hash functions
        :param fp_threshold: the threshold of false positive rate
        considered full
        """
        self.n = n
        self.m = m
        self.k = k
        self.fp_threshold = fp_threshold
        self.DBF = [bloomfilter.BloomFilter(m=m, k=k)]
        self.Size = 0

    # def Insert(self, item):
    #     BF_number = -1
    #     for i in range(len(self.DBF)):
    #         fp = 1 - (1 - (1 - math.e ** (-self.k * self.DBF[i].size / self.m)) ** self.k) ** int(
    #             self.n / (self.DBF[i].size + 1))
    #         if fp < self.fp_threshold:
    #             BF_number = i
    #     if BF_number != -1:
    #         self.DBF[BF_number].insert(item)
    #         self.Size += 1
    #         return True
    #     else:
    #         self.DBF += [bloomfilter.BloomFilter(m=self.m, k=self.k)]
    #         self.DBF[len(self.DBF) - 1].insert(item)
    #         self.Size += 1
    #         return True

    def Insert(self, item):
        fp = 1 - (1 - (1 - math.e ** (-self.k * self.DBF[len(self.DBF) - 1].size / self.m)) ** self.k) ** int(
            self.n / (self.DBF[len(self.DBF) - 1].size + 1))

        if fp < self.fp_threshold:
            self.DBF[len(self.DBF)-1].insert(item)
            self.Size += 1
            return True
        else:
            self.DBF += [bloomfilter.BloomFilter(m=self.m, k=self.k)]
            self.DBF[len(self.DBF) - 1].insert(item)
            self.Size += 1
            return True

    def Query(self, item):
        for i in range(len(self.DBF)):
            if self.DBF[i].query(item):
                return True
        return False

    def Delete(self, item):
        for i in range(len(self.DBF)):
            if self.DBF[i].delete(item):
                self.Size -= 1
                return True
        return False

    def compact(self):
        if len(self.DBF) <= 1:
            return False
        else:
            for i in range(len(self.DBF)):
                if self.DBF[i].size == 0:
                    del self.DBF[i]
                if len(self.DBF) <= 1:
                    return False

            BF1 = 0
            BF2 = 0
            size_list = []
            for BF in self.DBF:
                size_list.append(BF.size)
            size_list.sort()
            for i in range(len(self.DBF)):
                if self.DBF[i].size == size_list[0]:
                    BF1 = i
            for i in range(len(self.DBF)):
                if self.DBF[i].size == size_list[1] and i != BF1:
                    BF2 = i

            fp = 1 - (1 - (
                    1 - math.e ** (-self.k * (self.DBF[BF1].size + self.DBF[BF2].size) / self.m)) ** self.k) ** int(
                self.n / ((self.DBF[BF1].size + self.DBF[BF2].size) + 1))

            if fp > self.fp_threshold:
                return False
            else:
                for j in range(self.DBF[BF1].m):
                    self.DBF[BF2].vector[j] += self.DBF[BF1].vector[j]
                self.DBF[BF2].size += self.DBF[BF1].size
                del self.DBF[BF1]
                return True
