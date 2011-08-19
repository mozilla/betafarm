
# This is a hack to make the built (2to3) tests 
# run in Python 3.  That is, so Nose discovers all tests.
# See tox.ini

# FIXME: this is dumb

from fudge.tests.test_fudge import *
from fudge.tests.test_import_all import *
from fudge.tests.test_inspector import *
from fudge.tests.test_inspector_import_all import *
from fudge.tests.test_patcher import *
from fudge.tests.test_registry import *