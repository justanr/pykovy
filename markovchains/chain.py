from collections import Counter, UserDict, defaultdict, Mapping
from itertools import chain
from functools import update_wrapper
from numbers import Number
from operator import itemgetter
from random import random, choice

from .errors import MarkovError, DisjointChainError, MarkovStateError
from .utils import window, weighted_choice, unzip

__all__ = (
    "ProbablityMap", "MarkovChain",
    "MarkovChainIterator"
    )

class ProbablityMap(Counter):
    """Simple wrapper for Counter to enforce types on values.

    By default, it only accepts members of numbers.Number, which includes: 
    * bool
    * int
    * float
    * complex
    * long (Python 2)
    * numbers.Real
    * numbers.Complex
    * numbers.Rational
    * numbers.Integral
    * fractions.Fraction
    * decimal.Decimal
    * possibly others

    However, this class allows registering other classes as children. If
    you need to support a custom numeric like type, first use
    numbers.Number.register to mark it as a numeric type -- or inherit
    from one of these existing types.

    Custom numeric types need to support integer addition.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        """Sets key-value pair in the Probablity Map and ensures type
        safety of the value, i.e. it is a numeric type.
        """

        if not isinstance(value, Number):
            raise TypeError("value must be type of {!r}".format(Number))

        super().__setitem__(key, value)

# these methods in counter explicitly return
# a new instance of Counter rather than
# returning an instance of the calling class
__COUNTER_OVERRIDE_METHODS = [
    '__add__', '__sub__', '__or__',
    '__and__', '__pos__', '__neg__',
    ]

def __override(name):
    """Some of Counter's method return an explicit instance of Counter
    rather than attempting to delegate to a child's class.
    This is annoying to say the least.

    Instead of coding the same piece six or more times, this
    coerces the return type with some violence.
    """

    old = getattr(Counter, name)
    return update_wrapper(lambda s, *a, **k: s.__class__(old(s, *a, **k)), old)

for name in __COUNTER_OVERRIDE_METHODS:
    setattr(ProbablityMap, name, __override(name))


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
        """Order of the chain, refers to length of keys"""
        return self.__order

    @order.setter
    def order(self):
        raise TypeError("{}.order is read only".format(self.__class__name__))

    def __iter__(self):
        """Return a default MarkovChainIterator.

        If optional arguments needs to be passed to iterator,
        use :method:`MarkovChain.iterate_chain`
        """
        return MarkovChainIterator(chain=self.data)

    def __setitem__(self, key, value):
        """Sets key-value pair on the MarkovChain and ensures type saftey
        of keys and values.
        """
        if not isinstance(key, tuple) or len(key) != self.order:
            raise TypeError("key must be tuple of length {}".format(self.order))

        if isinstance(value, Mapping):
            value = ProbablityMap(value)
        else:
            raise TypeError(
                "value must be mapping with values "
                "type of {!s}".format(Number)
                )

        return super().__setitem__(key, value)
    
    def __delitem__(self, key):
        raise MarkovError(
            "Cannot delete from probablity chain without possibly "
            "becoming disjoint. If you meant this, use "
            "{}.data.__delitem__".format(self.__class__.__name__)
            )

    @classmethod
    def from_corpus(cls, corpus, order, begin_with=None):
        """Allows building a Markov Chain from a corpus rather than
        constructing it iteratively by hand.

        Corpus may be any iterable. If it is a string and words are
        intended to be preserved, use str.split or similar to convert
        it to a list before hand.

        * corpus: iterable of objects to build the chain over
        * order: order of the new chain
        * begin_with: allows preprending placeholder values
        before the actual content of the corpus to serve as a
        known starting point if needed.
        """

        staging = defaultdict(ProbablityMap)

        if begin_with is not None:
            corpus = chain(begin_with, corpus)

        for w in window(corpus, size=order+1):
            key = tuple(w[:-1])
            value = {w[-1] : 1}
            staging[key].update(value)

        return cls(states=staging, order=order)

    def iterate_chain(self, **kwargs):
        """Allows passing arbitrary keyword arguments to the
        MarkovChainIterator class for iteration.
        """
        return MarkovChainIterator(chain=self.data, **kwargs)

class MarkovChainIterator(object):
    """Iteration handler for MarkovChains.
    
    Maintains a copy of the original chain's keyed states and creates
    a weighted random choice closure from keys' possible states
    to prevent interference when modifying the original chain during iteration.

    It should be noted that this is a non-deterministic, possibly cyclical
    iterator.
    """

    def __init__(self, chain, randomizer=random, begin_at=None, **kwargs):
        """Set initial state of the iterator.

        * chain: MarkovChain or subclass to iterate
        * randomizer: callable that returns floats 0 < n < 1,
        defaults to :func:`~random.random`
        * begin_at: known state to place the iterator in
        """
        self.__chain = self.__build_chain(chain)
        self.__initial_state(begin_at=begin_at, randomizer=randomizer)

    def __initial_state(self, begin_at=None, randomizer=random, **kwargs):
        """Places the iterator into a known or random state.

        Useful for reusing the same iterator multiple times without having
        to rebuild every weighted random chooser.

        * begin_at: known state to place the iterator in
        * randomizer: callable that returns floats 0 < n < 1,
        defaults to :func:`~random.random`
        """

        self.__in_progress = False
        self.__state = self.__possible = None
        self.__invalid = False
        self.randomizer = randomizer

        if begin_at:
            try:
                self.state = begin_at
            except MarkovStateError:
                self.__random_state()
        else:
            self.__random_state()

    reset = __initial_state

    def __random(self, chain):
        """Returns a closure frozen to the current state of a probablity map.
        The closure will allow choosing weighted random, possible states
        from the map.

        Uses the instance's __randomizer attribute if random.random isn't
        desired or for testing purproses
        """

        values, chances = unzip(sorted(chain.items(), key=itemgetter(1)))
        chooser = weighted_choice(chances)

        def random_item():
            """Closure to associate indices returned by
            weighted_choices with with indices of actual values.
            """

            choice = chooser(self.randomizer())
            return values[choice]

        return random_item

    def __build_chain(self, chain):
        """Builds map of states and weighted random
        closures from a Markov Chain's possible states.
        """
        return {state : self.__random(chain[state]) for state in chain}

    def __random_state(self):
        "Puts the chain into a random state."
        self.state = choice(list(self.__chain.keys()))

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, state):
        """Attempts to set the iterator in a known state.

        If that isn't possible, raises a MarkovStateError.
        """
        if state not in self.__chain:
            raise MarkovStateError("Invalid state provided: {}".format(state))

        self.__state = state
        self.__possible = self.__chain[state]

    @property
    def in_progress(self):
        """Reports if the iterator is currently in progress or not.
        """
        return self.__in_progress

    def __iter__(self):
        return self

    def __next__(self):
        """Steps through states until an invalid state is reached,
        which stops iteration.
        """

        self.__in_progress = True
        value = self.__possible()

        if self.__invalid:
            raise DisjointChainError(self.__invalid)

        try:
            self.state = self.__state[1:] + tuple([value])
        except MarkovStateError as e:
            self.__invalid = e
        
        return value
