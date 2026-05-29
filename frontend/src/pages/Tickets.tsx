import { ChevronLeft, ChevronRight, ListFilter, Ticket as TicketIcon } from "lucide-react";
import { useEffect, useState } from "react";
import { connectWebSocket, fetchTickets } from "../api";
import TicketTable from "../components/TicketTable";
import PageHeader from "../ui/PageHeader";
import type { Category, Channel, Ticket, TicketFilters } from "../types";

const PAGE_SIZE = 15;
const CHANNELS: Channel[] = ["telegram", "zendesk", "whatsapp", "teams"];
const CATEGORIES: Category[] = ["how_to", "billing", "delivery_issue", "after_hours", "commercial", "outage", "unknown", "other"];

export default function Tickets() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [filters, setFilters] = useState<TicketFilters>({});

  async function load() {
    const result = await fetchTickets(page, PAGE_SIZE, filters);
    setTickets(result.items);
    setPages(result.pages || 1);
    setTotal(result.total ?? result.items.length);
  }

  useEffect(() => {
    load();
  }, [page, filters]);

  useEffect(() => {
    const socket = connectWebSocket((data) => {
      const message = data as { type?: string };
      if (message.type === "ticket") load();
    });
    return () => socket.close();
  }, [page, filters]);

  function updateFilter(key: keyof TicketFilters, value: string) {
    setPage(1);
    setFilters((current) => ({ ...current, [key]: value || undefined }));
  }

  return (
    <div className="mx-auto max-w-[1180px]">
      <PageHeader
        icon={TicketIcon}
        title="Support"
        accent="tickets"
        subtitle="Every conversation, classified and routed in real time."
        actions={
          <span className="badge badge-violet h-9 gap-1.5 px-4 text-[12px]">
            <span className="h-2 w-2 animate-pulse rounded-full bg-[#7c43c4]" />
            Live · {total} total
          </span>
        }
      />

      <div className="card p-2.5">
        <div className="flex flex-wrap items-center gap-2.5 border-b border-line px-2 pb-3 pt-1">
          <span className="ml-1 inline-flex items-center gap-1.5 text-[13px] font-semibold text-muted">
            <ListFilter size={15} strokeWidth={2.3} /> Filter
          </span>
          <select className="field h-9 w-auto py-0" onChange={(event) => updateFilter("channel", event.target.value)}>
            <option value="">All channels</option>
            {CHANNELS.map((channel) => <option key={channel} value={channel}>{channel}</option>)}
          </select>
          <select className="field h-9 w-auto py-0" onChange={(event) => updateFilter("category", event.target.value)}>
            <option value="">All categories</option>
            {CATEGORIES.map((category) => <option key={category} value={category}>{category}</option>)}
          </select>
        </div>

        <TicketTable tickets={tickets} />

        <div className="flex items-center justify-between gap-3 px-3 py-3">
          <span className="text-[13px] text-muted">
            Page <span className="font-semibold text-ink">{page}</span> of {pages}
          </span>
          <div className="flex items-center gap-2">
            <button className="btn btn-ghost h-9 px-3.5" disabled={page <= 1} onClick={() => setPage(page - 1)}>
              <ChevronLeft size={16} strokeWidth={2.4} /> Prev
            </button>
            <button className="btn btn-ghost h-9 px-3.5" disabled={page >= pages} onClick={() => setPage(page + 1)}>
              Next <ChevronRight size={16} strokeWidth={2.4} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
