'''Implementation of the actual Markov Chain dictionary.

'''

import collections

from . import CorpusError, MarkovChainError

class MarkovChain(collections.defaultdict):
    '''This class is essentially a fancy defaultdict that always
    uses a list for it's default factory method.

    Key methods such as __contains__ have been modified to reflect the
    nature of the keys (tuples)  for MarkovChains.

    It also provides modified comparison methods, key checking
    and operator shortcuts (chain & other_chain, chain + other_chain. etc).

    '''
    
    # Pretty standard magic methods.
    
    def __init__(self, order=2):
        self.order = order or 2
        super(MarkovChain, self).__init__(list)

    def __repr__(self):
        pattern = "<{} Order:{} Length:{}>"
        return pattern.format(type(self).__name__, self.order, len(self))

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

    def _equality_checker(func):
        def checker(self, other):
            if self != other:
                raise MarkovChainError("Incompatible MarkovChains. Tried "
                "comparing order {} with order {}."
                "".format(self.order, other.order))
            return func(self, other)
        return checker
   

    # Inequality comparions.
    # These are actually set comparisons.

    @_equality_checker
    def __lt__(self, other):
        '''Tests if self is a proper subset of other.
        That is self.viewkeys() <= self.viewkeys() and 
                self.viewkeys() != other.viewkeys()

        '''
        return self.viewkeys() < other.viewkeys()

    @_equality_checker
    def __le__(self, other):
        '''Tests if every element in self is in other.

        '''
        return self.viewkeys() <= other.viewkeys()

    @_equality_checker
    def __gt__(self, other):
        '''Tests if self is a proper superset of other.
        That is self.viewkeys() > other.viewkeys() and
                self.viewkeys() != other.viewkeys()

        '''
        return self.viewkeys() > other.viewkeys()

    @_equality_checker
    def __ge__(self, other):
        '''Tests if every element in other is in self.

        '''
        return self.viewkeys() >= other.viewkeys()

    # Bitwise and arithmetic operators.

    # Implemented but subject to change.
    # I think this is terribly ugly and I'm not sure
    # if I want to even keep it implemented.
    # -justanr

    @_equality_checker
    def __and__(self, other):
        ''' &: Intersection
        Creates a new MarkovChain object from the keys shared 
        by two (or more) MarkovChain objects.

        '''
        keys = self.viewkeys() & other
        new = MarkovChain(order=self.order)

        for key in keys:
            new[key] = self[key] + other[key]

        return new

    def __iand__(self, other):
        return self & other

    @_equality_checker
    def __or__(self, other):
        new = MarkovChain(order=self.order)
        keys = self.viewkeys() | other

        for key in keys:
            if key in self:
                new[key] = self[key]
            if key in other:
                new[key] = other[key]
        return new

    def __ior__(self, other):
        return self | other

    @_equality_checker
    def __xor__(self, other):
        new = MarkovChain(order=self.order)
        keys = self.viewkeys() ^ other

        for key in keys:
            if key in self:
                new[key] = self[key]
            else:
                new[key] = other[key]
        return new

    def __ixor__(self, other):
        return self ^ other

    @_equality_checker
    def __add__(self, other):
        new = MarkovChain(order=self.order)

        new.update(self, other)

        return new

    def __iadd__(self, other):
        return self + other

    @_equality_checker
    def __sub__(self, other):
        new = MarkovChain(order=self.order)
        keys = self.viewkeys() - other.viewkeys()

        for key in keys:
            new[key] = self[key]

        return new

    def __isub__(self, other):
        return self - other

    # container methods

    def __contains__(self, search):
        if isinstance(search, tuple):
            return bool(self._search_by_sequence(search))
        return any(search in key for key in self.keys())

    def __setitem__(self, key, value):
        #DANGER WILL ROBINSON!
        '''Over riden method to ensure data intergity.
        Ensures that key is a tuple with the proper length
        and that value is a list.

        Type checking...I know.

        '''

        if not isinstance(key, tuple):
            raise TypeError('MarkovChain expects tuple as key, {} provided.'
                                 ''.format(type(key).__name__))
        elif len(key) != self.order:
            raise AttributeError('MarkovChain expects key with length {}, '
                                 '{} length given'.format(self.order, len(key)))
        elif not isinstance(value, list):
            raise AttributeError('MarkovChain expects a list as a value, '
                                 '{} provided.'.format(type(value).__name__))
        else:
            super(MarkovChain, self).__setitem__(key, value)

#    Will have to be overridden to perserve chain logic.
    def __delitem__(self, key):
        keys = self.search(key)

        for key in keys:
            super(MarkovChain, self).__delitem__(key)

    # pickle methods
    # I'm 100% lost here. Uh-oh.
    # I know to store self.order for pickling, 
    # I'll have to override some of these.

    def __getstate__(self):
        pass

    def __setstate__(self, state):
        pass

    def __reduce__(self):
        pass

    def __reduce_ex__(self):
        pass

    # over riding specific methods

    def update(self, *args):
        if args:
            for arg in args:
                arg = dict(arg)
                for key, value in arg.iteritems():
                    self[key] = value
            return None
        else:
            raise AttributeError("MarkovChain.update expects at least one"
                                 "argument to be passed. Received none.")

    def setdefault(self, key, value=None):
        # may have to be overridden.
        pass

    def pop(self, key, default=None):
        pass

    # actual custom code.
    # criminey.
    
    # internal methods

    def _search_by_sequence(self, search):
        
        # keys are tuple and won't match across types
        search = tuple(search)
        length = len(search)
        match  = []

        if length == self.order:
            if search in self.keys():
                match.append(search)

        elif length < self.order:
           for n in range(self.order):
                if n+length > self.order:
                    break
                for key in self.keys():
                    if key[n:length+n] == search:
                        match.append(key)

        else: #must be longer
            for n in range(self.order):
                if n+self.order > length:
                    break
                for key in self.keys():
                    if search[n:n+self.order] == key:
                        match.append(key) 
        return match
    
    # API

    def search(self, search):
        if isinstance(search, str):
            search = (search, )

        return self._search_by_sequence(search)

    def remove(self, keyword):
        if keyword in self:
            for key in self.keys():
                if keyword in key:
                    del self[key]

                else:
                    try:
                        self[key].remove(keyword)
                    except ValueError:
                        pass

                    if not self[key]:
                        del self[key]

