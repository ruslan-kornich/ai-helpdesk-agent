import asyncio
import sys

from app.config.db import build_database_manager
from app.config.logger import setup_logging
from app.repositories.ticket_repository import TicketRepository
from app.schemas.analytics import AnalyticsReport
from app.services.analytics_service import AnalyticsService


def _format_report(report: AnalyticsReport) -> str:
    lines = [
        "=== ai-helpdesk-agent analytics ===",
        f"Total tickets: {report.total_tickets}",
        f"AI resolution rate: {report.ai_resolution_rate:.0%}",
        f"Escalation rate: {report.escalation_rate:.0%}",
        f"After-hours volume: {report.after_hours_volume}",
        "",
        "By channel:",
        *[f"  {channel}: {count}" for channel, count in sorted(report.by_channel.items())],
        "By category:",
        *[f"  {category}: {count}" for category, count in sorted(report.by_category.items())],
        "Sentiment:",
        *[f"  {sentiment}: {count}" for sentiment, count in sorted(report.sentiment_distribution.items())],
        "By day:",
        *[f"  {bucket.date}: {bucket.count}" for bucket in report.by_day],
    ]
    return "\n".join(lines)


async def _run_report() -> None:
    manager = build_database_manager()
    async with manager.session_factory() as session:
        service = AnalyticsService(TicketRepository(session))
        report = await service.build_report()
    await manager.dispose()
    print(_format_report(report))


def main() -> None:
    setup_logging()
    command = sys.argv[1] if len(sys.argv) > 1 else "report"
    if command == "report":
        asyncio.run(_run_report())
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
