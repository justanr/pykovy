Order-N Markov Chains
=====================

A simple class to build order-n Markov Chains. Includes a method to start a chain with a certain combination if the key exists in the chain.

Use
---
First you want to gather your corpus -- I'm fond of using Lovecraft texts.

```
import markov
from glob import glob

chain = markov.Markov(3)

texts = glob('lovecraft/*.txt')

for text in texts:
    with open(text, 'rb') as fh:
        chain.learn(fh.read())

chain.build_chain()
```

Sample output might be something like: 

```
['five',
 'feet',
 'long',
 'with',
 'crustaceous',
 'bodies',
 'bearing',
 'vast',
 'pairs'
 'of']
```

You can also specify a chain begin with a certain key, if it exists.

```
#search key must be a tuple.
search = ('bearing', 'vast')

chain.build_chain(search)
```

Output:
```
['bearing',
 'vast',
 'fins',
 'or',
 'membranous',
 'wings',
 'and'
 'several',
 'sets',
 'of']
```

If the search key doesn't exist, or is poorly formatted, it's discarded. Currently, any search keys that are longer than the chain's order are tuncated to the order.

Exceptions
----------

There are two built in custom exceptions: `CorpusError` and `MarkovChainError`. CorpusError should only be raised when there is an issue with the actual corpus (such as, it's shorter than the order of the chain, e.g. a corpus of two words in an order-3 chain). MarkovChainError should only be raised when there's an issue with a chain (such as trying to update the chain with another chain that's a different order).

Other
-----
Currently, there's no persistence. Whoops. 
