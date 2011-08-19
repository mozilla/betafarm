
from fudge import *

def test_import_all():
    assert "clear_calls" in globals()
    assert "clear_expectations" in globals()
    assert "verify" in globals()
    assert "Fake" in globals()
    assert "test" in globals()
    assert "patch" in globals()