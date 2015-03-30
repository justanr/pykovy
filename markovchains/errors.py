__all__ = ('MarkovError', 'DisjointChainError', 'MarkovStateError')

class MarkovError(Exception):
    """Used as a base exception for the library.
    """
    pass

class DisjointChainError(MarkovError, StopIteration):
    """Used to indicate a disjoint state in a Markov Chain when attempting
    to transition to a new state. Can also be used as StopIteration to end
    building a state chain.
    """
    pass

class MarkovStateError(MarkovError, KeyError):
    """Indicates an invalid state was accessed on a MarkovChain.
    """
    pass
