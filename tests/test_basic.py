
import sdypy as sd
import numpy as np

# Pytest will discover and run all test functions named `test_*` or `*_test`.

def test_version():
    """ check the exposes a version attribute """
    assert hasattr(sd, "__version__")
    assert isinstance(sd.__version__, str)


class TestCore:
    """ Testing core functions """

    def test_blank(self):
        """ Test blank """
        assert  np.all(np.equal(np.ones(10), np.ones(10)))
