Order-N Markov Chains
=====================

A module to build Markov chains. The chains themselves are stored in a heavily modified defaultdict designed for data intergrity. The Markov object, and its descendents, use the chain object to construct probablities (stock market predictions, text gibberishm etc).

Use
---
Under Construction.


Exceptions
----------

There are two built in custom exceptions: `CorpusError` and `MarkovChainError`. CorpusError should only be raised when there is an issue with the actual corpus (such as, it's shorter than the order of the chain, e.g. a corpus of two words in an order-3 chain). MarkovChainError should only be raised when there's an issue with a chain (such as trying to update the chain with another chain that's a different order).

Other
-----
Currently, there's no persistence. Whoops. Pickle and Redis are both being considered. 
