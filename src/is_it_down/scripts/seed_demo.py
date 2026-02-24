import asyncio
from datetime import UTC, datetime

from sqlalchemy import select

from is_it_down.db.models import Service, ServiceCheck
from is_it_down.db.session import get_sessionmaker


async def seed_cloudflare() -> None:
    session_factory = get_sessionmaker()

    async with session_factory() as session:
        service = await session.scalar(select(Service).where(Service.slug == "cloudflare"))
        if service is None:
            service = Service(
                slug="cloudflare",
                name="Cloudflare",
                description="Cloudflare core status",
                default_interval_seconds=60,
            )
            session.add(service)
            await session.flush()

        check = await session.scalar(
            select(ServiceCheck).where(
                ServiceCheck.service_id == service.id,
                ServiceCheck.check_key == "cloudflare_status_api",
            )
        )
        if check is None:
            session.add(
                ServiceCheck(
                    service_id=service.id,
                    check_key="cloudflare_status_api",
                    class_path="is_it_down.checkers.services.cloudflare.CloudflareStatusAPICheck",
                    interval_seconds=60,
                    timeout_seconds=4.0,
                    weight=1.0,
                    enabled=True,
                    next_due_at=datetime.now(UTC),
                )
            )

        await session.commit()


def main() -> None:
    asyncio.run(seed_cloudflare())


if __name__ == "__main__":
    main()
