from AdaptiveJumpCF import Jump_CF
import random
from cuckoofilter_AJCF import CuckooFilter
import time

"""
#Read insertion data and data preprocess
"""
raw_data1 = []
with open('C:/Users/fptjy/ArkFilter_experiment/experiment/IP_final_min_int_sort.csv', 'r') as fin:
    for line in fin:
        raw_data1.append(line.replace("\n", ""))
fin.close()

# raw_data1 = []
# delta = 100000
# for i in range(len(raw_data0) - delta):
#     raw_data1.append(raw_data0[i])

insert_result = [[]]
tem = 0
for i in range(len(raw_data1)):

    x = int(raw_data1[i].split(",")[1])
    y = raw_data1[i].split(",")[0]
    if x == tem:
        insert_result[x].append(y)
    elif x == tem + 1:
        insert_result.append([])
        insert_result[x].append(y)
        tem += 1
    else:
        distance = x - tem
        for j in range(distance - 1):
            insert_result.append(["non"])
            tem += 1
        insert_result.append([])
        insert_result[x].append(y)
        tem += 1

print(len(insert_result))  # 81230

"""
#Read deletion data and data preprocess
"""
raw_data2 = []
with open('C:/Users/fptjy/ArkFilter_experiment/experiment/IP_final_max_int_sort.csv', 'r') as fin:
    for line in fin:
        raw_data2.append(line.replace("\n", ""))
fin.close()

delete_result = [[]]
tem = 0
for i in range(len(raw_data2)):

    x = int(raw_data2[i].split(",")[1])
    y = raw_data2[i].split(",")[0]
    if x == tem:
        delete_result[x].append(y)
    elif x == tem + 1:
        delete_result.append([])
        delete_result[x].append(y)
        tem += 1
    else:
        distance = x - tem
        for j in range(distance - 1):
            delete_result.append(["non"])
            tem += 1
        delete_result.append([])
        delete_result[x].append(y)
        tem += 1

##过滤掉到达但未离开的元素
CF_filtrate = CuckooFilter(capacity=2 ** 21, bucket_size=4, fingerprint_size=20)
# CF_mur_filter = CuckooFilter_mur(capacity=2 ** 21, bucket_size=4, fingerprint_size=18)
for i in range(len(delete_result)):
    if delete_result[i] == "non":
        print("non appear in delete")
    else:
        for j in range(len(delete_result[i])):
            CF_filtrate.insert(delete_result[i][j])
            # CF_mur_filter.insert(delete_result[i][j])

count = 0
for i in range(len(insert_result)):
    if insert_result[i] == "non":
        print("non appear in insert")
    else:
        for j in range(len(insert_result[i])):
            # if not CF_filtrate.contains(insert_result[i][j]) or not CF_mur_filter.contains(insert_result[i][j]):
            if not CF_filtrate.query(insert_result[i][j]):
                count += 1
                insert_result[i][j] = "extra_element"
print(count)

count2 = 0
for i in range(len(insert_result)):
    while "extra_element" in insert_result[i]:
        insert_result[i].remove("extra_element")
        count2 += 1
print(count2)

##开始测试

JpCF = Jump_CF(capacity=2 ** 15, fpr=0.00048, exp_block_number=8, initial_block_number=1)

JpCF_test_result = []

start = time.time()
for i in range(len(insert_result)):
    if insert_result[i] == "non" or len(insert_result[i]) == 0:
        print("non appear in insert_result", i)

        for key in delete_result[i]:
            JpCF.Delete(key)

        JpCF.compact(0.8)

        x2 = len(JpCF.JCF) * JpCF.single_table_length * 4
        JpCF_test_result.append(x2)

    else:
        for key in insert_result[i]:
            # print("时间序列：", i)
            JpCF.Insert(key)

        for key in delete_result[i]:
            JpCF.Delete(key)

        JpCF.compact(0.8)

        x2 = len(JpCF.JCF) * JpCF.single_table_length * 4
        JpCF_test_result.append(x2)

        # print("FILTER尺寸     :", x2)

for i in range(len(delete_result) - len(insert_result)):
    for key in delete_result[i]:
        JpCF.Delete(key)

    JpCF.compact(0.8)

    x2 = len(JpCF.JCF) * JpCF.single_table_length * 4
    JpCF_test_result.append(x2)

end = time.time()

print(" ")
y2 = len(JpCF.JCF) * JpCF.single_table_length * 4
print(y2)
for i in range(len(JpCF.JCF)):
    print(JpCF.JCF[i])

print("JpCF.Size", JpCF.Size)
print("时间开销：", end - start)

import csv

##DCF_4_test_result
# 1. 创建文件对象
f = open('JpCF_test_result_0.8.csv', 'w', encoding='utf-8', newline="")
# 2. 基于文件对象构建 csv写入对象
csv_writer = csv.writer(f)
# 4. 写入csv文件内容
for i in range(len(JpCF_test_result)):
    csv_writer.writerow([str(JpCF_test_result[i])])
# 5. 关闭文件
f.close()
