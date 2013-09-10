try:
    import unittest
except ImportError:
    import unittest2 as unittest

from markovchain import MarkovChain
from markoverror import CorpusError, MarkovChainError

class TestMarkovChain(unittest.TestCase):
    def setUp(self):
        self.corpora = [
                {
                    ('','',''):['Mary'],
                    ('','','Mary'):['had'],
                    ('','Mary', 'had'):['a'],
                    ('Mary', 'had', 'a'):['little'],
                    ('had', 'a', 'little'):['lamb'],
                    ('a', 'little', 'lamb'):['whose'],
                    ('little', 'lamb', 'whose'):['fleece'],
                    ('lamb', 'whose', 'fleece'):['was'],
                    ('whose','fleece', 'was'):['white'],
                    ('fleece', 'was', 'white'):['as'],
                    ('was', 'white', 'as'):['snow'],
                    ('white', 'as', 'snow'):[None]
                },
                {
                    ('','',''):['The'],
                    ('','', 'The'):['quick'],
                    ('','The', 'quick'):['brown'],
                    ('The', 'quick', 'brown'):['fox'],
                    ('quick', 'brown', 'fox'):['jumped'],
                    ('brown', 'fox', 'jumped'):['over'],
                    ('fox', 'jumped', 'over'):['the'],
                    ('jumped', 'over', 'the'):['lazy'],
                    ('over', 'the', 'lazy'):['dog'],
                    ('the', 'lazy', 'dog'):[None]
                }
            ]

    def test_eqaulitiy(self):
        chain = MarkovChain(order=2)
        twochainz = MarkovChain(order=3)
        chain_3 = MarkovChain(order=3)

        self.assertFalse(chain == twochainz)
        self.assertTrue(twochainz == chain_3)

        self.assertTrue(chain != twochainz)
        self.assertFalse(twochainz != chain_3)

    def test_inequality(self):
        chain = MarkovChain(order=3)
        twochainz = MarkovChain(order=3)

        chain.update(self.corpora[0])
        twochainz.update(self.corpora[0])
        twochainz.update({('baa','baa','black'):['sheep']})

        self.assertTrue(chain < twochainz)
        self.assertTrue(chain <= twochainz)

        self.assertTrue(twochainz > chain)
        self.assertTrue(twochainz >= chain)

        twochainz.clear()
        twochainz.update(self.corpora[1])

        self.assertFalse(chain < twochainz)
        self.assertFalse(twochainz > chain)

    def test_contains(self):
        chain = MarkovChain(order=3)

        chain.update(self.corpora[0])

        self.assertTrue('Mary' in chain)
        self.assertTrue(('Mary', 'had', 'a') in chain)

    def test_setitem(self):
        chain = MarkovChain(order=3)

        with self.assertRaises(TypeError):
            chain['test'] = 'test'

        with self.assertRaises(AttributeError):
            chain[('', '')] = 'test'

        with self.assertRaises(AttributeError):
            chain[('','','')] = 'test'

    def test___missing__(self):
        chain = MarkovChain(order=3)

        with self.assertRaises(TypeError):
            chain['test'] = 'test'

        self.assertTrue(len(chain) == 0)

        with self.assertRaises(AttributeError):
            chain[('test',)] = 'test'

        self.assertTrue(len(chain) == 0)

        chain[('','','')]
        self.assertTrue(len(chain) == 1)

    def test_update(self):
        chain = MarkovChain(order=3)

        with self.assertRaises(TypeError):
            chain.update(*self.corpora)

        chain.update(self.corpora[0])

        self.assertTrue('Mary' in chain)
        self.assertTrue(('Mary', 'had', 'a') in chain)
        self.assertTrue(chain[('', '', '')] == ['Mary'])

    def test__find_by_sequence(self):
        chain = MarkovChain(order=3)
        chain.update(self.corpora[0])
        searches = [
            ('Mary',),  
            ('Mary', 'had', 'a'), 
            ('Mary', 'had', 'a','little')
        ]



        for search in searches:
            results = chain._search_by_sequence(search)
            self.assertTrue(results)

    def test_search(self):
        chain = MarkovChain(order=3)
        chain.update(self.corpora[0])

        searches = [
            'Mary', 
            ('Mary',),  
            ('Mary', 'had', 'a'), 
            ('Mary', 'had', 'a','little'),
            ('Mary', 'had', 'a', 'little', 'lamb')
        ]

        for search in searches:
            results = chain.search(search)
            self.assertTrue(results) 

if __name__ == '__main__':
    unittest.main()
