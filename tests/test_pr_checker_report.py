from is_it_down.scripts.pr_checker_report import (
    CheckerExecutionResult,
    changed_service_checker_modules,
    render_comment_markdown,
    selected_service_checker_classes,
    selected_service_checker_classes_with_errors,
)


def test_changed_service_checker_modules_filters_and_extracts_modules() -> None:
    changed_files = [
        "README.md",
        "src/is_it_down/checkers/services/destiny.py",
        "src/is_it_down/checkers/services/__init__.py",
        "src/is_it_down/checkers/services/discord.py",
        "src/is_it_down/core/scoring.py",
    ]

    modules = changed_service_checker_modules(changed_files)
    assert modules == ["destiny", "discord"]


def test_selected_service_checker_classes_matches_changed_modules() -> None:
    changed_files = [
        "src/is_it_down/checkers/services/cloudflare.py",
        "src/is_it_down/checkers/services/discord.py",
    ]

    selected = selected_service_checker_classes(changed_files)
    selected_modules = [module_name for module_name, _ in selected]

    assert selected_modules == ["cloudflare", "discord"]


def test_render_comment_markdown_handles_no_selected_modules() -> None:
    markdown = render_comment_markdown(changed_files=["README.md"], selected_modules=[], results=[])

    assert "<!-- is-it-down-checker-results -->" in markdown
    assert "No added/modified service checker files" in markdown


def test_render_comment_markdown_includes_summary_table() -> None:
    markdown = render_comment_markdown(
        changed_files=["src/is_it_down/checkers/services/destiny.py"],
        selected_modules=["destiny"],
        results=[],
    )

    assert "| Service | Checker | Dependencies | Result |" in markdown
    assert "Changed service checker modules:" in markdown


def test_selected_service_checker_classes_with_errors_for_unknown_module() -> None:
    changed_files = ["src/is_it_down/checkers/services/does_not_exist.py"]
    selected, module_errors = selected_service_checker_classes_with_errors(changed_files)

    assert selected == []
    assert "does_not_exist" in module_errors


def test_render_comment_markdown_includes_verbose_non_up_logs_when_enabled() -> None:
    results = [
        CheckerExecutionResult(
            service_key="reddit",
            checker_class="is_it_down.checkers.services.reddit.RedditServiceChecker",
            official_uptime="https://www.redditstatus.com/",
            dependencies=["cloudflare"],
            changed_module="reddit",
            checks=[
                {
                    "check_key": "reddit_all_hot",
                    "status": "degraded",
                    "http_status": 403,
                    "latency_ms": 120,
                    "error_code": None,
                    "error_message": None,
                    "metadata": {"debug": {"body_preview": "blocked", "status_code": 403}},
                }
            ],
            error=None,
        )
    ]

    markdown = render_comment_markdown(
        changed_files=["src/is_it_down/checkers/services/reddit.py"],
        selected_modules=["reddit"],
        results=results,
        verbose=True,
    )

    assert "Verbose non-up check logs (1)" in markdown
    assert '"status": "degraded"' in markdown
    assert '"http_status": 403' in markdown
