class MarkovError(Exception):
    pass

class DisjointChainError(MarkovError, StopIteration):
    pass

class MarkovStateError(MarkovError, KeyError):
    pass
