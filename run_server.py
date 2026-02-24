"""
Compat wrapper for backend entrypoint.
"""

from run import _ensure_port_available, _resolve_bind_port, main


if __name__ == "__main__":
    raise SystemExit(main())
