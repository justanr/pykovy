"""Implementation of the actual MarkovChain chains instead of the API handler

"""

import collections

from markoverror import CorpusError, MarkovChainError

class MarkovChain(collections.defaultdict):
    '''This class is essentially a really fancy defaultdict that always
    uses a list for it's factory method.

    '''

    def __init__(self, **kwargs):
        self.order = kwargs.get('order', 2)

        super(MarkovChain, self).__init__(list)

    def __repr__(self):
        pattern = '<{} Order:{} Length:{}>'
        return pattern.format(type(self).__name__, self.order, len(self))

    def __len__(self):
        return len(self.keys())

    def __eq__(self, other):
        """Equality operators rely on the order of the Markov chain.
        This is useful for quickly determining if two chains are comparable
        and preserving encapsulation.
        e.g. g == h instead of g.order == h.order


        """
        if not isinstance(other, MarkovChain):
            return NotImplemented
        return self.order == other.order

    def __ne__(self, other):
        """See: MarkovChain.__eq__

        """
        if not isinstance(other, MarkovChain):
            return NotImplemented
        return not self.__eq__(other)
    
    # Inequality comparisons are actually
    # set comparions: supersets, subsets,
    # et cetera.

    # every key in self is in other
    # but other might contain just those keys
    def __lt__(self, other):
        """Determines if self is a subset of other."""
        return set(self.keys()) < set(other.keys())
    
    # every key in self is in other
    # and other contains other keys
    def __le__(self, other):
        """Determines if self is a true subset of other."""
        return set(self.keys()) <= set(other.keys())

    # every key in other is in self
    # but self might just contain those keys
    def __gt__(self, other):
        """Determines if self is a superset of other."""
        return set(self.keys()) > set(other.keys())

    # every key in other is in self
    # and self contains other keys
    def __ge__(self, other):
        """Determines if self is a true superset of other."""
        return set(self.keys()) >= set(other.keys())

    # Bitwise operators can be used on dictionaries by
    # calling {}.view[keys|values|items]()
    # But this is going to be a shortcut on that.
    # Plus, Markov chain orders need to be taken into
    # account, otherwise mixed order chains could happen.

    def __and__(self, other):
        """ &: Intersect
         All keys that are in both self and other
         Combine those key values into a new chain.

        """

        if self != other:
            raise MarkovChainError(
                "Different Markov chain orders."
                "Order {0} and Order{1} provided."
                "".format(self.order, other.order)
                )

        keys = self.viewkeys() & other
        new = MarkovChain(order=self.order)

        for key in keys:
            new[key] = self[key] + other[key]

        return new

    def __iand__(self, other):
        """See MarkovChain.__and__ for implementation details."""
        new = self & other
        self.clear()
        self.update(new)

    def __xor__(self, other):
        """ ^: Symmetric Difference
         All keys that are in self or other but not both
         Return the key:value pairs for these.
         Probably not entirely helpful, but it's here.

        """

        if self != other:
            raise MarkovChainError(
                "Different Markov chain orders."
                "Order {0} and Order{1} provided."
                "".format(self.order, other.order)
                )

        keys = self.viewkeys() ^ other
        new = MarkovChain(order=self.order)

        for key in keys:
            try:
                new[key] = self[key]
            except KeyError:
                new[key] = other[key]
        
        return new

    def __ixor__(self, other):
        """See: MarkovChain.__xor__ for implementation details."""
        new = self ^ other
        self.clear()
        self.update(new)

    def __or__(self, other):
        """ |: Union
         All keys that are in self or other, maybe both
         Return the key:value pairs for these.

        """
        
        if self != other:
            raise MarkovChainError(
                "Different Markov chain orders."
                "Order {0} and Order{1} provided."
                "".format(self.order, other.order)
                )
        
        keys = self.viewkeys() | other
        new = MarkovChain(order=self.order)

        for key in keys:
            if key in self:
                new[key].append(self[key])
            if key in other:
                new[key].append(other[key])

        return new

    def __ior__(self, other):
        """See MarkovChain.__or__ for implementation details."""
        new = self | other
        self.clear()
        self.update(new)

    def __sub__(self, other):
        """ -: Diff
         Keys that appear in self that don't appear in other
         Returns new MarkovChain with

        """
        if self != other:
            raise MarkovChainError(
                "Different Markov chain orders."
                "Order {0} and Order{1} provided."
                "".format(self.order, other.order)
                )
 
        keys = self.viewkeys() - other.viewkeys()
        new = MarkovChain(order=self.order)

        for key in keys:
            new[key] = self[key]

        return new

    def __isub__(self, other):
        """See MarkovChain.__sub__ for implementation details."""
        new = self - other
        self.clear()
        self.update(new)

    # Other operations that'll be run on the chain
    
    def __contains__(self, key):
        if isinstance(key, tuple):
            return key in self.keys()
        return any(key in state for state in self.keys())

    def __del__(self, key):
        """Removes a key.
        NOTE: This is different from MarkovChain.remove(key) 
        which removes a keyword and all references to it.
        """
        # Gonna be some logic up in this bitch.
        # -Jesse Pinkman.
        pass


    def __setattr__(self, key, value):
        # Again, logic to make sure a key isn't set
        # that doesn't match the chain order.

        pass

    # Actual code we might care about that's not busy
    # redefining everything in dict or defaultdict

    def remove(self, keyword):
        """Removes a keyword from the chain and all references to it.

        """
        if keyword in self:
            for key in self.keys():
                if keyword in key:
                    del self[key]

                else:
                    try:
                        self[key].remove(keyword)
                    except ValueError:
                        pass

                    # remove potentially empty chains now
                    if not self[key]:
                        del self[key]

    def extend(self, other):
        """Extend current chain with another."""
        if self != other:
            raise MarkovChainError

        for key, value in other.iteritems():
            self[key].extend(value)
