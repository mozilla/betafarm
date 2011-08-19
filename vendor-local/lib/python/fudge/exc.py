
"""Exceptions used by the fudge module.

See :ref:`using-fudge` for common scenarios.
"""

__all__ = ['FakeDeclarationError']

class FakeDeclarationError(Exception):
    """Exception in how this :class:`fudge.Fake` was declared."""