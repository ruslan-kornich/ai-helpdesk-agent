import pytest

from app.channels.zendesk import (
    ZendeskInbound,
    ZendeskTicketFields,
    build_reply_payload,
    parse_inbounds,
)
from app.channels.zendesk_poller import ZendeskPoller, is_new_comment, map_ticket_fields
from app.models.enums import Category, Channel, EscalationTarget, Priority, Sentiment
from app.models.ticket import Ticket


def test_parse_inbounds_maps_fields_and_preserves_order():
    tickets = [{"id": 100, "requester_id": 7}]
    comments_by_ticket = {
        "100": [
            {"id": 1, "author_id": 7, "body": "client msg"},
            {"id": 2, "author_id": 9, "body": "agent msg"},
        ]
    }
    inbounds = parse_inbounds(tickets, comments_by_ticket)
    assert len(inbounds) == 2
    assert inbounds[0].zendesk_ticket_id == "100"
    assert inbounds[0].requester_id == "7"
    assert inbounds[0].comment_id == "1"
    assert inbounds[0].author_id == "7"
    assert inbounds[0].text == "client msg"
    assert inbounds[1].author_id == "9"


def test_build_reply_payload_shape():
    fields = ZendeskTicketFields(
        priority="high", tags=["ai-helpdesk-agent", "cat_billing"], status="open"
    )
    payload = build_reply_payload("hello", fields)
    assert payload["ticket"]["comment"]["body"] == "hello"
    assert payload["ticket"]["comment"]["public"] is True
    assert payload["ticket"]["priority"] == "high"
    assert payload["ticket"]["status"] == "open"
    assert payload["ticket"]["tags"] == ["ai-helpdesk-agent", "cat_billing"]


def _ticket(**overrides) -> Ticket:
    base = dict(
        channel=Channel.ZENDESK,
        client_id="r1",
        category=Category.BILLING,
        priority=Priority.HIGH,
        summary="s",
        conversation_snippet="",
        escalation_target=EscalationTarget.FINANCE,
        resolved_by_ai=False,
        sentiment=Sentiment.NEUTRAL,
        ticket_metadata={},
    )
    base.update(overrides)
    return Ticket(**base)


def test_is_new_comment_no_metadata():
    assert is_new_comment(None, "10") is True


def test_is_new_comment_no_cursor():
    assert is_new_comment({"zendesk_ticket_id": "1"}, "10") is True


def test_is_new_comment_newer():
    assert is_new_comment({"last_seen_comment_id": "5"}, "10") is True


def test_is_new_comment_already_seen():
    assert is_new_comment({"last_seen_comment_id": "10"}, "10") is False
    assert is_new_comment({"last_seen_comment_id": "10"}, "9") is False


def test_map_ticket_fields_escalated():
    fields = map_ticket_fields(_ticket())
    assert fields.priority == "high"
    assert fields.status == "open"
    assert "cat_billing" in fields.tags
    assert "esc_finance" in fields.tags
    assert "ai-helpdesk-agent" in fields.tags


def test_map_ticket_fields_resolved():
    fields = map_ticket_fields(
        _ticket(
            resolved_by_ai=True,
            escalation_target=None,
            category=Category.HOW_TO,
            priority=Priority.NORMAL,
        )
    )
    assert fields.status == "solved"
    assert all(not tag.startswith("esc_") for tag in fields.tags)


class _FakeChannel:
    def __init__(self, inbounds):
        self._inbounds = inbounds

    async def fetch_new_comments(self, since):
        return self._inbounds


async def _noop_handler(inbound):
    return None


@pytest.mark.asyncio
async def test_poll_processes_only_requester_comments():
    inbounds = [
        ZendeskInbound("100", "7", "1", "7", "client msg"),
        ZendeskInbound("100", "7", "2", "9", "agent msg"),
    ]
    handled = []

    async def handler(inbound):
        handled.append(inbound)

    poller = ZendeskPoller(_FakeChannel(inbounds), handler, interval_seconds=1)
    await poller.poll_once()
    assert [inbound.comment_id for inbound in handled] == ["1"]


@pytest.mark.asyncio
async def test_poll_advances_watermark():
    poller = ZendeskPoller(_FakeChannel([]), _noop_handler, interval_seconds=1)
    before = poller.watermark
    await poller.poll_once()
    assert poller.watermark >= before
