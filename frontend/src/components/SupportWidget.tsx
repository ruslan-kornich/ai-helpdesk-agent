import { Bot, MessageCircle, SendHorizontal, X } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { fetchSupportReplies, startSupportChat } from "../api";
import type { Message, SupportMessage } from "../types";
import ChatWindow from "./ChatWindow";

const STORAGE_KEY = "support_chat";
const POLL_INTERVAL_MS = 3000;
const POLL_TIMEOUT_MS = 90000;

interface ChatState {
  name: string;
  email: string;
  started: boolean;
  zendeskTicketId: string | null;
  lastSeenId: number;
  messages: Message[];
}

const EMPTY: ChatState = {
  name: "",
  email: "",
  started: false,
  zendeskTicketId: null,
  lastSeenId: 0,
  messages: [],
};

function loadState(): ChatState | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as ChatState) : null;
  } catch {
    return null;
  }
}

function toMessage(reply: SupportMessage): Message {
  return {
    id: reply.id,
    ticket_id: "",
    role: reply.role,
    text: reply.text,
    channel: "zendesk",
    created_at: reply.created_at,
  };
}

export default function SupportWidget({ openSignal = 0 }: { openSignal?: number }) {
  const stored = useMemo(loadState, []);
  const [open, setOpen] = useState(false);
  const [chat, setChat] = useState<ChatState>(stored ?? EMPTY);
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [awaiting, setAwaiting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const localIdRef = useRef(
    (stored?.messages ?? []).reduce((min, message) => Math.min(min, message.id), 0),
  );
  const lastSeenRef = useRef(stored?.lastSeenId ?? 0);
  const pollTimer = useRef<number | null>(null);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(chat));
  }, [chat]);

  useEffect(() => {
    if (openSignal > 0) setOpen(true);
  }, [openSignal]);

  function stopPolling() {
    if (pollTimer.current !== null) {
      window.clearTimeout(pollTimer.current);
      pollTimer.current = null;
    }
  }

  function applyReplies(replies: SupportMessage[]) {
    const maxId = Math.max(lastSeenRef.current, ...replies.map((reply) => reply.id));
    lastSeenRef.current = maxId;
    setChat((prev) => ({
      ...prev,
      lastSeenId: maxId,
      messages: [...prev.messages, ...replies.map(toMessage)],
    }));
  }

  // Catch up on replies that arrived while the page was closed.
  useEffect(() => {
    if (!chat.started || !chat.zendeskTicketId) return;
    fetchSupportReplies(chat.zendeskTicketId, lastSeenRef.current)
      .then(({ messages }) => {
        if (messages.length > 0) applyReplies(messages);
      })
      .catch(() => undefined);
    return stopPolling;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function startPolling(ticketId: string) {
    stopPolling();
    const deadline = Date.now() + POLL_TIMEOUT_MS;
    const tick = async () => {
      try {
        const { messages: replies } = await fetchSupportReplies(ticketId, lastSeenRef.current);
        if (replies.length > 0) {
          applyReplies(replies);
          setAwaiting(false);
          stopPolling();
          return;
        }
      } catch {
        // Transient error — keep polling until the deadline.
      }
      if (Date.now() < deadline) {
        pollTimer.current = window.setTimeout(tick, POLL_INTERVAL_MS);
      } else {
        setAwaiting(false);
        stopPolling();
      }
    };
    pollTimer.current = window.setTimeout(tick, POLL_INTERVAL_MS);
  }

  function handleStart() {
    if (!chat.name.trim() || !chat.email.includes("@")) {
      setError("Please enter your name and a valid email.");
      return;
    }
    setError(null);
    setChat((prev) => ({ ...prev, started: true }));
  }

  async function handleSend() {
    const trimmed = text.trim();
    if (!trimmed || busy) return;
    setText("");
    setError(null);
    localIdRef.current -= 1;
    const clientMessage: Message = {
      id: localIdRef.current,
      ticket_id: "",
      role: "client",
      text: trimmed,
      channel: "zendesk",
      created_at: new Date().toISOString(),
    };
    const ticketId = chat.zendeskTicketId ?? undefined;
    setChat((prev) => ({ ...prev, messages: [...prev.messages, clientMessage] }));
    setBusy(true);
    setAwaiting(true);
    try {
      const { zendesk_ticket_id } = await startSupportChat(
        chat.name, chat.email, trimmed, ticketId,
      );
      setChat((prev) => ({ ...prev, zendeskTicketId: zendesk_ticket_id }));
      startPolling(zendesk_ticket_id);
    } catch {
      setAwaiting(false);
      setError("Couldn't send your message. Please try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="fixed bottom-5 right-5 z-50">
      {!open && (
        <button
          onClick={() => setOpen(true)}
          aria-label="Open support chat"
          className="btn brand-fill h-14 w-14 !p-0 text-white shadow-[var(--shadow-lift)]"
        >
          <MessageCircle size={24} strokeWidth={2.2} />
        </button>
      )}

      {open && (
        <div className="card animate-rise flex h-[560px] max-h-[calc(100dvh-2.5rem)] w-[380px] max-w-[calc(100vw-2.5rem)] flex-col overflow-hidden !p-0">
          <div className="brand-fill flex items-center justify-between px-5 py-4 text-white">
            <div className="flex items-center gap-2.5">
              <span className="grid h-9 w-9 place-items-center rounded-full bg-white/20">
                <Bot size={18} strokeWidth={2.3} />
              </span>
              <div>
                <div className="font-display text-[15px] font-bold">Support</div>
                <div className="text-[11px] text-white/85">Typically replies in under a minute</div>
              </div>
            </div>
            <button
              onClick={() => setOpen(false)}
              aria-label="Minimize chat"
              className="grid h-8 w-8 place-items-center rounded-full transition-colors hover:bg-white/15"
            >
              <X size={18} strokeWidth={2.3} />
            </button>
          </div>

          {!chat.started ? (
            <div className="flex flex-1 flex-col justify-center gap-4 p-6">
              <div>
                <h3 className="font-display text-lg font-bold text-ink">Let's get started</h3>
                <p className="mt-1 text-sm text-muted">
                  Tell us who you are and our assistant will help right away.
                </p>
              </div>
              <input
                className="field"
                placeholder="Your name"
                value={chat.name}
                onChange={(event) => setChat((prev) => ({ ...prev, name: event.target.value }))}
              />
              <input
                className="field"
                type="email"
                placeholder="Email"
                value={chat.email}
                onChange={(event) => setChat((prev) => ({ ...prev, email: event.target.value }))}
              />
              {error && <p className="text-[13px] text-danger">{error}</p>}
              <button
                className="btn btn-gradient"
                disabled={!chat.name.trim() || !chat.email.includes("@")}
                onClick={handleStart}
              >
                Start chat
              </button>
            </div>
          ) : (
            <>
              <div className="min-h-0 flex-1 px-4 pt-4">
                <ChatWindow
                  messages={chat.messages}
                  heightClass="h-full"
                  emptyText="Ask us anything — our assistant is here to help."
                />
              </div>
              {awaiting && (
                <div className="flex items-center gap-2 px-5 pb-1 text-[12px] text-muted">
                  <span className="flex gap-1">
                    <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-violet [animation-delay:-0.2s]" />
                    <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-sky [animation-delay:-0.1s]" />
                    <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-mint" />
                  </span>
                  Assistant is typing…
                </div>
              )}
              {error && <p className="px-5 pb-1 text-[12px] text-danger">{error}</p>}
              <div className="flex items-center gap-2 border-t border-line p-3">
                <input
                  className="flex-1 bg-transparent px-2 text-sm outline-none placeholder:text-muted"
                  placeholder="Type your message…"
                  value={text}
                  onChange={(event) => setText(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter") handleSend();
                  }}
                />
                <button
                  className="btn btn-dark h-10 w-10 !p-0"
                  disabled={busy || !text.trim()}
                  onClick={handleSend}
                >
                  <SendHorizontal size={17} strokeWidth={2.3} />
                </button>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
