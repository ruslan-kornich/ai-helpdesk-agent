from app.models.enums import Channel, MessageRole
from app.models.message import Message
from app.services.ticket_service import build_snippet


def _message(role: MessageRole, text: str) -> Message:
    return Message(ticket_id="t1", role=role, text=text, channel=Channel.TELEGRAM)


def test_build_snippet_orders_and_labels_roles():
    messages = [
        _message(MessageRole.CLIENT, "hello"),
        _message(MessageRole.AGENT, "hi there"),
        _message(MessageRole.CLIENT, "i have a question"),
    ]
    snippet = build_snippet(messages)
    assert "client: hello" in snippet
    assert "agent: hi there" in snippet
    assert snippet.index("client: hello") < snippet.index("agent: hi there")


def test_build_snippet_caps_messages():
    messages = [_message(MessageRole.CLIENT, f"msg {index}") for index in range(20)]
    snippet = build_snippet(messages, max_messages=10)
    assert snippet.count("\n") == 9
