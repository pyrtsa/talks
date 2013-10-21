#!/usr/bin/env python3
# encoding: utf-8

# Public domain.
# 2013, Pyry Jahkola.

import builtins
import itertools as it
import operator
import inspect
from functools import reduce, wraps
from collections import deque

# https://gist.github.com/pyrtsa/7083770
from progress import progress, progresslines

# ------------------------------------------------------------------------------

def reductions(f, xs, *init):
    "Generate all steps of reduction."
    it = iter(xs)
    ac = init[0] if init else next(it)
    yield ac
    for x in it:
        ac = f(ac, x)
        yield ac

nan = float('nan')

def mean(xs):
    s, n = 0, 0
    for x in (x for x in xs if x==x):
        s += x
        n += 1
    return s / n if n else nan

# ------------------------------------------------------------------------------

def do(xs):
    for _ in xs: pass

def first(xs):
    for x in xs: return x

def last(xs):
    try:
        return xs[-1]
    except TypeError:
        return deque(xs, 1)[0]

# ------------------------------------------------------------------------------

def group_by(key, xs, op=list):
    """Group xs by key into a dict
    with op(values) as values."""
    gs = {}
    for x in xs:
        gs.setdefault(key(x),
                      []).append(x)
    return {k: op(gs[k]) for k in gs}

# ------------------------------------------------------------------------------

class Into(object):
    def __init__(self, cls): self.cls = cls
    def __or__(self, x): return self.cls(x)
    def __ror__(self, x): return self.cls(x)

L = Into(list)
T = Into(tuple)

def merge(*ds):
    if not ds: return {}
    return reduce(lambda a, b: a.update(b) or a, ds[1:], ds[0].copy())

# ------------------------------------------------------------------------------

def curry(f, n=None):
    "Enable currying on function f up to until n positional arguments."
    if n is None:
        s = inspect.getfullargspec(f)
        n = len(s.args) - len(s.defaults or [])
    if not n: return f # nothing to curry
    def call(f, *a1, **k1):
        if len(a1) >= n: return f(*a1, **k1)
        return lambda *a2, **k2: call(f, *(a1 + a2), **merge(k1, k2))
    return wraps(f)(call(f))

@curry
def at(n, xs, **kwargs):
    try: return xs[n]
    except (IndexError, KeyError) as e:
        if 'default' in kwargs: return kwargs['default']
        raise e

def juxt(*fs):
    "Compose a new function returning as tuple the results of original ones"
    return lambda *a, **k: tuple(f(*a, **k) for f in fs)

map = curry(builtins.map, 2)
filter = curry(builtins.filter, 2)

@curry
def sort_by(key, xs, **kwargs): return sorted(xs, key=key, **kwargs)

@curry
def zipsort(xs, *more, **kwargs):
    return zip(*sorted(zip(xs, *more), **kwargs))

# ------------------------------------------------------------------------------

if __name__ == '__main__':
    names = "Donald Daisy Pluto Huey Luey Dewey Scrooge".split()
    places = [x.strip().split(';') for x in progresslines('places.csv')]
    initials = lambda s: [s[0] for s in s.split()]
    