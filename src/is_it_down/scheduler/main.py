"""Provide functionality for `is_it_down.scheduler.main`."""

import asyncio

from is_it_down.scheduler.service import run_scheduler_loop


def main() -> None:
    """Run the entrypoint."""
    asyncio.run(run_scheduler_loop())


if __name__ == "__main__":
    main()
