import sys

from .bridge import run as run_bridge
from .server import main as run_fastmcp


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--bridge":
        raise SystemExit(run_bridge())
    raise SystemExit(run_fastmcp())
