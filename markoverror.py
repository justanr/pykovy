'''
Exceptions used in the Markov chain module.
'''

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


