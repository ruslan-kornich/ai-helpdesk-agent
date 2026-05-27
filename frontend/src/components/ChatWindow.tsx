import { Bot, Info, User } from "lucide-react";
import type { Message } from "../types";

export default function ChatWindow({
  messages,
  emptyText = "No messages yet.",
}: {
  messages: Message[];
  emptyText?: string;
}) {
  return (
    <div className="flex max-h-[58vh] flex-col gap-4 overflow-auto px-1 py-1 scrollbar-slim">
      {messages.map((message) => {
        if (message.role === "system") {
          return (
            <div key={message.id} className="flex items-center justify-center gap-1.5 text-[12px] text-muted">
              <Info size={12} strokeWidth={2.2} />
              {message.text}
            </div>
          );
        }
        const isAgent = message.role === "agent";
        return (
          <div
            key={message.id}
            className={`flex items-end gap-2.5 ${isAgent ? "flex-row-reverse" : ""}`}
          >
            <span
              className={`grid h-8 w-8 shrink-0 place-items-center rounded-full ${
                isAgent ? "brand-fill text-white" : "bg-surface-soft text-ink-soft"
              }`}
            >
              {isAgent ? <Bot size={16} strokeWidth={2.2} /> : <User size={16} strokeWidth={2.2} />}
            </span>
            <div
              className={`max-w-[78%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                isAgent
                  ? "rounded-br-md bg-ink text-white"
                  : "rounded-bl-md border border-line bg-surface text-ink"
              }`}
            >
              {message.text}
            </div>
          </div>
        );
      })}
      {messages.length === 0 && (
        <div className="grid place-items-center gap-2 py-12 text-center text-sm text-muted">
          <Bot size={26} strokeWidth={1.8} className="text-line" />
          {emptyText}
        </div>
      )}
    </div>
  );
}
