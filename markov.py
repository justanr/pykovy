import random
from collections import defaultdict

class CorpusException(Exception):
    pass

class MarkovChainError(Exception):
    pass

class Markov(object):
    
    def __init__(self, n=2, links=10):
        self._chain = defaultdict(list)
        self._chance = defaultdict(dict)
        self.n = n
        self._state = None
        self.links = links
        self.seperator = " "
        self.nonword = "\n"
    
    def _get_initial(self):
        return tuple(['']*self.n)

    def _break(self, source):
        
        prev = self._get_initial()

        source = source.split(self.seperator)

        if len(source) < self.n+1:
            raise CorpusError("Corpus is too short.")

        else:        
            for word in source:
                yield prev, word
                prev = prev[1:] + tuple([word])

    def _set_state(self, state):
        self._state = state if state in self._chain.keys() else None

    def _get_state(self):
        if self._state is None:
            self._state = random.choice(self._chain.keys())
        else:
            word = random.choice(self._chain[self._state])
            self._state = self._state[1:] + tuple([word])

        return self._state

    def _pull_from_state(self):
        return random.choice(self._chain[self.state])

    def _update_chain(self, chain):
        if all(len(key) == self.n for key in chain.keys()):
            for key, links in chain.items():
                chain._chain[key].extend(links)

        else:
            raise MarkovChainError("Supplied chain is not the same order as the current chain.")
        
    def _search_chain(self, search):
        length = len(search)

        if length > self.n:
            length = self.n
            search = search[:length]

        states = [state for state in self._chain.keys() if state[:length] == search]
        self.state = random.choice(states or [''])
        
        return (self._state is not None)
        
    
    def _add_to_chain(self, key, links):
        self._chain[key].append(links)

    def learn(self, source):
        for parts in self._break(source):
            self._add_to_chain(parts[0], parts[1])

    def build_chain(self, begins_with=None):
        chain = []

        if begins_with is not None:
            try:
                if self._search_chain(begins_with):
                    chain.extend(begins_with)
            except TypeError:
                pass

        while len(chain) < self.links:
            chain.append(self._pull_from_state())
        return chain

    state = property(_get_state, _set_state)
