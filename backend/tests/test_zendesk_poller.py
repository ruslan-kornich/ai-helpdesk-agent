from app.channels.zendesk import (
    ZendeskInbound,
    ZendeskTicketFields,
    build_reply_payload,
    parse_inbounds,
)


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
    fields = ZendeskTicketFields(priority="high", tags=["ai-helpdesk-agent", "cat_billing"], status="open")
    payload = build_reply_payload("hello", fields)
    assert payload["ticket"]["comment"]["body"] == "hello"
    assert payload["ticket"]["comment"]["public"] is True
    assert payload["ticket"]["priority"] == "high"
    assert payload["ticket"]["status"] == "open"
    assert payload["ticket"]["tags"] == ["ai-helpdesk-agent", "cat_billing"]
