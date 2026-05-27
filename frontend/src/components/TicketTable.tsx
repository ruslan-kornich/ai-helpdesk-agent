import { Link } from "react-router-dom";
import type { Ticket } from "../types";
import Badge from "./Badge";

export default function TicketTable({ tickets }: { tickets: Ticket[] }) {
  return (
    <table>
      <thead>
        <tr>
          <th>ID</th><th>Created</th><th>Channel</th><th>Category</th>
          <th>Priority</th><th>Sentiment</th><th>Escalation</th><th>Summary</th>
        </tr>
      </thead>
      <tbody>
        {tickets.map((ticket) => (
          <tr key={ticket.ticket_id}>
            <td><Link to={`/tickets/${ticket.ticket_id}`}>{ticket.ticket_id.slice(0, 8)}</Link></td>
            <td className="muted">{new Date(ticket.created_at).toLocaleString()}</td>
            <td><Badge value={ticket.channel} /></td>
            <td><Badge value={ticket.category} /></td>
            <td><Badge value={ticket.priority} /></td>
            <td><Badge value={ticket.sentiment} /></td>
            <td><Badge value={ticket.escalation_target} /></td>
            <td>{ticket.summary}</td>
          </tr>
        ))}
        {tickets.length === 0 && (
          <tr><td colSpan={8} className="muted">No tickets yet.</td></tr>
        )}
      </tbody>
    </table>
  );
}
