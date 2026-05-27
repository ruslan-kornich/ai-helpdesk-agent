import type { Message } from "../types";

export default function ChatWindow({ messages }: { messages: Message[] }) {
  return (
    <div className="chat">
      {messages.map((message) => (
        <div key={message.id} className={`bubble ${message.role}`}>
          {message.text}
        </div>
      ))}
      {messages.length === 0 && <div className="muted">No messages.</div>}
    </div>
  );
}
