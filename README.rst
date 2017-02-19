=====================
Order-N Markov Chains
=====================

A simple library for building Order-N Markov Chains.

There's nothing fancy here, just a modified `collections.Counter` and `collections.MutableMapping` to handle type saftey on a few things, some helper functions and an iterator for the Markov Chain class.

Why?
====

Why not? Markov Chains are cool. Sure, I didn't include Monte Carlo, Hidden Markov Chains, lexical analysis and tagging and the whole host of other things that accompany more robust Markov libraries.

But sometimes you just want generate funny text from H.P. Lovecraft stories.

Uses
====

* Build custom Lipsum generators!
* Analyze patterns in your meals!
* Predict the stock market!
* Combine it with AST to determine your programming habits!

I guess more seriously, there's two ways to build the chains themselves:

* Construct `ProbablityMap` from a source -- it acts just like `collections.Counter` except it'll pitch a fit if your value isn't an instance of `numbers.Number` and then attach it to a chain via `MarkovChain.update({('known', 'state'):MyProbMap})`
* Use `MarkovChain.from_corpus` to automatically build the chain for you. Note that it accepts any iterable, so if you have a string and want words rather than characters, use `str.split`

To iterate over the Chain -- usually to generate place holder non-sense text -- you can simply do `for value in my_markov_chain:`. Simply iterating over the chain gives you a default `MarkovChainIterator` instance. 

If you'd like a configured instance, use `MarkovChain.iterate_chain` which can pass arbitrary keywords to `MarkovChainIterator`. 

Alternatively you can just create the `MarkovChainIterator` yourself. It doesn't bother me.

Classes
=======

* `ProbablityMap`: Modified `collections.Counter` that handles weighted, random choices from its key-value pairs via a closure.
* `MarkovChain`: Simple modification on a `collections.MutableMapping` to collate `ProbablityMap` instances together to form a coherent chain.
* `MarkovChainIterator`: Handles passing through possible states in a `MarkovChain` instance to produce non-deterministic state changes.

Exceptions
==========

I've included the new `MarkovError` exception and two sub-exceptions:

* `MarkovError`: "Root" exception for library.
* `MarkovStateError`: used in place (read: subclass of) KeyError when an invalid state is passed to the chain.
* `DisjointChainError`: used in place of StopIteration when the `MarkovChainIterator` can not progress to the next possible state.


