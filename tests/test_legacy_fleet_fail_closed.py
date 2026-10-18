"""Source-level and subprocess safety regression for retired carousel."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DAEMON = ROOT / "scripts" / "autonomous_fleet_daemon.py"

class LegacySafetyTest(unittest.TestCase):
    def test_cli_fails_closed(self):
        result = subprocess.run([sys.executable, str(DAEMON)], cwd=ROOT,
                                capture_output=True, text=True, timeout=10)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Legacy carousel retired", result.stderr)
    def test_guard_precedes_transport_imports(self):
        source = DAEMON.read_text(encoding="utf-8")
        self.assertLess(source.index('if __name__ == "__main__":'), source.index("from re_gpt.mutation_service import MutationService"))

if __name__ == "__main__":
    unittest.main()
