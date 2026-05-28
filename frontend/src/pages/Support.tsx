import { Clock, MessageSquare, Sparkles, Zap } from "lucide-react";
import { useState } from "react";
import SupportWidget from "../components/SupportWidget";

const FEATURES = [
  {
    icon: Zap,
    title: "Instant answers",
    text: "Our AI assistant replies in seconds — billing, delivery, how-to and more.",
  },
  {
    icon: Clock,
    title: "Around the clock",
    text: "Support that never sleeps, weekends and holidays included.",
  },
  {
    icon: Sparkles,
    title: "Smart escalation",
    text: "Tricky cases are routed to the right human team automatically.",
  },
];

export default function Support() {
  const [openSignal, setOpenSignal] = useState(0);

  return (
    <div className="mesh-bg min-h-dvh">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <div className="flex items-center gap-2 font-display text-lg font-bold">
          <span className="brand-fill grid h-9 w-9 place-items-center rounded-xl text-white">
            <MessageSquare size={18} strokeWidth={2.4} />
          </span>
          <span className="brand-text">gatum</span>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6">
        <section className="animate-rise py-16 text-center sm:py-24">
          <span className="badge badge-violet mx-auto">
            <Sparkles size={12} strokeWidth={2.4} /> AI-powered support
          </span>
          <h1 className="mx-auto mt-5 max-w-3xl font-display text-4xl font-extrabold leading-tight text-ink sm:text-5xl">
            Help that feels <span className="brand-text">instant</span>.
          </h1>
          <p className="mx-auto mt-5 max-w-xl text-lg text-muted">
            Got a question about billing, delivery, or how things work? Chat with our
            assistant and get answers in seconds.
          </p>
          <button
            className="btn btn-gradient mx-auto mt-8"
            onClick={() => setOpenSignal((value) => value + 1)}
          >
            <MessageSquare size={17} strokeWidth={2.3} /> Chat with us
          </button>
        </section>

        <section className="grid gap-5 pb-28 sm:grid-cols-3">
          {FEATURES.map((feature) => (
            <div key={feature.title} className="card p-6 text-left">
              <span className="bg-violet-soft grid h-11 w-11 place-items-center rounded-2xl text-[#7c43c4]">
                <feature.icon size={20} strokeWidth={2.2} />
              </span>
              <h3 className="mt-4 font-display text-base font-bold text-ink">{feature.title}</h3>
              <p className="mt-1.5 text-sm text-muted">{feature.text}</p>
            </div>
          ))}
        </section>
      </main>

      <SupportWidget openSignal={openSignal} />
    </div>
  );
}
