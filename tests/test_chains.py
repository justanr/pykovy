import pytest
from markovchains import chain
from random import Random


def consistent_random():
    return Random(x=0)


def test_ProbablityMap_overridden():
    prob_map = chain.ProbablityMap('aab')
    assert isinstance(prob_map + prob_map, chain.ProbablityMap)
    assert isinstance(prob_map - prob_map, chain.ProbablityMap)
    assert isinstance(prob_map | prob_map, chain.ProbablityMap)
    assert isinstance(prob_map & prob_map, chain.ProbablityMap)
    assert isinstance(+prob_map, chain.ProbablityMap)
    assert isinstance(-prob_map, chain.ProbablityMap)


def test_ProbablityMap_weighted_random():
    prob_map = chain.ProbablityMap('aab')
    weighter = consistent_random().random
    assert prob_map.weighted_choice(randomizer=weighter)() == 'a'
    assert prob_map.weighted_choice(randomizer=lambda: 0)() == 'b'


def test_MarkovChain():
    my_chain = chain.MarkovChain(order=1)
    assert my_chain.data == {}
    assert my_chain.order == 1


def test_MarkovChain_init_with_states():
    prob_map = chain.ProbablityMap('aab')
    my_chain = chain.MarkovChain(order=1, states={('a',): prob_map})
    assert my_chain.data == {('a',): prob_map}


def test_MarkovChain_order_read_only():
    with pytest.raises(TypeError) as e:
        chain.MarkovChain(order=1).order = 2

    assert 'read only' in str(e.value)


def test_MarkovChain_eq():
    states = [{('a', 'b'): c} for c in
              (chain.ProbablityMap('aab'), chain.ProbablityMap('abb'))]
    chains = [chain.MarkovChain(order=2, states=states[i]) for i in (0, 1)]
    assert chain.MarkovChain(order=2) == chain.MarkovChain(order=2)
    assert chains[0] == chains[1]


def test_MarkovChain_iter():
    mc = chain.MarkovChain(order=1, states={('a',): chain.ProbablityMap('a')})
    assert isinstance(iter(mc), chain.MarkovChainIterator)


def test_MarkovChain_iterate_chain():
    mc = chain.MarkovChain(order=1, states={('a',): chain.ProbablityMap('a')})
    r = consistent_random().random
    mci = mc.iterate_chain(randomizer=r)
    assert mci._randomizer is r


@pytest.mark.parametrize('key, value', [
    (('a',), {'a': 3}),
    ('ab', {'a': 3})
])
def test_MarkovChain_setitem_raises_with_bad_key(key, value):
    mc = chain.MarkovChain(order=2)

    with pytest.raises(TypeError) as err:
        mc[key] = value

    assert 'key must be tuple of length 2' == str(err.value)


def test_MarkovChain_setitem_raises_with_bad_value():
    mc = chain.MarkovChain(order=2)

    with pytest.raises(TypeError) as err:
        mc[('a', 'b')] = 'a'

    assert 'value must be a mapping' == str(err.value)


def test_MarkovChain_setitem_converts_mapping():
    mc = chain.MarkovChain(order=2)

    mc[('a', 'b')] = {'a': 4}

    assert mc.data == {('a', 'b'): chain.ProbablityMap({'a': 4})}


def test_MarkovChain_getitem():
    mc = chain.MarkovChain(order=2, states={('a', 'b'): {'a': 4}})

    assert mc[('a', 'b')] == mc['a', 'b'] == {'a': 4}


def test_MarkovChain_from_corpus():
    corpus = 'mary had a little lamb'.split()
    mc = chain.MarkovChain.from_corpus(corpus, order=2)

    states = {('mary', 'had'): {'a': 1},
              ('had', 'a'): {'little': 1},
              ('a', 'little'): {'lamb': 1}}

    assert mc.data == states
    assert mc.order == 2


def test_MarkovChain_from_corpus_with_start_pad():
    corpus = 'mary had a little lamb'.split()
    mc = chain.MarkovChain.from_corpus(corpus, order=2, begin_with=('', ''))

    states = {('', ''): {'mary': 1},
              ('', 'mary'): {'had': 1},
              ('mary', 'had'): {'a': 1},
              ('had', 'a'): {'little': 1},
              ('a', 'little'): {'lamb': 1}}

    assert mc.data == states
    assert mc.order == 2


def test_MarkovChain_delitem_raises():
    with pytest.raises(chain.MarkovError) as err:
        del chain.MarkovChain(order=2)['', '']

    assert 'disjoint' in str(err.value)
