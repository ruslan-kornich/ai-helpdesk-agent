import type { Message } from "../types";

export default function ChatWindow({
  messages,
  emptyText = "No messages.",
}: {
  messages: Message[];
  emptyText?: string;
}) {
  return (
    <div className="chat">
      {messages.map((message) => (
        <div key={message.id} className={`bubble ${message.role}`}>
          {message.text}
        </div>
      ))}
      {messages.length === 0 && <div className="muted">{emptyText}</div>}
    </div>
  );
}
