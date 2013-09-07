"""Implementation of the actual MarkovChain chains instead of the API handler

"""

import collections

class MarkovChain(collections.defaultdict):
    '''This class is essentially a really fancy defaultdict that always
    uses a list for it's factory method. It includes the abilitiy to
    preform bitwise operators (why of god why) and comparisons with 
    other instances of this class.

    Honestly, I should probably subclass Set (or something similar) 
    as well, but that might  be __TOO__ much of a fucking 
    Frankenstein's monster.

    I don't recommend reading ahead if you don't like type checking.

    '''
    def __init__(self, **kwargs):
        self.order = kwargs.get('order', 2)

        super(MarkovChain, self).__init__(list)

    # Mucking about with interals
    # because why not, it's fun and we'll learn something

    # def __new__(mcs, name, bases, dict):
    #    pass
    # You didn't think I was this dumb, did you?

    def __repr__(self):
        pattern = '<{} Order:{} Length:{}>'
        return pattern.format(type(self).__name__, self.order, len(self))

    def __len__(self):
        return len(self.keys())

    # All equality operators rely on the order of the Markov chain.
    # This is useful for quickly determining if two chains are comparable
    # e.g. g == h instead of g.order == h.order
    # It might be creating some magic,
    # but life's a little better with magic.

    def __eq__(self, other):
        if not isinstance(other, MarkovChain):
            return NotImplemented
        return self.order == other.order

    def __ne__(self, other):
        if not isinstance(other, MarkovChain ):
            return NotImplemented
        return not self.__eq__(other)

    def __lt__(self, other):
        if not isinstance(other, MarkovChain):
            return NotImplemented
        return self.order < other.order

    def __le__(self, other):
        if not isinstance(other, MarkovChain):
            return NotImplemented
        return self.order <= other.order

    def __gt__(self, other):
        if not isinstance(other, MarkovChain):
            return NotImplemented
        return self.order > other.order

    def __ge__(self, other):
        if not isinstance(other, MarkovChain):
            return NotImplemented
        return self.order >= other.order

    # These deal with unions, intersections, etc
    # between two MarkovChain chains

    def __add__(self, other):
        pass

    def __iadd__(self, other):
        pass

    def __sub__(self, other):
        pass

    def __isub__(self, other):
        pass

    def __and__(self, other):
        pass

    def __iand__(self, other):
        pass

    def __xor__(self, other):
        pass

    def __ixor__(self, other):
        pass

    def __or__(self, other):
        pass

    def __ior__(self, other):
        pass

    # Other operations that'll be run on the chain
    
    def __contains__(self, key):
        if isinstance(key, tuple):
            return key in self.keys()
        return any(key in state for state in self.keys())

    def __del__(self, key):
        # Gonna be some logic up in this bitch.
        # -Jesse Pinkman
        pass

    def __setattr__(self, key, value):
        pass

    # Actual code we might care about that's not busy
    # redefining everything in dict or defaultdict
