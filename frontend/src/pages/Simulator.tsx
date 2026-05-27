import { useState } from "react";
import { Link } from "react-router-dom";
import { simulate } from "../api";
import Badge from "../components/Badge";
import type { Channel, Message, Ticket } from "../types";

const CHANNELS: Channel[] = ["whatsapp", "teams", "telegram", "zendesk"];

export default function Simulator() {
  const [channel, setChannel] = useState<Channel>("whatsapp");
  const [clientId, setClientId] = useState("demo-client");
  const [text, setText] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [busy, setBusy] = useState(false);

  async function send() {
    if (!text.trim()) return;
    const clientMessage: Message = {
      id: Date.now(), ticket_id: "", role: "client", text, channel,
      created_at: new Date().toISOString(),
    };
    setMessages((current) => [...current, clientMessage]);
    setText("");
    setBusy(true);
    try {
      const response = await simulate(channel, clientId, clientMessage.text);
      setMessages((current) => [...current, {
        id: Date.now() + 1, ticket_id: response.ticket.ticket_id, role: "agent",
        text: response.reply, channel, created_at: new Date().toISOString(),
      }]);
      setTicket(response.ticket);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <h2 className="page-title">Simulator</h2>
      <div className="toolbar">
        <select value={channel} onChange={(event) => setChannel(event.target.value as Channel)}>
          {CHANNELS.map((option) => <option key={option} value={option}>{option}</option>)}
        </select>
        <input value={clientId} onChange={(event) => setClientId(event.target.value)} placeholder="client id" />
      </div>
      <div className="grid cols-2">
        <div className="card">
          <ChatPanel messages={messages} />
          <div className="row" style={{ marginTop: 12 }}>
            <input
              style={{ flex: 1 }}
              value={text}
              placeholder="Type as a client…"
              onChange={(event) => setText(event.target.value)}
              onKeyDown={(event) => { if (event.key === "Enter") send(); }}
            />
            <button disabled={busy} onClick={send}>Send</button>
          </div>
        </div>
        <div className="card">
          <h3>Created / updated ticket</h3>
          {ticket ? (
            <dl className="kv">
              <dt>ID</dt><dd><Link to={`/tickets/${ticket.ticket_id}`}>{ticket.ticket_id.slice(0, 8)}</Link></dd>
              <dt>Category</dt><dd><Badge value={ticket.category} /></dd>
              <dt>Priority</dt><dd><Badge value={ticket.priority} /></dd>
              <dt>Sentiment</dt><dd><Badge value={ticket.sentiment} /></dd>
              <dt>Escalation</dt><dd><Badge value={ticket.escalation_target} /></dd>
              <dt>Resolved by AI</dt><dd><Badge value={ticket.resolved_by_ai} /></dd>
            </dl>
          ) : <div className="muted">Send a message to see the ticket.</div>}
        </div>
      </div>
    </div>
  );
}

function ChatPanel({ messages }: { messages: Message[] }) {
  return (
    <div className="chat">
      {messages.map((message) => (
        <div key={message.id} className={`bubble ${message.role}`}>{message.text}</div>
      ))}
      {messages.length === 0 && <div className="muted">Start a conversation.</div>}
    </div>
  );
}
