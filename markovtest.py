try:
    import unittest
except ImportError:
    import unittest2 as unittest

import markovchain as mc

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
        chain = mc.MarkovChain(order=2)
        twochainz = mc.MarkovChain(order=3)
        chain_3 = mc.MarkovChain(order=3)

        self.assertFalse(chain == twochainz)
        self.assertTrue(twochainz == chain_3)

        self.assertTrue(chain != twochainz)
        self.assertFalse(twochainz != chain_3)

    def test_inequality(self):
        chain = mc.MarkovChain(order=3)
        twochainz = mc.MarkovChain(order=3)

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

if __name__ == '__main__':
    unittest.main()
