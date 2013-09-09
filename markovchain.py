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
    
    # Pretty standard magic methods.
    
    def __init__(self, **kwargs):
        self.order = kwargs.get('order', 2)
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

    # container methods

    def __contains__(self, key):
        if isinstance(key, tuple):
            return key in self.keys()
        return any(key in state for state in self.keys())

    def __setitem__(self, key, value):
        #DANGER WILL ROBINSON!
        '''Over riden method to ensure data intergity.
        Ensures that key is a tuple with the proper length
        and that value is a list.

        Type checking...I know.

        '''

        if not isinstance(key, tuple):
            raise AttributeError('MarkovChain expects tuple as key, {} provided.'
                            ''.format(type(key).__name__))
        elif len(key) != self.order:
            raise AttributeError('MarkovChain expects a tuple with length {}, '
                                 '{} length given'.format(self.order, len(key)))
        elif not isinstance(value, list):
            raise AttributeError('MarkovChain expects a list as a value, '
                                 '{} provided.'.format(type(value).__name__))
        else:
            super(MarkovChain, self).__setitem__(key, value)

    def __getitem__(self, key):
        # may have to be overridden.
        pass

    def __missing__(self, key):
        # may have to be overridden. 
        pass

    def __delitem__(self, key):
        # Will have to be overridden to perserve chain logic.
        pass

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

    def update(self, *args, **kwargs):
        if args:
            if len(args) > 1:
                raise TypeError("MarkovChain.update expects at most 1 arguments, "
                                "got {}.".format(len(args)))

            other = dict(args[0])
            
            for key, value in other.iteritems():
                self[key] = value

        for key, value in kwargs.iteritems():
            self[key] = value

    def setdefault(self, key, value=None):
        # may have to be overridden.
        pass

    def pop(self, default=None):
        # will have to be overridden to perserve chain logic.
        pass
