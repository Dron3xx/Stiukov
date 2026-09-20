"""Compatibility alias for the legacy top-level ``main`` import path.

The real application lives in ``app.main``. The test suite patches attributes on
``main.*`` directly, so this module must resolve to the exact same module object
as ``app.main`` rather than a copied namespace.
"""

import sys
from app import main as _app_main

sys.modules[__name__] = _app_main
