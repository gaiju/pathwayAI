"""Refresh public community helpers after Streamlit source updates, not user state."""
import hashlib
import importlib
from pathlib import Path
import sys
from threading import RLock

_LOCK = RLock()
_BASE = Path(__file__).resolve().parent
# Dependencies first: later modules import functions/constants from earlier ones.
_MODULES = ('mid_hudson_counties', 'county_report_context', 'community_action_summary',
            'county_planning_indicators', 'county_burden_report', 'county_brief_pdf')
_MARKER = '_PATHWAYAI_COMMUNITY_SOURCE_SHA256'


def ensure_current_community_modules():
    """Reload the group once when a cached helper predates its on-disk source."""
    with _LOCK:
        hashes = {name: hashlib.sha256((_BASE / (name + '.py')).read_bytes()).hexdigest()
                  for name in _MODULES}
        stale = any(name in sys.modules and getattr(sys.modules[name], _MARKER, None) != hashes[name]
                    for name in _MODULES)
        importlib.invalidate_caches()
        for name in _MODULES:
            cached = name in sys.modules
            module = importlib.import_module(name)
            if stale and cached:
                module = importlib.reload(module)
            setattr(module, _MARKER, hashes[name])
