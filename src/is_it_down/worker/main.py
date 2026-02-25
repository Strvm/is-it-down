"""Provide functionality for `is_it_down.worker.main`."""

import asyncio

from is_it_down.worker.service import run_worker_loop


def main() -> None:
    """Run the entrypoint."""
    asyncio.run(run_worker_loop())


if __name__ == "__main__":
    main()
