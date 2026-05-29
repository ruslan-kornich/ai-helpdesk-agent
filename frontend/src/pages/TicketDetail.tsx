import { ArrowLeft, Braces, FileText, MessagesSquare, Ticket as TicketIcon, User } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { fetchMessages, fetchTicket } from "../api";
import Badge from "../components/Badge";
import ChatWindow from "../components/ChatWindow";
import type { Message, Ticket } from "../types";

const PAGE_SIZE = 20;

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-4 border-b border-line py-2.5 last:border-0">
      <dt className="text-[13px] font-medium text-muted">{label}</dt>
      <dd className="text-right text-[13px] font-semibold">{children}</dd>
    </div>
  );
}

export default function TicketDetail() {
  const { ticketId } = useParams();
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);

  useEffect(() => {
    if (!ticketId) return;
    fetchTicket(ticketId).then(setTicket);
  }, [ticketId]);

  useEffect(() => {
    if (!ticketId) return;
    fetchMessages(ticketId, page, PAGE_SIZE).then((result) => {
      setMessages((current) => (page === 1 ? result.items : [...current, ...result.items]));
      setPages(result.pages || 1);
    });
  }, [ticketId, page]);

  if (!ticket) return <div className="py-20 text-center text-sm text-muted">Loading…</div>;

  return (
    <div className="mx-auto max-w-[1180px]">
      <Link to="/" className="mb-5 inline-flex items-center gap-1.5 text-[13px] font-semibold text-muted transition-colors hover:text-ink">
        <ArrowLeft size={15} strokeWidth={2.4} /> Back to tickets
      </Link>

      <header className="mb-7 flex flex-wrap items-center gap-3.5">
        <span className="brand-fill grid h-11 w-11 place-items-center rounded-2xl text-white shadow-[var(--shadow-lift)]">
          <TicketIcon size={21} strokeWidth={2.3} />
        </span>
        <div>
          <h1 className="font-display text-[1.7rem] font-extrabold leading-none">
            Ticket <span className="font-mono text-[#7c43c4]">#{ticket.ticket_id.slice(0, 8)}</span>
          </h1>
          <p className="mt-1.5 flex items-center gap-1.5 text-sm text-muted">
            <User size={14} strokeWidth={2.2} /> {ticket.client_id}
          </p>
        </div>
      </header>

      <div className="grid gap-5 lg:grid-cols-2">
        <div className="flex flex-col gap-5">
          <div className="card p-5">
            <div className="mb-3 flex items-center gap-2 text-[12px] font-bold uppercase tracking-wider text-muted">
              <FileText size={14} strokeWidth={2.3} /> Summary
            </div>
            <p className="text-[15px] leading-relaxed">{ticket.summary}</p>
          </div>

          <div className="card p-5">
            <div className="mb-2 flex items-center gap-2 text-[12px] font-bold uppercase tracking-wider text-muted">
              <TicketIcon size={14} strokeWidth={2.3} /> Attributes
            </div>
            <dl>
              <Field label="Channel"><Badge value={ticket.channel} /></Field>
              <Field label="Category"><Badge value={ticket.category} /></Field>
              <Field label="Priority"><Badge value={ticket.priority} /></Field>
              <Field label="Sentiment"><Badge value={ticket.sentiment} /></Field>
              <Field label="Escalation"><Badge value={ticket.escalation_target} /></Field>
              <Field label="Resolution"><Badge value={ticket.resolved_by_ai} /></Field>
            </dl>
          </div>

          <div className="card p-5">
            <div className="mb-3 flex items-center gap-2 text-[12px] font-bold uppercase tracking-wider text-muted">
              <Braces size={14} strokeWidth={2.3} /> Metadata
            </div>
            <pre className="overflow-auto rounded-xl bg-[#1c1f27] p-4 font-mono text-[12px] leading-relaxed text-[#cdd3e0] scrollbar-slim">
              {JSON.stringify(ticket.ticket_metadata, null, 2)}
            </pre>
          </div>
        </div>

        <div className="card flex flex-col p-5">
          <div className="mb-4 flex items-center gap-2 text-[12px] font-bold uppercase tracking-wider text-muted">
            <MessagesSquare size={14} strokeWidth={2.3} /> Conversation
          </div>
          <ChatWindow messages={messages} />
          {page < pages && (
            <button className="btn btn-ghost mt-4 w-full" onClick={() => setPage(page + 1)}>
              Load older messages
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
