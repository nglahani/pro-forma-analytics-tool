#!/usr/bin/env python3
"""
System Health Check Script

Runs core validation checks to verify system health for operations and monitoring.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], timeout: int = 30) -> tuple[bool, str]:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        ok = result.returncode == 0
        output = result.stdout if ok else result.stderr or result.stdout
        return ok, output.strip()
    except subprocess.TimeoutExpired:
        return False, f"Timeout running: {' '.join(cmd)}"
    except Exception as e:  # pragma: no cover
        return False, f"Error running {' '.join(cmd)}: {e}"


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    checks = []

    # 1) End-to-end demo sanity check
    checks.append(("Demo workflow", [sys.executable, "demo_end_to_end_workflow.py"]))

    # 2) Database performance monitor quick run
    checks.append(
        (
            "DB performance monitor",
            [sys.executable, str(repo_root / "scripts" / "profile_database_performance.py")],
        )
    )

    all_ok = True
    for name, cmd in checks:
        ok, output = run(cmd, timeout=45)
        print(f"[{name}] {'OK' if ok else 'FAIL'}")
        if not ok:
            print(output)
            all_ok = False

    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

