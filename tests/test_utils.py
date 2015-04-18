from markovchains import utils
from collections import Counter, OrderedDict
from random import Random


def consistent_random():
    return Random(x=0)


def test_window():
    w = utils.window([1, 2, 3, 4, 5, 6], 2)

    assert next(w) == (1, 2)
    assert next(w) == (2, 3)


def test_unzip():
    g = [('a', 1), ('b', 2), ('c', 3)]
    u = list(utils.unzip(g))
    assert u == [('a', 'b', 'c'), (1, 2, 3)]


def test_groupby():
    items = ['red', 'blue', 'green', 'yellow', 'black']
    groups = utils.groupby(items, len)
    assert groups == \
        {3: ['red'], 4: ['blue'], 5: ['green', 'black'], 6: ['yellow']}


def test_head():
    assert utils.head([1, 2, 3]) == [1, 2]


def test_last():
    assert utils.last([1, 2, 3]) == 3


def test_weighted_choice():
    choices = utils.weighted_choice([1, 2, 3, 4])
    chooser = consistent_random().random()
    assert choices.__closure__[0].cell_contents == [1, 3, 6, 10]
    #  returns index, not value
    assert choices(chooser) == 3
    assert choices(0) == 0


def test_weighted_choice_on_map():
    m = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    map_choices = utils.weighted_choice_on_map(m, consistent_random().random)
    assert map_choices() == 'd'


def test_random_key():
    #  OrderedDict allows faking determinism for the test
    m = OrderedDict([(x, x) for x in range(1, 5)])
    assert utils.random_key(m, consistent_random().choice) == 4


def test_patch_return_type():
    @utils.patch_return_type(['__add__'], Counter)
    class MyCounter(Counter):
        pass

    added_my_counter = MyCounter('aab') + MyCounter('bba')
    assert isinstance(added_my_counter, MyCounter)
    assert added_my_counter == {'a': 3, 'b': 3}
