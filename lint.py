"""One-command lint/format runner: `python lint.py` (add `--check` for CI, no fixes applied)."""

import subprocess
import sys

CHECK_MODE = "--check" in sys.argv

if CHECK_MODE:
    STEPS = {
        "ruff format": ["ruff", "format", "--check", "."],
        "ruff check": ["ruff", "check", "."],
        "mypy": ["mypy", "."],
    }
else:
    STEPS = {
        "ruff format": ["ruff", "format", "."],
        "ruff check": ["ruff", "check", "--fix", "."],
        "mypy": ["mypy", "."],
    }


def main() -> None:
    results = {}
    for name, cmd in STEPS.items():
        print(f"\n=== {name} ===")
        results[name] = subprocess.run(cmd).returncode == 0

    print("\n=== Summary ===")
    for name, passed in results.items():
        print(f"{'PASS' if passed else 'FAIL'}: {name}")

    sys.exit(0 if all(results.values()) else 1)


if __name__ == "__main__":
    main()
