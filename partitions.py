#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 12 19:15:42 2016

get_partitions_ruskey() is a drop-in replacement of
get_partitions() in ps1_partition.py. It generates the
partitions in increasing order of the number of subsets.
It implements Frank Ruskey's algorithm, described in
Knuth's The Art of Computer Programming, Vol. 4A,
Section 7.2.1.5, Exercise 17.
Author: Wan-Teh Chang
Date: 2016-11-06
"""
from typing import *


def partitions_ruskey(L:Iterable, m: int)->Iterator:
    def visit(a):
        partition = [[] for i in range(m)]
        i = 0
        while i < len(L):
            partition[a[i + 1]].append(L[i])
            i += 1
        return partition

    def f(mu, nu, sigma, a):
        if mu == 2:
            yield visit(a)
        else:
            yield from f(mu - 1, nu - 1, (mu + sigma) % 2, a)
        if nu == mu + 1:
            assert a[mu] == 0
            a[mu] = mu - 1
            yield visit(a)
            while a[nu] != 0:
                a[nu] -= 1
                yield visit(a)
        elif nu > mu + 1:
            index = nu - 1 if (mu + sigma) % 2 != 0 else mu
            assert a[index] == 0
            a[index] = mu - 1
            if (a[nu] + sigma) % 2 != 0:
                yield from b(mu, nu - 1, 0, a)
            else:
                yield from f(mu, nu - 1, 0, a)
            while a[nu] > 0:
                a[nu] -= 1
                if (a[nu] + sigma) % 2 != 0:
                    yield from b(mu, nu - 1, 0, a)
                else:
                    yield from f(mu, nu - 1, 0, a)

    def b(mu, nu, sigma, a):
        if nu == mu + 1:
            while a[nu] != mu - 1:
                yield visit(a)
                a[nu] += 1
            yield visit(a)
            assert a[mu] == mu - 1
            a[mu] = 0
        elif nu > mu + 1:
            if (a[nu] + sigma) % 2 != 0:
                yield from f(mu, nu - 1, 0, a)
            else:
                yield from b(mu, nu - 1, 0, a)
            while a[nu] < mu - 1:
                a[nu] += 1
                if (a[nu] + sigma) % 2 != 0:
                    yield from f(mu, nu - 1, 0, a)
                else:
                    yield from b(mu, nu - 1, 0, a)
            index = nu - 1 if (mu + sigma) % 2 != 0 else mu
            assert a[index] == mu - 1
            a[index] = 0
        if mu == 2:
            yield visit(a)
        else:
            yield from b(mu - 1, nu - 1, (mu + sigma) % 2, a)

    n = len(L)
    assert 1 < m < n
    a = [0] * (n + 1)
    j = 1
    while j <= m:
        a[n - m + j] = j - 1
        j += 1
    yield from f(m, n, 0, a)


def get_partitions_ruskey(L):
    yield [L[:]]
    for m in range(2, len(L)):
        yield from partitions_ruskey(L, m)
    if len(L) > 1:
        yield [[e] for e in L]


# +
#for partitions in get_partitions_ruskey(['a','b','c','e']):
#    print(partitions, len(partitions))
# -


