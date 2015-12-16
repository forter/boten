from boten.core import Cached
from random import random


@Cached
def cacheme():
    return random


def test_check_cache():
    val1 = cacheme()
    val2 = cacheme()
    assert val1 == val2
