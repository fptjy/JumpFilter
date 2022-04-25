import cuckoofilter_AJCF
import math
import jump
import hashutils_DJBhash_JCF


class Adaptive_Jump_CF(object):
    """
    Jump Cuckoo Filter class.

    Implements dynamic filter with elastic capacity.
    """

    # def __init__(self, capacity, fpr, exp_block_number, initial_block_number):
    #     """
    #     Initialize CuckooFilter object.
    #
    #     :param capacity: Size of the Jump Cuckoo Filter
    #     :param single_table_length: Number of buckets in a block
    #     :param single_capacity: capacity of a single block
    #     :param finger_size: size of fingerprint
    #     considered full
    #     """
    #     self.capacity = capacity
    #     self.single_table_length = int(capacity / 4 / exp_block_number)
    #     self.single_capacity = self.single_table_length * 0.9375 * 4
    #     self.finger_size = math.ceil(math.log(8.0 / (1 - (1.0 - fpr) ** (self.single_capacity / capacity)), 2))
    #     self.JCF = [cuckoofilter_JCF.CuckooFilter(capacity=self.single_table_length, fingerprint_size=self.finger_size)
    #                 for _ in range(initial_block_number)]
    #     self.Size = 0

    def __init__(self, capacity, fpr, block_length, initial_block_number):
        """
        Initialize CuckooFilter object.

        :param capacity: Size of the Jump Cuckoo Filter
        :param fpr: the false positive rate threshold
        :param block_length: bucket number of a single block
        :param initial_block_number: initial block number
        considered full
        """
        self.capacity = capacity
        self.block_length = block_length
        self.single_capacity = self.block_length * 0.9375 * 4
        self.finger_size = math.ceil(math.log(8.0 / (1 - (1.0 - fpr) ** (self.single_capacity / capacity)), 2))
        self.AJCF = [cuckoofilter_AJCF.CuckooFilter(capacity=self.block_length, fingerprint_size=self.finger_size)
                    for _ in range(initial_block_number)]
        self.Size = 0

    def Insert(self, item, Bnum):
        fingerprint = hashutils_DJBhash_JCF.fingerprint(item, self.finger_size)
        Block = jump.hash(fingerprint, len(self.AJCF))
        result = self.AJCF[Block].insert(item)
        while result != "yes":
            self.extend(Bnum)
            Block = jump.hash(result[1], len(self.AJCF))
            result = self.AJCF[Block].insert_eviction(result[0], result[1])
        self.Size += 1
        return True

    def Query(self, item):
        fingerprint = hashutils_DJBhash_JCF.fingerprint(item, self.finger_size)
        Block = jump.hash(fingerprint, len(self.AJCF))
        return self.AJCF[Block].query(item)

    def Delete(self, item):
        fingerprint = hashutils_DJBhash_JCF.fingerprint(item, self.finger_size)
        Block = jump.hash(fingerprint, len(self.AJCF))
        if self.AJCF[Block].delete(item):
            self.Size -= 1

            return True
        return False

    def extend(self, Bnum):
        self.AJCF += [cuckoofilter_AJCF.CuckooFilter(capacity=self.block_length,
                                                    fingerprint_size=self.finger_size) for _ in range(Bnum)]
        # self.JCF[len(self.JCF)] = cuckoofilter.CuckooFilter(capacity=self.single_table_length,
        #                                                     fingerprint_size=self.finger_size)
        for x in range(len(self.AJCF) - Bnum):
            for y in range(self.AJCF[x].capacity):
                for fingerprint in self.AJCF[x].buckets[y].bucket:
                    Block = jump.hash(fingerprint, len(self.AJCF))
                    if Block != x:
                        self.AJCF[x].buckets[y].delete(fingerprint)
                        self.AJCF[x].size -= 1
                        self.AJCF[Block].insert_eviction(y, fingerprint)
        return True

    def compact(self, t):
        if not self.can_compact(threshold=t):
            return False
        else:
            count = 0
            for i in range(self.AJCF[len(self.AJCF) - 1].capacity):
                for fingerprint in self.AJCF[len(self.AJCF) - 1].buckets[i].bucket:
                    Block = jump.hash(fingerprint, len(self.AJCF) - 1)
                    result = self.AJCF[Block].insert_eviction(i, fingerprint)

                    if result == "yes":
                        count += 1
                    else:
                        c = 0
                        for d_i in range(self.AJCF[len(self.AJCF) - 1].capacity):
                            for d_fingerprint in self.AJCF[len(self.AJCF) - 1].buckets[i].bucket:
                                d_Block = jump.hash(d_fingerprint, len(self.AJCF) - 1)
                                self.AJCF[d_Block].delete_eviction(d_i, d_fingerprint)
                                c += 1
                                if c >= count:
                                    self.AJCF[Block].insert_eviction(result[0], result[1])
                                    return False

            del self.AJCF[len(self.AJCF) - 1]
            return True

    def can_compact(self, threshold):
        if len(self.AJCF) > 1:
            if self.Size / ((len(self.AJCF) - 1) * self.block_length * self.AJCF[0].bucket_size) < threshold:
                return True
        return False
