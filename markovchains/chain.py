from collections import Counter, UserDict, defaultdict, Mapping
from decimal import Decimal
from fraction import Fraction
from itertools import chain
from numbers import Number
from operator import itemgetter
from random import random, choice

from .errors import MarkovError, DisjointChainError, MarkovStateError
from .utils import window, weighted_choice, unzip

__all__ = (
    "ProbablityMap", "MarkovChain",
    "MarkovChainIterator", "ACCEPTED_TYPES"
    )

# alternatively: register Decimal and Fraction
# *as* members of Number, at the risk of messing
# with someone else's code
ACCEPTED_TYPES = (Decimal, Fraction, Number)

class ProbablityMap(Counter):
    """Simple wrapper for Counter to enforce types on values.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        """Sets key-value pair in the Probablity Map and ensures type
        safety of the value, i.e. it is a numeric type.
        """

        if not isinstance(value, ACCEPTED_TYPES):
            raise TypeError("value must be numeric or numeric like object")

        super().__setitem__(key, value)

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
        use :method:`~MarkovChain.iterate_chain`
        """
        return MarkovChainIterator(self.data)

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
                "type of {!r}".format(ACCEPTED_TYPES)
                )

        return super().__setitem__(key, value)
    
    def __delitem__(self, key):
        raise MarkovError(
            "Cannot delete from probablity chain without "
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

        * corpus:iterable of objects to build the chain over
        * order: order of the new chain
        * begin_with: allows preprending placeholder values
            before the actual content of the corpus to serve as a
            starting point if needed.
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
        return MarkovChainIterator(self.data, **kwargs)

class MarkovChainIterator(object):
    """Iteration handler for MarkovChains.
    
    Maintains a copy of the original chain's keyed states and creates
    a weighted random choice closure from keys' possible states
    to prevent interference when modifying the original chain during iteration.

    It should be noted that this is a non-deterministic, possibly cyclical
    iterator.
    """

    def __init__(self, chains, randomizer=random, begin_with=None, **kwargs):
        self.__chain = self.__build_chain(chains)
        self.__in_progress = False
        self.__state = self.__possible = None
        self.__invalid = False
        self.__randomizer = randomizer

        if begin_with:
            try:
                self.state = begin_with
            except MarkovStateError:
                self.__random_state()
        else:
            self.__random_state()

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

            choice = chooser(self.__randomizer())
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
