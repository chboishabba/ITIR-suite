"""Executable regression: retired carousel cannot reach transport or scheduling."""
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
DAEMON = ROOT / "scripts" / "autonomous_fleet_daemon.py"


class LegacySafetyTest(unittest.TestCase):
    def test_cli_fails_closed(self):
        result = subprocess.run(
            [sys.executable, str(DAEMON)], cwd=ROOT,
            capture_output=True, text=True, timeout=10,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Legacy title carousel retired.", result.stderr)

    def test_import_and_every_dispatch_path_fail_without_transport(self):
        spec = importlib.util.spec_from_file_location("retired_fleet_daemon", DAEMON)
        module = importlib.util.module_from_spec(spec)
        # If a future regression attempts to load mutation transport on import,
        # the sentinel makes that regression observable without any account access.
        with patch.dict(sys.modules, {"re_gpt.mutation_service": None}):
            spec.loader.exec_module(module)
        self.assertNotIn("MutationService", vars(module))
        routes = [
            (module.ThreadLifecycleManager, (ROOT,)),
            (module.ThreadLifecycleManager.get_thread_info, (object(), "cid")),
            (module.ThreadLifecycleManager.evaluate_lifecycle, (object(), "cid")),
            (module.CarouselFleetOrchestrator, (ROOT,)),
            (module.CarouselFleetOrchestrator.load_fleet_roster, (object(),)),
            (module.CarouselFleetOrchestrator.synthesize_prompt, (object(), "cid", "title")),
            (module.CarouselFleetOrchestrator.advance_single_thread, (object(), {})),
            (module.CarouselFleetOrchestrator.run_carousel_tick, (object(), object())),
            (module.CarouselFleetOrchestrator.run_loop, (object(),)),
            (module.main, ()),
        ]
        with patch.dict(sys.modules, {"re_gpt.mutation_service": None}):
            for route, args in routes:
                with self.subTest(route=route):
                    with self.assertRaises(module.LegacyCarouselRetired):
                        route(*args)


if __name__ == "__main__":
    unittest.main()
