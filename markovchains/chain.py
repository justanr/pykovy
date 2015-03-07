from collections import Counter, UserDict, defaultdict, Mapping
from itertools import chain
from random import random
from .errors import MarkovError, DisjointChainError, MarkovStateError
from .utils import window, weighted_choice_on_map, patch_return_type, random_key

__all__ = (
    "MarkovChain", "MarkovChainIterator", "ProbablityMap"
    )

# these methods in counter explicitly return
# a new instance of Counter rather than
# returning an instance of the calling class
__COUNTER_OVERRIDE_METHODS = [
    '__add__', '__sub__', '__or__',
    '__and__', '__pos__', '__neg__',
    ]

@patch_return_type(__COUNTER_OVERRIDE_METHODS, Counter)
class ProbablityMap(Counter):
    """Specialized Counter class that provides for creating a weighted
    random choice from it's key-value pairs.

    Certain methods from Counter are overriden to provide for correct
    return types (ProbablityMap instead of Counter):
        * __add__
        * __sub__
        * __or__
        * __and__
        * __pos__
        * __neg__

    These overrides are handled by the patch_return_type decorator.

    If ProbablityMap is inherited from, the return type of these methods
    will be of the subclass rather than ProbablityMap.
    """

    def weighted_choice(self, randomizer=random):
        """Returns a closure to allow pulling weighted, random keys
        from the object based on the "counted" value.

        Allows passing a function that returns floats 0 < n < 1
        if random.random should not be used.

        The closure is frozen to the state of the object when it was called.
        """

        return weighted_choice_on_map(self, randomizer)


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

        if not isinstance(value, Mapping):
            raise TypeError("value must be a mapping")

        if not isinstance(value, ProbablityMap):
            value = ProbablityMap(value)

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
        * randomizer: function to generate floats 0 < n < 1
        defaults to random.random
        """

        self.__invalid = False
        self.__state = self.__possible = None
        self.__randomizer = randomizer
        self.__chain = self.__build_chain(chain)

        if begin_at:
            self.__set_state(begin_at)
        else:
            self.__random_state()


    def reset(self, begin_at=None, **kwargs):
        """Places the iterator back into a known or random state.

        Useful for reusing the same iterator multiple times without having
        to rebuild every weighted random chooser.

        * begin_at: known state to place the iterator in
        """

        self.__invalid = False
        self.__state = self.__possible = None

        if begin_at:
            self.__set_state(begin_at)
        else:
            self.__random_state()


    def __set_state(self, begin_at=None):
        """Attempts to place iterator into a known state and falls back
        to a random state if the known state isn't possible.
        """

        try:
            self.state = begin_at
        except MarkovStateError:
            self.__random_state()


    def __build_chain(self, chain):
        """Builds map of states and weighted random
        closures from a Markov Chain's possible states.
        """

        return {
            state : chain[state].weighted_choice(randomizer=self.__randomizer) 
            for state in chain
            }


    def __random_state(self):
        "Puts the chain into a random state."

        self.state = random_key(self.__chain)


    @property
    def state(self):
        """Current state of the iterator.

        If set, the iterator tries to enter a known state. If the known
        state does not exist, a MarkovStateError is raised.
        """

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


    def __iter__(self):
        return self


    def __next__(self):
        """Steps through states until an invalid state is reached,
        which stops iteration with a DisjointChainError.
        """

        value = self.__possible()

        if self.__invalid:
            raise DisjointChainError(self.__invalid)

        try:
            self.state = self.__state[1:] + tuple([value])
        except MarkovStateError as e:
            self.__invalid = e
        
        return value

