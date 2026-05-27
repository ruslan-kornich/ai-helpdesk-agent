import { ArrowUpRight, ExternalLink, SendHorizontal, Sparkles, TerminalSquare } from "lucide-react";
import { useRef, useState } from "react";
import { Link } from "react-router-dom";
import { simulate } from "../api";
import Badge from "../components/Badge";
import ChatWindow from "../components/ChatWindow";
import { CHANNEL_META } from "../ui/meta";
import PageHeader from "../ui/PageHeader";
import type { Channel, Message, Ticket } from "../types";

const CHANNELS: Channel[] = ["whatsapp", "teams", "telegram", "zendesk"];

export default function Simulator() {
  const [channel, setChannel] = useState<Channel>("whatsapp");
  const [clientId, setClientId] = useState("demo-client");
  const [text, setText] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [busy, setBusy] = useState(false);
  const nextMessageId = useRef(0);

  async function send() {
    if (!text.trim()) return;
    const clientMessage: Message = {
      id: nextMessageId.current++, ticket_id: "", role: "client", text, channel,
      created_at: new Date().toISOString(),
    };
    setMessages((current) => [...current, clientMessage]);
    setText("");
    setBusy(true);
    try {
      const response = await simulate(channel, clientId, clientMessage.text);
      setMessages((current) => [...current, {
        id: nextMessageId.current++, ticket_id: response.ticket.ticket_id, role: "agent",
        text: response.reply, channel, created_at: new Date().toISOString(),
      }]);
      setTicket(response.ticket);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-[1180px]">
      <PageHeader
        icon={TerminalSquare}
        title="Channel"
        accent="simulator"
        subtitle="Play any scenario end-to-end without sending real messages."
      />

      <div className="mb-5 flex flex-wrap items-center gap-3">
        <div className="flex flex-wrap gap-2">
          {CHANNELS.map((option) => {
            const meta = CHANNEL_META[option];
            const Icon = meta.icon;
            const active = channel === option;
            return (
              <button
                key={option}
                onClick={() => setChannel(option)}
                className={[
                  "flex items-center gap-2 rounded-full border px-4 py-2 text-[13px] font-semibold transition-all",
                  active
                    ? "border-transparent bg-ink text-white shadow-[var(--shadow-lift)]"
                    : "border-line bg-surface text-muted hover:text-ink",
                ].join(" ")}
              >
                <Icon size={15} strokeWidth={2.3} />
                {meta.label}
              </button>
            );
          })}
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[13px] font-semibold text-muted">as</span>
          <input
            className="field h-9 w-44 py-0"
            value={clientId}
            onChange={(event) => setClientId(event.target.value)}
            placeholder="client id"
          />
        </div>
      </div>

      <div className="grid gap-5 lg:grid-cols-[1.3fr_1fr]">
        <div className="card flex flex-col p-5">
          <ChatWindow messages={messages} emptyText="Type a message to start the scenario." />
          <div className="mt-4 flex items-center gap-2 rounded-2xl border border-line bg-surface-soft p-1.5 pl-4">
            <input
              className="flex-1 bg-transparent text-sm outline-none placeholder:text-muted"
              value={text}
              placeholder="Type as a client…"
              onChange={(event) => setText(event.target.value)}
              onKeyDown={(event) => { if (event.key === "Enter") send(); }}
            />
            <button className="btn btn-dark h-10 w-10 !p-0" disabled={busy} onClick={send}>
              <SendHorizontal size={17} strokeWidth={2.3} />
            </button>
          </div>
        </div>

        <div className="card p-5">
          <div className="mb-4 flex items-center gap-2 text-[12px] font-bold uppercase tracking-wider text-muted">
            <Sparkles size={14} strokeWidth={2.3} /> Resulting ticket
          </div>
          {ticket ? (
            <div className="space-y-3.5">
              <Link
                to={`/tickets/${ticket.ticket_id}`}
                className="flex items-center justify-between rounded-2xl border border-line bg-surface-soft px-4 py-3 transition-colors hover:bg-violet-soft"
              >
                <span className="font-mono text-[13px] font-bold text-[#7c43c4]">
                  #{ticket.ticket_id.slice(0, 8)}
                </span>
                <ExternalLink size={15} strokeWidth={2.3} className="text-muted" />
              </Link>
              <div className="flex flex-wrap gap-2">
                <Badge value={ticket.category} />
                <Badge value={ticket.priority} />
                <Badge value={ticket.sentiment} />
                <Badge value={ticket.escalation_target} />
                <Badge value={ticket.resolved_by_ai} />
              </div>
            </div>
          ) : (
            <div className="grid place-items-center gap-2 py-12 text-center text-sm text-muted">
              <ArrowUpRight size={24} strokeWidth={1.8} className="text-line" />
              Send a message to see the created ticket.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
