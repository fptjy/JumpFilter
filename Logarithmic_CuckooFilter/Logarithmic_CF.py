import cuckoofilter_tree
import math
import jump
import hashutils_DJBhash_LDCF


class Logarithmic_DCF(object):
    """
    Logarithmic Cuckoo Filter class.

    Implements dynamic filter with elastic capacity.
    """

    # def __init__(self, capacity, fpr, exp_block_number):
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
    #     self.LDCF = [cuckoofilter_tree.CuckooFilter_Tree(level=0, number=0, capacity=self.single_table_length,
    #                                                      fingerprint_size=self.finger_size)]
    #     self.Size = 0

    def __init__(self, capacity, fpr, block_length):
        """
        Initialize CuckooFilter object.

        :param capacity: Size of the Logarithmic Dynamic Cuckoo Filter
        :param fpr: the false positive rate threshold
        :param block_length: bucket number of a single block
        considered full
        """
        self.capacity = capacity
        self.block_length = block_length
        self.single_capacity = self.block_length * 0.9375 * 4
        self.finger_size = math.ceil(math.log(8.0 / (1 - (1.0 - fpr) ** (self.single_capacity / capacity)), 2))
        self.LDCF = [cuckoofilter_tree.CuckooFilter_Tree(level=0, number=0, capacity=self.block_length,
                                                         fingerprint_size=self.finger_size)]
        self.Size = 0

    def Insert(self, item):
        fingerprint = hashutils_DJBhash_LDCF.fingerprint(item, self.finger_size)
        for bk_num in range(len(self.LDCF)):
            if (fingerprint >> (self.finger_size - self.LDCF[bk_num].level)) == self.LDCF[bk_num].number:

                result = self.LDCF[bk_num].insert(item)
                if result != "yes":
                    # print("扩          容")
                    self.LDCF += [cuckoofilter_tree.CuckooFilter_Tree(level=self.LDCF[bk_num].level + 1,
                                                                      number=self.LDCF[bk_num].number * 2,
                                                                      capacity=self.block_length,
                                                                      fingerprint_size=self.finger_size)]
                    self.LDCF += [cuckoofilter_tree.CuckooFilter_Tree(level=self.LDCF[bk_num].level + 1,
                                                                      number=self.LDCF[bk_num].number * 2 + 1,
                                                                      capacity=self.block_length,
                                                                      fingerprint_size=self.finger_size)]

                    for bucket_locate in range(self.LDCF[bk_num].capacity):
                        for Finger in self.LDCF[bk_num].buckets[bucket_locate].bucket:
                            if Finger >> (self.finger_size - self.LDCF[bk_num].level - 1) == self.LDCF[
                                bk_num].number * 2:
                                self.LDCF[len(self.LDCF) - 2].insert_eviction(bucket_locate, Finger)
                            else:
                                self.LDCF[len(self.LDCF) - 1].insert_eviction(bucket_locate, Finger)

                    if result[1] >> (self.finger_size - self.LDCF[bk_num].level - 1) == self.LDCF[
                        bk_num].number * 2:
                        self.LDCF[len(self.LDCF) - 2].insert_eviction(result[0], result[1])
                    else:
                        self.LDCF[len(self.LDCF) - 1].insert_eviction(result[0], result[1])

                    del self.LDCF[bk_num]

                    self.Size += 1
                    # print("insert true")
                    return True

                else:
                    self.Size += 1
                    # print("insert true")
                    return True
        print("insert          false")
        return False

    def Query(self, item):
        fingerprint = hashutils_DJBhash_LDCF.fingerprint(item, self.finger_size)
        for bk_num in range(len(self.LDCF)):
            if fingerprint >> (self.finger_size - self.LDCF[bk_num].level) == self.LDCF[bk_num].number:
                return self.LDCF[bk_num].query(item)

        return False

    def Delete(self, item):
        fingerprint = hashutils_DJBhash_LDCF.fingerprint(item, self.finger_size)
        for bk_num in range(len(self.LDCF)):
            if fingerprint >> (self.finger_size - self.LDCF[bk_num].level) == self.LDCF[bk_num].number:
                if self.LDCF[bk_num].delete(item):
                    self.Size -= 1
                    return True

        return False

    def can_compact(self, threshold):
        B1 = -1
        B2 = -1
        for bk_num in range(len(self.LDCF)):
            if self.LDCF[bk_num].size / (self.LDCF[0].capacity * self.LDCF[bk_num].bucket_size) < threshold / 2:
                if self.LDCF[bk_num].number % 2 == 0:
                    for bk_num2 in range(len(self.LDCF)):
                        if self.LDCF[bk_num2].number == self.LDCF[bk_num].number + 1 and self.LDCF[bk_num2].level == \
                                self.LDCF[bk_num].level:
                            if self.LDCF[bk_num2].size / (
                                    self.LDCF[0].capacity * self.LDCF[bk_num].bucket_size) < threshold / 2:
                                B1 = bk_num
                                B2 = bk_num2
                                return B1, B2
                if self.LDCF[bk_num].number % 2 == 1:
                    for bk_num2 in range(len(self.LDCF)):
                        if self.LDCF[bk_num2].number == self.LDCF[bk_num].number - 1 and self.LDCF[bk_num2].level == \
                                self.LDCF[bk_num].level:
                            if self.LDCF[bk_num2].size / (
                                    self.LDCF[0].capacity * self.LDCF[bk_num].bucket_size) < threshold / 2:
                                B1 = bk_num2
                                B2 = bk_num
                                return B1, B2

        return B1, B2

    def compact_two_block(self, b1, b2):
        self.LDCF += [cuckoofilter_tree.CuckooFilter_Tree(level=self.LDCF[b1].level - 1,
                                                          number=int(self.LDCF[b1].number / 2),
                                                          capacity=self.block_length,
                                                          fingerprint_size=self.finger_size)]

        for bucket_location in range(self.LDCF[b1].capacity):
            for finger in self.LDCF[b1].buckets[bucket_location].bucket:
                compact_result = self.LDCF[len(self.LDCF) - 1].insert_eviction(bucket_location, finger)
                if compact_result != "yes":
                    del self.LDCF[len(self.LDCF) - 1]
                    return False

        for bucket_location in range(self.LDCF[b2].capacity):
            for finger in self.LDCF[b2].buckets[bucket_location].bucket:
                compact_result = self.LDCF[len(self.LDCF) - 1].insert_eviction(bucket_location, finger)
                if compact_result != "yes":
                    del self.LDCF[len(self.LDCF) - 1]
                    return False

        if b1 < b2:
            del self.LDCF[b2]
            del self.LDCF[b1]
        else:
            del self.LDCF[b1]
            del self.LDCF[b2]
        return True

    # def compact(self, threshold):
    #     result = self.can_compact(threshold)
    #     while result[0] != -1:
    #         self.compact_two_block(result[0], result[1])
    #         result = self.can_compact(threshold)
    #
    #     return True

    def compact(self, threshold):
        if len(self.LDCF) <= 1:
            return False
        else:
            result = self.can_compact(threshold)
            if result[0] != -1:
                self.compact_two_block(result[0], result[1])
                return True
            return False
