"""Shared helpers for the tests. The project folder is put on the path; a stand-in dry run is made once and shared."""
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import bench  # noqa: E402
import routing as RT  # noqa: E402
import standin  # noqa: E402
from room import Room  # noqa: E402

DEFAULT_ARMS = list(bench.load_config()["default_arms"])
PRESETS = bench.load_config()["presets"]
VENV_PY = Path(r"C:\Users\joshd\Workbench\autoevals-scorer\.venv\Scripts\python.exe")
_cache = {}


def make_runner(out_dir, workers=1, cap=5.0, stop_min=120, client=None, clock=None, cfg=None):
    room = Room(Path(out_dir) / "room.jsonl", fsync=False)
    cfg = cfg or bench.load_config()
    kw = {"clock": clock} if clock else {}
    return bench.Runner(room, client or standin.StandIn(), cfg, standin=True, cap_usd=cap, stop_after_min=stop_min,
                        workers=workers, force_shim=True, **kw)


def dry(reps=1, workers=1):
    """One shared stand-in run (all five arms, 5 rounds, `reps` reps) in a temp folder."""
    key = (reps, workers)
    if key not in _cache:
        d = tempfile.mkdtemp(prefix="eab-test-dry-")
        R = make_runner(d, workers=workers)
        code = R.run_all(DEFAULT_ARMS, reps, "standin")
        assert code == 0, code
        _cache[key] = (R, Path(d))
    return _cache[key]
