import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { fetchMessages, fetchTicket } from "../api";
import Badge from "../components/Badge";
import ChatWindow from "../components/ChatWindow";
import type { Message, Ticket } from "../types";

const PAGE_SIZE = 20;

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
      setMessages((current) => (page === 1 ? result.items : [...result.items, ...current]));
      setPages(result.pages || 1);
    });
  }, [ticketId, page]);

  if (!ticket) return <div className="muted">Loading…</div>;

  return (
    <div>
      <h2 className="page-title">Ticket {ticket.ticket_id.slice(0, 8)}</h2>
      <div className="grid cols-2">
        <div className="card">
          <dl className="kv">
            <dt>Channel</dt><dd><Badge value={ticket.channel} /></dd>
            <dt>Client</dt><dd>{ticket.client_id}</dd>
            <dt>Category</dt><dd><Badge value={ticket.category} /></dd>
            <dt>Priority</dt><dd><Badge value={ticket.priority} /></dd>
            <dt>Sentiment</dt><dd><Badge value={ticket.sentiment} /></dd>
            <dt>Escalation</dt><dd><Badge value={ticket.escalation_target} /></dd>
            <dt>Resolved by AI</dt><dd><Badge value={ticket.resolved_by_ai} /></dd>
            <dt>Summary</dt><dd>{ticket.summary}</dd>
            <dt>Metadata</dt><dd><pre className="muted">{JSON.stringify(ticket.ticket_metadata, null, 2)}</pre></dd>
          </dl>
        </div>
        <div className="card">
          {page < pages && (
            <button className="secondary" onClick={() => setPage(page + 1)}>Load older</button>
          )}
          <ChatWindow messages={messages} />
        </div>
      </div>
    </div>
  );
}
