import { ChevronRight, Inbox } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import type { Ticket } from "../types";
import { CHANNEL_META } from "../ui/meta";
import Badge from "./Badge";

const HEADERS = ["Ticket", "Created", "Channel", "Category", "Priority", "Sentiment", "Escalation", "Summary", ""];

export default function TicketTable({ tickets }: { tickets: Ticket[] }) {
  const navigate = useNavigate();

  if (tickets.length === 0) {
    return (
      <div className="grid place-items-center gap-3 py-16 text-center">
        <span className="grid h-14 w-14 place-items-center rounded-2xl bg-surface-soft text-muted">
          <Inbox size={26} strokeWidth={1.8} />
        </span>
        <p className="text-sm font-semibold text-ink">No tickets yet</p>
        <p className="text-[13px] text-muted">Conversations will appear here as they arrive.</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto scrollbar-slim">
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr className="border-b border-line">
            {HEADERS.map((header, index) => (
              <th
                key={index}
                className="px-3 py-3 text-left text-[11px] font-bold uppercase tracking-wider text-muted"
              >
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {tickets.map((ticket) => {
            const channel = CHANNEL_META[ticket.channel];
            const ChannelIcon = channel?.icon;
            return (
              <tr
                key={ticket.ticket_id}
                onClick={() => navigate(`/tickets/${ticket.ticket_id}`)}
                className="group cursor-pointer border-b border-line/70 transition-colors hover:bg-surface-soft/60"
              >
                <td className="px-3 py-3">
                  <Link
                    to={`/tickets/${ticket.ticket_id}`}
                    className="rounded-lg bg-surface-soft px-2 py-1 font-mono text-[12px] font-semibold text-[#7c43c4] transition-colors group-hover:bg-violet-soft"
                  >
                    {ticket.ticket_id.slice(0, 8)}
                  </Link>
                </td>
                <td className="whitespace-nowrap px-3 py-3 text-[12px] text-muted">
                  {new Date(ticket.created_at).toLocaleString()}
                </td>
                <td className="px-3 py-3">
                  <span className="inline-flex items-center gap-2 font-medium text-ink-soft">
                    {ChannelIcon && (
                      <span className={`grid h-6 w-6 place-items-center rounded-lg badge-${channel.tone}`}>
                        <ChannelIcon size={13} strokeWidth={2.3} />
                      </span>
                    )}
                    {channel?.label ?? ticket.channel}
                  </span>
                </td>
                <td className="px-3 py-3"><Badge value={ticket.category} /></td>
                <td className="px-3 py-3"><Badge value={ticket.priority} /></td>
                <td className="px-3 py-3"><Badge value={ticket.sentiment} /></td>
                <td className="px-3 py-3"><Badge value={ticket.escalation_target} /></td>
                <td className="max-w-[260px] truncate px-3 py-3 text-[13px] text-ink-soft">
                  {ticket.summary}
                </td>
                <td className="px-3 py-3 text-right">
                  <Link
                    to={`/tickets/${ticket.ticket_id}`}
                    className="inline-grid h-7 w-7 place-items-center rounded-lg text-muted opacity-0 transition-opacity hover:bg-surface-soft group-hover:opacity-100"
                  >
                    <ChevronRight size={16} strokeWidth={2.4} />
                  </Link>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
