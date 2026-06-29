"""Compatibility shim for legacy joblib models.

This module keeps backward compatibility with serialized pipelines that
reference `preprocessing` at repository root.
"""

from backend.api.preprocessing import *  # noqa: F401,F403
