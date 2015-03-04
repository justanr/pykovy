from collections import Counter, UserDict, defaultdict
from itertools import chain
from operator import itemgetter
from random import random, choice

from .errors import MarkovError, DisjointChainError, MarkovStateError
from .utils import window, weighted_choice, unzip

__all__ = ("ProbablityMap", "MarkovChain", "MarkovChainIterator")

class ProbablityMap(Counter):
    """Simple wrapper around :class:`~collections.Counter` that adds a method
    to make weighted, random choices from the map.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def random(self, randomizer=random):
        """Returns a closure frozen to the current state of the map.
        The closure will allow choosing weighted random, possible states 
        from the map.

        Allows passing a randomizer if random.random is insufficient or for
        testing purposes. randomizer should return a float 0 < n < 1.
        """

        values, chances = unzip(sorted(self.items(), key=itemgetter(1)))
        chooser = weighted_choice(chances)
        
        def random_item():
            choice = chooser(randomizer())
            return values[choice]

        return random_item

class MarkovChain(UserDict):
    """A collection of states and possible states.

    States are keys stored as n-length tuples and possible states are values
    stored as ProbablityMap instances.
    """
    
    def __init__(self, order, states=None):
        super().__init__()
        self.__order = order
        if states is not None:
            self.update(states)

    
    def __repr__(self):
        return "{}(order={})".format(self.__class__.__name__, self.order)

    @property
    def order(self):
        return self.__order

    @order.setter
    def order(self):
        raise TypeError("{}.order is read only".format(self.__class__name__))

    def __iter__(self):
        return MarkovChainIterator(self.data)

    def __setitem__(self, key, value):
        if not isinstance(key, tuple) or len(key) != self.order:
            raise TypeError("key must be tuple of length {}".format(self.order))

        if not isinstance(value, ProbablityMap):
            raise TypeError("value must be a ProbablityMap or subclass.")

        return super().__setitem__(key, value)
    
    def __delitem__(self, key):
        raise MarkovError(
            "Cannot delete from probablity chain without "
            "becoming disjoint. If you meant this, use "
            "MarkovChain.data.__delitem__"
            )

    @classmethod
    def from_corpus(cls, corpus, order, begin_with=None):
        staging = defaultdict(ProbablityMap)

        if begin_with is not None:
            corpus = chain(begin_with, corpus)

        for w in window(corpus, size=order+1):
            staging[w[:-1]].update([w[-1]])

        return cls(states=staging, order=order)

class MarkovChainIterator(object):
    """Iteration handler for MarkovChains.
    
    Maintains a copy of the original chain's keys and their value's weighted
    random choices' closures to prevent interference when modifying the 
    target chain during iteration.

    It should be noted that this is a non-deterministic, possibly cyclical
    iterator.
    """

    def __init__(self, chain, begin_with=None):
        self.__chain = {state:chain[state].random() for state in chain}
        self.__in_progress = False
        self.__state = self.__possible = None
        self.__invalid = False

        if begin_with:
            try:
                self.state = begin_with
            except MarkovStateError:
                self.__random_state()
        else:
            self.__random_state()

    def __random_state(self):
        self.state = choice(list(self.__chain.keys()))

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, state):
        if state not in self.__chain:
            raise MarkovStateError("Invalid state provided: {}".format(state))

        self.__state = state
        self.__possible = self.__chain[state]

    def __begin_with(self, state):
        if not self.__in_progress:
            self.state = state
        else:
            raise MarkovError("MarkovChainIterator in progress already")

    begin_with = property(fset=__begin_with)

    def __iter__(self):
        return self

    def __next__(self):
        self.__in_progress = True
        value = self.__possible()

        if self.__invalid:
            raise DisjointChainError(self.__invalid)

        try:
            self.state = self.__state[1:] + tuple([value])
        except MarkovStateError as e:
            self.__invalid = e
        
        return value
