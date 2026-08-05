from __future__ import annotations

import argparse
from pathlib import Path

from .config import default_config
from .runner import run


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the reproducible Factor Lab baseline.")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--output-root", default=None)
    args = parser.parse_args()
    cfg = default_config()
    path = run(cfg, Path(args.output_root) if args.output_root else None, args.run_id)
    print(path)


if __name__ == "__main__":
    main()

