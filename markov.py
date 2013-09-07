'''
Module for generating Markov chains.
'''

import random
import collections

from markovchain import MarkovChain

__all__ = ['CorpusError', 'MarkovChainError', 'Markov', 'TextMarkov']


class CorpusError(Exception):
    '''
    Used for errors with the corpus, such as it being too short.
    '''
    pass

class MarkovChainError(Exception):
    '''
    Used for errors within a chain, such as trying to union different orders.
    '''
    pass

class Markov(object):

    def __init__(self, **kwargs):
        self.order = kwargs.get('order', 3)
        self.links = kwargs.get('links', 10)

        self._chain = MarkovChain(order=self.order)
        
    # Now for the nitty gritty internals of the actual chains,
    def _get_initial(self):
        return tuple(['']*self.order)
    

    def _break_corpus(self, corpus):
        """Accepts an iterable and returns a generator of it's components

        """
        if len(corpus) < self.order + 1:
            raise CorpusError("""The provided corpus is too short.
                              It must be at least {0} items long ({1} provided)
                              """.format(self.order, len(corpus)))

        return (item for item in corpus)

    def _yield_corpus(self, corpus):
        """Accepts an iterable and creates a series of tuples based on it.

        The iterable is first passed to Markov._break_corpus which is responsible
        for dismantling it into component parts.

        """
        prev = self._get_initial()      
        
        for item in self._break_corpus(corpus):
            yield prev, item

            prev = prev[1:] + (item,)

        yield prev[1:] + (None,), None

    def _add_to_chain(self, key, links):
        """Simple internal method to add an item to a key's links.

        """
        self._chain[key].append(links)

    def _get_state(self):
        pass

    def _set_state(self):
        pass

    def _next_state(self):
        pass

    def _remove(self, keyword):
        """Removes a key word and all references to it.

        """
        
        if keyword in self:
            for key in self.keys():
                if keyword in key:
                    del self._chain[key]

                else:
                    try:
                        self._chain[key].remove(keyword)
                    except ValueError:
                        pass

                    # check if the links are empty now
                    # remove if they are.
                    if not self._chain[key]:
                        del self._chain[key]
                

    def _extend_chain(self, other):
        """Internal method for extending the current Markov chain with
        an external dictionary. Both the external dictionary and the 
        current chain must be the same order for this operation to be
        successful.

        """
        if all(len(key) == self.order for key in other.keys()):
            for key, links in other.items():
                self._chain[key].extend(links)
        else:
            raise MarkovChainError("Provided Markov chain has a different"
                                   " order than the current chain.")

    def _search_chain(self, search):
        length = len(search)

        if length > self.order:
            length = self.order
            search = search[:length]

        if search in self:
            f = lambda x: x[:length] == search
            
            # states = filter(f, self._chain.keys())
            # I prefer comprehensions. -ANR
            states = [state for state in self._chain.keys() if f(state)]
            self.state = random.choice(states or [''])
            
            return (self.state is not None)

        return False


    # Public API for using the chains.
    
    state = property(_get_state, _set_state)

    def keys(self):
        return self._chain.keys()

    def values(self):
        return self._chain.values()

    def extend(self, other):
        pass

    def remove(self, key):
        self._remove(key)

    def learn(self, corpus):
        for each in self._yield_corpus(corpus):
            self._add_to_chain(each[0], each[1])

    def build_chain(self, **kwargs):
        search = kwargs.get('search', None)
        pass

class TextMarkov(Markov):
    
    __NONWORD__ = "\n"
    __PUNCUATION__ = ['.', ',', '"', "'", ':', ':', '?', '!', '(', ')']

    def __init__(self, **kwargs):

        self.seperator = kwargs.get('seperator', ' ')

        super(TextMarkov, self).__init__(**kwargs)
    
    def _break_corpus(self, corpus):
        
        length = len(corpus.split(self.seperator))

        if length < self.order + 1:
            raise CorpusError("""The provided is too shorted."""
                              """Expected corpus to be at least {} words long."""
                              """ ({} words long)""".format(self.order+1, length))

        return (word.rstrip(TextMarkov.__NONWORD__) for word in corpus.split(self.seperator))

    def _sanitize_corpus(self, corpus):
        pass

    def _analyze_sentence(self, sentence):
        pass

    def _analyze_paragraph(self, paragraph):
        pass
