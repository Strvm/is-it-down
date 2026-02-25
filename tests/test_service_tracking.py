from datetime import UTC, datetime

from is_it_down.api.bigquery_store import _sort_service_summaries_by_views
from is_it_down.api.schemas import ServiceSummary
from is_it_down.api.service_tracking_middleware import _service_slug_from_path


def _summary(slug: str) -> ServiceSummary:
    return ServiceSummary(
        service_id=1,
        slug=slug,
        name=slug.title(),
        logo_url=f"https://example.com/{slug}.svg",
        status="up",
        raw_score=100.0,
        effective_score=100.0,
        observed_at=datetime.now(UTC),
        dependency_impacted=False,
        attribution_confidence=0.0,
        probable_root_service_id=None,
    )


def test_sort_service_summaries_by_recent_views() -> None:
    summaries = [_summary("github"), _summary("gitlab"), _summary("cloudflare")]
    view_counts = {"gitlab": 9, "cloudflare": 4}

    sorted_summaries = _sort_service_summaries_by_views(summaries, view_counts)

    assert [summary.slug for summary in sorted_summaries] == ["gitlab", "cloudflare", "github"]


def test_sort_service_summaries_falls_back_to_slug_when_views_tie() -> None:
    summaries = [_summary("vercel"), _summary("github"), _summary("gitlab")]

    sorted_summaries = _sort_service_summaries_by_views(summaries, {})

    assert [summary.slug for summary in sorted_summaries] == ["github", "gitlab", "vercel"]


def test_service_slug_from_path_matches_detail_path_only() -> None:
    assert _service_slug_from_path("/v1/services/gitlab") == "gitlab"
    assert _service_slug_from_path("/v1/services/gitlab/") == "gitlab"

    assert _service_slug_from_path("/v1/services") is None
    assert _service_slug_from_path("/v1/services/uptime") is None
    assert _service_slug_from_path("/v1/services/checker-trends") is None
    assert _service_slug_from_path("/v1/services/gitlab/history") is None
    assert _service_slug_from_path("/v1/incidents") is None
