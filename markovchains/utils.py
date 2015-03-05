from bisect import bisect_right
from collections import deque
from itertools import islice, accumulate

__all__ = ("window", "weighted_choice", "unzip")

def window(it, size):
    """Returns a sliding window (of width size) over data from the iterable.
    
    This is a spin on a recipe provided in the 2.3.5 itertools docs, using
    a deque rather than playing surgeon on a tuple.
    """

    it = iter(it)
    window = deque(islice(it, size), maxlen=size)
    yield tuple(window)
    for i in it:
        window.append(i)
        yield tuple(window)

def weighted_choice(weights):
    """Creates a list of running totals for weights to choose from 
    and returns a callable to handle the actual choosing process.

    This closure is a compromise between an object maintaining state and
    recreating the running total every time we need to choose an element.

    The closure allows deterministic responses for testing purposes
    instead of inherently relying on random.random(), though that's 
    likely the only actual input.
    """

    weights = list(accumulate(weights))
    def weighted_chooser(choice):
        choice *= weights[-1]
        return bisect_right(weights, choice)
    return weighted_chooser

def unzip(groups):
    """Simple wrapper around zip(*groups). Providing a name is a lot clearer
    than having the raw code around and someone wondering what it's doing.

    [(1,'a'), (2, 'b'), (3, 'c')] -> [(1,2,3), ('a', 'b', 'c')]
    """
    return zip(*groups)
