import cuckoofilter_for_DCF
import math
import hashutils_DJBhash_DCF


class Dynamic_CF(object):
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
    #     self.DCF = [cuckoofilter_for_DCF.CuckooFilter_DCF(capacity=self.single_table_length, fingerprint_size=self.finger_size)
    #                 for _ in range(initial_block_number)]
    #     self.Size = 0

    def __init__(self, capacity, fpr, block_length, initial_block_number):
        """
        Initialize CuckooFilter object.

        :param capacity: Size of the Dynamic Cuckoo Filter
        :param fpr: the false positive rate threshold
        :param block_length: bucket number of a single block
        :param initial_block_number: initial block number
        considered full
        """
        self.capacity = capacity
        self.block_length = block_length
        self.single_capacity = self.block_length * 0.9375 * 4
        self.finger_size = math.ceil(math.log(8.0 / (1 - (1.0 - fpr) ** (self.single_capacity / capacity)), 2))
        self.DCF = [cuckoofilter_for_DCF.CuckooFilter_DCF(capacity=self.block_length, fingerprint_size=self.finger_size)
                    for _ in range(initial_block_number)]
        self.Size = 0

    def Insert(self, item):
        cur = len(self.DCF) - 1
        result = self.DCF[cur].insert(item)
        if result != "yes":
            cur += 1
            if cur >= len(self.DCF):
                self.DCF += [
                    cuckoofilter_for_DCF.CuckooFilter_DCF(capacity=self.block_length, fingerprint_size=self.finger_size)]
                self.DCF[cur].insert_eviction(result[0], result[1])
        self.Size += 1
        return True

    def Query(self, item):
        for i in range(len(self.DCF)):
            if self.DCF[i].query(item):
                return True
        return False

    def Delete(self, item):
        for i in range(len(self.DCF)):
            if self.DCF[i].delete(item):
                self.Size -= 1
                return True
        return False

    def can_compact(self):
        sort_list = [[i, self.DCF[i].size] for i in range(len(self.DCF))]
        result = sorted(sort_list, key=(lambda x: x[1]))
        sort = [result[i][0] for i in range(len(self.DCF))]

        for bucket_location in range(self.DCF[sort[0]].capacity):
            if len(self.DCF[sort[0]].buckets[bucket_location].bucket) > 0:
                empty_slot_number = 0

                for num in range(len(self.DCF) - 1):
                    empty_slot_number += self.DCF[0].bucket_size - len(
                        self.DCF[sort[num + 1]].buckets[bucket_location].bucket)
                if empty_slot_number < len(self.DCF[sort[0]].buckets[bucket_location].bucket):
                    return False
        return True

    def compact(self, threshold):
        if len(self.DCF) <= 1:
            return False
        else:
            space_occupancy = self.Size / ((len(self.DCF) - 1) * self.DCF[0].capacity * self.DCF[0].bucket_size)
            if space_occupancy > threshold:
                return False
            else:

                sort_list = [[i, self.DCF[i].size] for i in range(len(self.DCF))]
                result = sorted(sort_list, key=(lambda x: x[1]))
                sort = [result[i][0] for i in range(len(self.DCF))]

                if not self.can_compact():
                    # print("the filter is too full to compact, consider removing more elements")
                    return False

                if self.DCF[sort[0]].size == 0:
                    del self.DCF[sort[0]]
                    return True

                if self.DCF[sort[0]].size > 0 and self.can_compact():
                    for i in range(self.DCF[sort[0]].capacity):
                        if len(self.DCF[sort[0]].buckets[i].bucket) > 0:
                            for l in range(len(self.DCF[sort[0]].buckets[i].bucket)):
                                evict_item = self.DCF[sort[0]].buckets[i].bucket[l]
                                num = 1
                                while num < len(sort):
                                    if self.DCF[sort[len(sort) - num]].buckets[i].insert(evict_item):
                                        self.DCF[sort[len(sort) - num]].size += 1
                                        break
                                    num += 1

                    del self.DCF[sort[0]]
                    return True
