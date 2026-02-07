from __future__ import annotations

import sys

from src.interface_adapter.controller.cli import main as _impl

sys.modules[__name__] = _impl
