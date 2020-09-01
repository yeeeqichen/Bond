#!/usr/bin/python3
# encoding: utf-8
"""
@author: yeeeqichen
@contact: 1700012775@pku.edu.cn
@file: lsh.py
@time: 2020/8/27 11:59 上午
@desc: 使用随机超平面划分将向量哈希到 bucket 内
"""
import numpy as np
import math
## 获取签名
def get_signature(user_vector, rand_proj):
    res = 0
    for p in rand_proj:
        res = res << 1
        val = np.dot(p, user_vector)
        if val >= 0:
            res |= 1
    return res
## 获取输入数字中二进制值中1的个数
def nnz(num):
    if num == 0:
        return 0
    res = 1
    while num:
        res += 1
        num = num & (num - 1)
    return res
## 获取真正的cosine距离
def angular_similarity(a, b):
    dot_prod = np.dot(a, b)
    sum_a = sum(a**2) **.5
    sum_b = sum(b**2) **.5
    cosine = dot_prod/(sum_a * sum_b)
    theta = math.acos(cosine)
    return 1.0 - (theta/math.pi)
if __name__ == "__main__":
    dim = 512
    d = 2 ** 10
    nruns = 24
    avg = 0
    for run in range(nruns):
        user1 = np.random.randn(dim)
        user2 = np.random.randn(dim)
        ## 生成随机超平面
        randv = np.random.rand(d, dim)
        r1 = get_signature(user1, randv)
        r2 = get_signature(user2, randv)
        xor = r1^r2
        true_sim, hash_sim = (angular_similarity(user1, user2), (d - nnz(xor))/float(d))
        diff = abs(hash_sim - true_sim)/true_sim
        avg += diff
        print("true: %.4f, hash: %.4f, diff: %.4f" % (true_sim, hash_sim, diff))
    print("avg diff: ", avg / nruns)