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
