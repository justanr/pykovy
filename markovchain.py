'''Implementation of the actual Markov Chain dictionary.

'''

import collections

from markoverror import CorpusError, MarkovChainError

class MarkovChain(collections.defaultdict):
    '''This class is essentially a fancy defaultdict that always
    uses a list for it's default factory method.

    Key methods such as __contains__ have been modified to reflect the
    nature of the keys (tuples)  for MarkovChains.

    It also provides modified comparison methods, key checking
    and operator shortcuts (chain & other_chain, chain + other_chain. etc).

    '''

    def __init__(self, **kwargs):
        self.order = kwargs.get('order', 2)
        super(MarkovChain, self).__init__(list)

    # Modified equality testers.

    def __eq__(self, other):
        '''Equality for Markov chains is resolved based on order,
        rather than content. Instead of running self.order == other.order
        every time (despite that being more explicit), this allows a
        shortcut to that.

        '''

        if not isinstance(other, MarkovChain):
            return NotImplemented

        return self.order == other.order

    def __ne__(self, other):
        '''See self.__eq__ for implementation details.

        '''
        return not self.__eq__(other)

    # Inequality comparions.
    # These are actually set comparisons.

    def __lt__(self, other):
        '''Tests if self is a proper subset of other.
        That is set(self.keys()) <= set(self.keys()) and 
                set(self.keys()) != set(other.keys())

        '''
        if not isinstance(other, MarkovChain):
            return NotImplemented
        return set(self.keys()) < set(other.keys())

    def __le__(self, other):
        '''Tests if every element in self is in other.

        '''
        if not isinstance(other, MarkovChain):
            return NotImplemented
        return set(self.keys()) <= set(other.keys())

    def __gt__(self, other):
        '''Tests if self is a proper superset of other.
        That is set(self.keys()) > set(other.keys()) and
                set(self.keys()) != set(other.keys())

        '''
        if not isinstance(other, MarkovChain):
            return NotImplemented
        return set(self.keys()) > set(other.keys())

    def __ge__(self, other):
        '''Tests if every element in other is in self.

        '''
        if not isinstance(other, MarkovChain):
            return NotImplemented
        return set(self.keys()) >= set(other.keys())

    # Bitwise and arithmetic operators.
    # I'll leave this blank for now.
    # Implementation has given me a headache before.

    def __and__(self, other):
        raise NotImplementedError

    def __iand__(self, other):
        raise NotImplementedError

    def __or__(self, other):
        raise NotImplementedError

    def __ior__(self, other):
        raise NotImplementedError

    def __add__(self, other):
        raise NotImplementedError

    def __iadd__(self, other):
        raise NotImplementedError

    def __sub__(self, other):
        raise NotImplementedError

    def __isub__(self, other):
        raise NotImplementedError
