import {
  ArrowUpRight,
  BarChart3,
  Bot,
  Bug,
  Check,
  Clock,
  Copy,
  ExternalLink,
  Headset,
  Info,
  ListChecks,
  type LucideIcon,
  Menu,
  MessageSquare,
  MessagesSquare,
  Rocket,
  Send,
  Settings2,
  Share2,
  Sparkles,
  Terminal,
  X,
} from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  CATEGORY_META,
  ESCALATION_META,
  type Meta,
  PRIORITY_META,
} from "../ui/meta";

const BOT_URL = "https://t.me/Gatum_support_llm_bot";
const BOT_HANDLE = "@Gatum_support_llm_bot";

type NavGroup = {
  group: string;
  items: { id: string; label: string; icon: LucideIcon }[];
};

const NAV: NavGroup[] = [
  {
    group: "Знайомство",
    items: [
      { id: "overview", label: "Огляд проєкту", icon: Info },
      { id: "channels", label: "Канали та інтеграції", icon: Share2 },
    ],
  },
  {
    group: "Запуск",
    items: [
      { id: "quickstart", label: "Швидкий старт", icon: Rocket },
      { id: "config", label: "Налаштування .env", icon: Settings2 },
    ],
  },
  {
    group: "Тестування",
    items: [
      { id: "scenarios", label: "8 сценаріїв", icon: ListChecks },
      { id: "phrases", label: "Тестові фрази", icon: MessageSquare },
      { id: "telegram", label: "Бот у Telegram", icon: Send },
      { id: "support-widget", label: "Віджет Zendesk", icon: Headset },
      { id: "debug", label: "DEBUG-логи", icon: Bug },
    ],
  },
  {
    group: "Результат",
    items: [{ id: "analytics", label: "Аналітичний звіт", icon: BarChart3 }],
  },
];

const SECTION_IDS = NAV.flatMap((group) => group.items.map((item) => item.id));

/* ── Primitives ─────────────────────────────────────────────── */

// Works on non-secure origins (e.g. http://0.0.0.0:8000) where
// navigator.clipboard is unavailable, by falling back to execCommand.
async function copyText(text: string): Promise<boolean> {
  if (navigator.clipboard && window.isSecureContext) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      // fall through to the legacy path
    }
  }
  try {
    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.top = "-9999px";
    textarea.style.opacity = "0";
    document.body.appendChild(textarea);
    textarea.select();
    const ok = document.execCommand("copy");
    document.body.removeChild(textarea);
    return ok;
  } catch {
    return false;
  }
}

function CodeBlock({ code }: { code: string }) {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    if (!(await copyText(code))) return;
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="relative my-3">
      <pre className="scrollbar-slim overflow-x-auto rounded-2xl bg-[#1d2029] p-4 pr-12 font-mono text-[13px] leading-relaxed text-[#e7e9f0]">
        <code>{code}</code>
      </pre>
      <button
        type="button"
        onClick={copy}
        aria-label="Скопіювати"
        className="absolute right-2.5 top-2.5 grid h-8 w-8 place-items-center rounded-lg bg-white/10 text-white/80 transition hover:bg-white/20 hover:text-white"
      >
        {copied ? <Check size={15} strokeWidth={2.4} /> : <Copy size={15} strokeWidth={2.2} />}
      </button>
    </div>
  );
}

function Code({ children }: { children: string }) {
  return (
    <code className="rounded-md bg-surface-soft px-1.5 py-0.5 font-mono text-[12.5px] text-[#7c43c4]">
      {children}
    </code>
  );
}

function CopyPhrase({ lang, text }: { lang: string; text: string }) {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    if (!(await copyText(text))) return;
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <button
      type="button"
      onClick={copy}
      className="group flex w-full items-start gap-3 rounded-2xl border border-line bg-surface-soft px-4 py-3 text-left transition hover:border-violet/40 hover:bg-violet-soft"
    >
      <span className="mt-px shrink-0 rounded-md bg-surface px-1.5 py-0.5 font-mono text-[10px] font-bold text-muted">
        {lang}
      </span>
      <span className="flex-1 text-[14.5px] leading-relaxed text-ink-soft">{text}</span>
      <span className="mt-0.5 shrink-0 text-muted transition group-hover:text-[#7c43c4]">
        {copied ? <Check size={15} strokeWidth={2.4} /> : <Copy size={15} strokeWidth={2.2} />}
      </span>
    </button>
  );
}

function MetaBadge({ meta }: { meta: Meta }) {
  const Icon = meta.icon;
  return (
    <span className={`badge badge-${meta.tone}`}>
      <Icon size={12} strokeWidth={2.4} />
      {meta.label}
    </span>
  );
}

function Section({
  id,
  icon: Icon,
  eyebrow,
  title,
  children,
}: {
  id: string;
  icon: LucideIcon;
  eyebrow: string;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section id={id} className="scroll-mt-24 pt-16 first:pt-0">
      <div className="mb-6 flex items-center gap-3">
        <span className="brand-fill grid h-10 w-10 shrink-0 place-items-center rounded-2xl text-white shadow-[var(--shadow-soft)]">
          <Icon size={19} strokeWidth={2.3} />
        </span>
        <div>
          <p className="text-[11px] font-bold uppercase tracking-wider text-muted">{eyebrow}</p>
          <h2 className="font-display text-2xl font-extrabold leading-tight text-ink">{title}</h2>
        </div>
      </div>
      <div className="space-y-5">{children}</div>
    </section>
  );
}

function CardTitle({ children }: { children: React.ReactNode }) {
  return <h3 className="font-display text-lg font-bold text-ink">{children}</h3>;
}

/* ── Data ───────────────────────────────────────────────────── */

type Scenario = {
  id: string;
  title: string;
  category: string;
  priority: string;
  escalation: Meta | "ai";
  reply: string;
  flags: string[];
  phrases: { lang: string; text: string }[];
};

const MORNING_QUEUE: Meta = {
  label: "Ранкова черга",
  icon: Clock,
  tone: "sky",
};

const SCENARIOS: Scenario[] = [
  {
    id: "C-1",
    title: "Як користуватися платформою",
    category: "how_to",
    priority: "normal",
    escalation: "ai",
    reply:
      "Покрокова інструкція з бази знань (FAQ) у відповідь на питання. Без ескалації — бот вирішує сам.",
    flags: ["resolved_by_ai = true"],
    phrases: [
      { lang: "UA", text: "Як мені відправити масову SMS-розсилку?" },
      { lang: "EN", text: "How do I send a bulk SMS campaign?" },
      { lang: "UA", text: "Де подивитися звіти про доставку?" },
      { lang: "UA", text: "Як зареєструвати Sender ID?" },
      { lang: "UA", text: "Як отримати API-ключі для відправлення повідомлень?" },
    ],
  },
  {
    id: "C-2",
    title: "Поповнення балансу",
    category: "billing",
    priority: "normal",
    escalation: ESCALATION_META.finance,
    reply:
      "Інструкція «Billing → Top up balance» + прохання прислати підтвердження транзакції. Реквізитів у відповіді немає.",
    flags: [],
    phrases: [
      { lang: "UA", text: "Як поповнити баланс? Дайте, будь ласка, реквізити для оплати." },
      { lang: "EN", text: "How can I top up my balance? What is the wallet address for payment?" },
    ],
  },
  {
    id: "C-3",
    title: "Недоставлені SMS",
    category: "delivery_issue",
    priority: "high",
    escalation: ESCALATION_META.l2_support,
    reply:
      "Підтверджує приймання, просить номер(и), час і Sender ID та передає структуровані дані в L2.",
    flags: ["entities → metadata"],
    phrases: [
      {
        lang: "UA",
        text: 'Мої SMS на номер +380501234567 о 14:30 не доставилися. Sender ID був "MyApp".',
      },
      {
        lang: "EN",
        text: 'My SMS to +380501234567 at 14:30 was not delivered. Sender ID was "MyApp".',
      },
    ],
  },
  {
    id: "C-4",
    title: "Поза робочим часом",
    category: "after_hours",
    priority: "normal",
    escalation: MORNING_QUEUE,
    reply:
      "Миттєве підтвердження: «отримали ваше повідомлення, відповімо в робочий час, тикет створено».",
    flags: ["was_after_hours = true"],
    phrases: [
      { lang: "UA", text: "У мене технічне питання щодо платформи." },
      { lang: "EN", text: "I have a technical question about the platform." },
    ],
  },
  {
    id: "C-5",
    title: "Ціни / комерція",
    category: "commercial",
    priority: "normal",
    escalation: ESCALATION_META.sales,
    reply:
      "Ввічливе підтвердження + «менеджер з продажів зв'яжеться найближчим часом». Конкретні ціни НЕ називає.",
    flags: [],
    phrases: [
      { lang: "UA", text: "Скільки коштує масова SMS-розсилка? Чи можна знижку за великий обсяг?" },
      { lang: "EN", text: "What is your pricing for bulk SMS? Can we get a discount for high volume?" },
    ],
  },
  {
    id: "C-6",
    title: "Збій / помилка API",
    category: "outage",
    priority: "urgent",
    escalation: ESCALATION_META.l2_support,
    reply:
      "Просить текст помилки, час і акаунт/IP, підтверджує терміновість і ескалює негайно (навіть уночі).",
    flags: ["entities → metadata"],
    phrases: [
      {
        lang: "UA",
        text: 'Впало SMPP-з\'єднання, помилка "bind_failed". IP 192.168.1.100, час 15:45, акаунт acme.',
      },
      {
        lang: "EN",
        text: 'Our SMPP connection keeps dropping. Error: "bind_failed". IP: 192.168.1.100. Time 15:45.',
      },
    ],
  },
  {
    id: "C-7",
    title: "Нерозпізнане повідомлення",
    category: "unknown",
    priority: "normal",
    escalation: ESCALATION_META.general_support,
    reply:
      "Ввічливе «передаю запит спеціалісту». Тикет із сирим текстом, відповідь не вигадується.",
    flags: ["raw text → ticket", "confidence < 0.55"],
    phrases: [
      { lang: "UA", text: "У чому сенс життя?" },
      { lang: "EN", text: "asdkjh qweqwe ???" },
      { lang: "CMD", text: "/start" },
    ],
  },
  {
    id: "C-8",
    title: "Скарга / негатив",
    category: "other",
    priority: "high",
    escalation: ESCALATION_META.support_lead,
    reply:
      "Розпізнає негатив, фіксує тикет з HIGH priority і сповіщає керівника підтримки (broadcast в адмінку).",
    flags: ["sentiment = negative"],
    phrases: [
      { lang: "UA", text: "Ваш сервіс жахливий! Я дуже розчарований якістю обслуговування." },
      {
        lang: "EN",
        text: "Your service is terrible! I'm so frustrated and disappointed with the platform.",
      },
    ],
  },
];

const ENV_VARS: { key: string; required: boolean; note: string }[] = [
  { key: "OPENAI_API_KEY", required: true, note: "Ключ для живих AI-відповідей. Без нього — детерміновані шаблони." },
  { key: "OPENAI_MODEL", required: false, note: "Модель класифікатора. За замовчуванням gpt-4.1." },
  { key: "TELEGRAM_BOT_TOKEN", required: false, note: "Токен від @BotFather. Без нього канал Telegram вимкнено." },
  { key: "ZENDESK_SUBDOMAIN / EMAIL / API_TOKEN", required: false, note: "Доступ до Zendesk для каналу /support. Без них Zendesk недоступний." },
  { key: "WORKING_HOURS_START / END", required: false, note: "Робоче вікно (9–18). Поза ним — сценарій after_hours." },
  { key: "TIMEZONE", required: false, note: "Таймзона робочого часу. За замовчуванням Europe/Kyiv." },
  { key: "SESSION_WINDOW_MINUTES", required: false, note: "Вікно склейки повідомлень в один тикет (30 хв)." },
  { key: "CONFIDENCE_THRESHOLD", required: false, note: "Нижче цього порога (0.55) → примусово unknown." },
];

/* ── Sidebar ────────────────────────────────────────────────── */

function NavLinks({
  activeId,
  onNavigate,
}: {
  activeId: string;
  onNavigate?: () => void;
}) {
  return (
    <nav className="space-y-7">
      {NAV.map((group) => (
        <div key={group.group}>
          <p className="mb-2 px-3 text-[11px] font-bold uppercase tracking-wider text-muted/80">
            {group.group}
          </p>
          <ul className="space-y-0.5">
            {group.items.map((item) => (
              <li key={item.id}>
                <a
                  href={`#${item.id}`}
                  onClick={onNavigate}
                  className={`doc-nav-link ${activeId === item.id ? "active" : ""}`}
                >
                  <item.icon size={15} strokeWidth={2.2} />
                  {item.label}
                </a>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </nav>
  );
}

/* ── Page ───────────────────────────────────────────────────── */

export default function Docs() {
  const [activeId, setActiveId] = useState(SECTION_IDS[0]);
  const [navOpen, setNavOpen] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (visible[0]) setActiveId(visible[0].target.id);
      },
      { rootMargin: "-20% 0px -70% 0px", threshold: 0 },
    );
    for (const id of SECTION_IDS) {
      const element = document.getElementById(id);
      if (element) observer.observe(element);
    }
    return () => observer.disconnect();
  }, []);

  return (
    <div className="mesh-bg min-h-dvh">
      <header className="sticky top-0 z-30 border-b border-line bg-surface/80 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-3 px-4 sm:px-6">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setNavOpen(true)}
              aria-label="Відкрити навігацію"
              className="grid h-9 w-9 place-items-center rounded-xl border border-line text-ink lg:hidden"
            >
              <Menu size={18} strokeWidth={2.3} />
            </button>
            <div className="flex items-center gap-2 font-display text-lg font-bold">
              <span className="brand-fill grid h-9 w-9 place-items-center rounded-xl text-white">
                <MessageSquare size={18} strokeWidth={2.4} />
              </span>
              <span className="brand-text">gatum</span>
              <span className="hidden text-sm font-semibold text-muted sm:inline">/ docs</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Link to="/support" className="btn btn-ghost hidden sm:inline-flex">
              <Headset size={16} strokeWidth={2.3} /> Підтримка
            </Link>
            <a
              href={BOT_URL}
              target="_blank"
              rel="noreferrer"
              className="btn btn-gradient"
            >
              <Send size={16} strokeWidth={2.3} /> Відкрити бота
            </a>
          </div>
        </div>
      </header>

      {/* Mobile drawer */}
      {navOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div
            className="absolute inset-0 bg-ink/30 backdrop-blur-sm"
            onClick={() => setNavOpen(false)}
          />
          <aside className="animate-rise absolute left-0 top-0 h-full w-72 overflow-y-auto border-r border-line bg-surface p-5">
            <div className="mb-6 flex items-center justify-between">
              <span className="font-display text-sm font-bold text-muted">Навігація</span>
              <button
                type="button"
                onClick={() => setNavOpen(false)}
                aria-label="Закрити"
                className="grid h-8 w-8 place-items-center rounded-lg text-muted hover:bg-surface-soft"
              >
                <X size={18} strokeWidth={2.3} />
              </button>
            </div>
            <NavLinks activeId={activeId} onNavigate={() => setNavOpen(false)} />
          </aside>
        </div>
      )}

      <div className="mx-auto flex max-w-7xl gap-10 px-4 sm:px-6">
        <aside className="scrollbar-slim sticky top-16 hidden h-[calc(100dvh-4rem)] w-60 shrink-0 overflow-y-auto py-10 lg:block">
          <NavLinks activeId={activeId} />
        </aside>

        <main className="min-w-0 flex-1 py-10 lg:max-w-3xl">
          {/* Hero */}
          <section className="animate-rise">
            <span className="badge badge-violet">
              <Sparkles size={12} strokeWidth={2.4} /> Документація · прототип
            </span>
            <h1 className="mt-4 font-display text-4xl font-extrabold leading-[1.1] text-ink sm:text-[44px]">
              Як <span className="brand-text">запустити</span> і протестувати агента
            </h1>
            <p className="mt-4 max-w-xl text-lg text-muted">
              Багатоканальний AI-агент підтримки Gatum: огляд, запуск, 8 сценаріїв і готові фрази
              для тестування в Telegram та через віджет Zendesk.
            </p>

            <div className="mt-7 grid gap-3 sm:grid-cols-3">
              <a
                href={BOT_URL}
                target="_blank"
                rel="noreferrer"
                className="card group flex items-center gap-3 p-4 transition hover:shadow-[var(--shadow-lift)]"
              >
                <span className="brand-fill grid h-10 w-10 shrink-0 place-items-center rounded-xl text-white">
                  <Send size={18} strokeWidth={2.3} />
                </span>
                <span className="min-w-0">
                  <span className="flex items-center gap-1 font-display text-sm font-bold text-ink">
                    Живий бот <ArrowUpRight size={14} className="text-muted transition group-hover:text-violet" />
                  </span>
                  <span className="block truncate text-xs text-muted">{BOT_HANDLE}</span>
                </span>
              </a>
              <Link
                to="/support"
                className="card group flex items-center gap-3 p-4 transition hover:shadow-[var(--shadow-lift)]"
              >
                <span className="bg-mint-soft grid h-10 w-10 shrink-0 place-items-center rounded-xl text-[#138a76]">
                  <Headset size={18} strokeWidth={2.3} />
                </span>
                <span className="min-w-0">
                  <span className="flex items-center gap-1 font-display text-sm font-bold text-ink">
                    Віджет Zendesk <ArrowUpRight size={14} className="text-muted transition group-hover:text-mint" />
                  </span>
                  <span className="block truncate text-xs text-muted">/support</span>
                </span>
              </Link>
              <a
                href="#phrases"
                className="card group flex items-center gap-3 p-4 transition hover:shadow-[var(--shadow-lift)]"
              >
                <span className="bg-sky-soft grid h-10 w-10 shrink-0 place-items-center rounded-xl text-[#2980b5]">
                  <ListChecks size={18} strokeWidth={2.3} />
                </span>
                <span className="min-w-0">
                  <span className="block font-display text-sm font-bold text-ink">Тестові фрази</span>
                  <span className="block truncate text-xs text-muted">8 сценаріїв · копіювання</span>
                </span>
              </a>
            </div>
          </section>

          {/* Overview */}
          <Section id="overview" icon={Info} eyebrow="Знайомство" title="Огляд проєкту">
            <div className="card p-6">
              <p className="text-[15px] leading-relaxed text-ink-soft">
                Багатоканальний AI-агент підтримки для платформи <strong>Gatum</strong> (SMS/SMPP).
                Він спілкується з клієнтами в кількох каналах, на кожну розмову створює
                структурований тикет, ескалює складні випадки до потрібної команди та рахує
                аналітику. У комплекті — React адмін-панель.
              </p>
              <div className="mt-4 inline-flex items-center gap-2 rounded-xl bg-warn/10 px-3 py-2 text-[13px] font-semibold text-[#b9791a]">
                <Info size={15} strokeWidth={2.3} />
                Це прототип тестового завдання, а не продакшн.
              </div>
            </div>

            <div className="card p-6">
              <CardTitle>Як це працює</CardTitle>
              <p className="mt-3 text-[15px] leading-relaxed text-ink-soft">
                Повідомлення з будь-якого каналу потрапляє у <Code>conversation_service</Code>, який
                веде сесію та тикет і викликає <Code>agent.pipeline</Code>:
              </p>
              <ol className="mt-4 space-y-2.5 text-[15px] text-ink-soft">
                {[
                  <>
                    <strong>analyzer</strong> — один структурований виклик GPT-4.1: класифікація +
                    витяг сутностей + тональність.
                  </>,
                  <>
                    <strong>router</strong> — чиста детермінована логіка: категорія → пріоритет,
                    ескалація, чи вирішено AI.
                  </>,
                  <>
                    <strong>responder + retriever</strong> — формує відповідь, для how_to підтягує
                    FAQ.
                  </>,
                ].map((text, index) => (
                  <li key={index} className="flex gap-3">
                    <span className="mt-0.5 grid h-6 w-6 shrink-0 place-items-center rounded-lg bg-violet-soft text-xs font-bold text-[#7c43c4]">
                      {index + 1}
                    </span>
                    <span>{text}</span>
                  </li>
                ))}
              </ol>
              <p className="mt-4 text-[15px] leading-relaxed text-ink-soft">
                Далі тикет зберігається у PostgreSQL, а оновлення транслюються в адмінку через
                WebSocket.
              </p>
            </div>

            <div className="card p-6">
              <CardTitle>Стек</CardTitle>
              <div className="mt-3 flex flex-wrap gap-2">
                {[
                  "FastAPI",
                  "async SQLAlchemy",
                  "PostgreSQL (asyncpg)",
                  "OpenAI structured outputs",
                  "React + Vite",
                  "Tailwind v4",
                  "WebSocket",
                ].map((item) => (
                  <span key={item} className="badge badge-neutral">
                    {item}
                  </span>
                ))}
              </div>
            </div>
          </Section>

          {/* Channels */}
          <Section
            id="channels"
            icon={Share2}
            eyebrow="Знайомство"
            title="Канали та інтеграції"
          >
            <p className="text-[15px] leading-relaxed text-ink-soft">
              За ТЗ агент підключений щонайменше до 2 із 4 каналів через <strong>реальні API</strong>.
              У прототипі це Telegram і Zendesk; решта каналів покрита симулятором в адмінці.
            </p>

            <div className="grid gap-4 sm:grid-cols-3">
              <div className="card p-5">
                <span className="bg-sky-soft grid h-10 w-10 place-items-center rounded-xl text-[#2980b5]">
                  <Send size={18} strokeWidth={2.3} />
                </span>
                <h3 className="mt-3 font-display text-base font-bold text-ink">Telegram</h3>
                <p className="mt-1.5 text-sm text-muted">
                  Реальний канал через long-polling бота. Живий бот уже піднятий — тестуй одразу.
                </p>
              </div>
              <div className="card p-5">
                <span className="bg-mint-soft grid h-10 w-10 place-items-center rounded-xl text-[#138a76]">
                  <Headset size={18} strokeWidth={2.3} />
                </span>
                <h3 className="mt-3 font-display text-base font-bold text-ink">Zendesk</h3>
                <p className="mt-1.5 text-sm text-muted">
                  Реальний канал через inbound-поллінг тикетів. Тестується через віджет на сторінці{" "}
                  <Code>/support</Code>.
                </p>
              </div>
              <div className="card p-5">
                <span className="bg-violet-soft grid h-10 w-10 place-items-center rounded-xl text-[#7c43c4]">
                  <MessagesSquare size={18} strokeWidth={2.3} />
                </span>
                <h3 className="mt-3 font-display text-base font-bold text-ink">Симулятор</h3>
                <p className="mt-1.5 text-sm text-muted">
                  Мок WhatsApp/Teams в адмінці для прогону всіх сценаріїв без зовнішніх API.
                </p>
              </div>
            </div>
          </Section>

          {/* Quick start */}
          <Section id="quickstart" icon={Rocket} eyebrow="Запуск" title="Швидкий старт">
            <div className="card p-6">
              <CardTitle>Вимоги</CardTitle>
              <ul className="mt-3 space-y-1.5 text-[15px] text-ink-soft">
                <li>• Docker + Docker Compose</li>
                <li>• (опційно, для локальної розробки) uv та Node.js 20+</li>
                <li>
                  • OpenAI API key — для живих AI-відповідей. Без нього застосунок теж працює:
                  відповіді падають на детерміновані шаблони.
                </li>
                <li>• (опційно) Telegram bot token і Zendesk trial-акаунт</li>
              </ul>
            </div>

            <div className="card p-6">
              <CardTitle>Запуск однією командою</CardTitle>
              <CodeBlock
                code={`cp .env.example .env        # заповни OPENAI_API_KEY (і за бажанням Telegram/Zendesk)
make run                    # docker compose up --build`}
              />
              <p className="text-[15px] leading-relaxed text-ink-soft">
                Відкрий <Code>http://localhost:8000</Code> — адмін-панель, REST API, WebSocket і
                (якщо заданий токен) Telegram-бот працюють в одному контейнері <Code>app</Code>.
                PostgreSQL піднімається окремим контейнером <Code>db</Code> з постійним volume.
              </p>
            </div>

            <div className="grid gap-4 lg:grid-cols-2">
              <div className="card min-w-0 p-6">
                <CardTitle>Корисні команди</CardTitle>
                <CodeBlock
                  code={`make report   # аналітика з CLI
make seed     # демо-тикети
make test     # юніт-тести`}
                />
              </div>
              <div className="card min-w-0 p-6">
                <CardTitle>Локальна розробка</CardTitle>
                <CodeBlock
                  code={`cd backend && uv sync \\
  && uv run uvicorn app.main:app --port 8000
cd frontend && npm i && npm run dev`}
                />
              </div>
            </div>
          </Section>

          {/* Config */}
          <Section id="config" icon={Settings2} eyebrow="Запуск" title="Налаштування .env">
            <p className="text-[15px] leading-relaxed text-ink-soft">
              Усі секрети та параметри читаються з environment variables — жодного хардкоду.
              Скопіюй <Code>.env.example</Code> у <Code>.env</Code> і заповни потрібне.
            </p>
            <div className="card overflow-hidden p-0">
              <div className="scrollbar-slim overflow-x-auto">
                <table className="w-full border-collapse text-left text-[14px]">
                  <thead>
                    <tr className="border-b border-line bg-surface-soft text-[12px] uppercase tracking-wide text-muted">
                      <th className="px-4 py-3 font-bold">Змінна</th>
                      <th className="px-4 py-3 font-bold">Обовʼязкова</th>
                      <th className="px-4 py-3 font-bold">Призначення</th>
                    </tr>
                  </thead>
                  <tbody>
                    {ENV_VARS.map((variable) => (
                      <tr key={variable.key} className="border-b border-line last:border-0">
                        <td className="px-4 py-3 align-top">
                          <code className="font-mono text-[12.5px] text-[#7c43c4]">{variable.key}</code>
                        </td>
                        <td className="px-4 py-3 align-top">
                          <span className={`badge ${variable.required ? "badge-warn" : "badge-neutral"}`}>
                            {variable.required ? "так" : "ні"}
                          </span>
                        </td>
                        <td className="px-4 py-3 align-top text-ink-soft">{variable.note}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </Section>

          {/* Scenarios */}
          <Section id="scenarios" icon={ListChecks} eyebrow="Тестування" title="8 сценаріїв підтримки">
            <p className="text-[15px] leading-relaxed text-ink-soft">
              Агент обробляє 7 обовʼязкових сценаріїв (C-1…C-7) плюс бонусний C-8 (розпізнавання
              негативної тональності). Кожен сценарій має фіксовані категорію, пріоритет і ціль
              ескалації.
            </p>
            <div className="card overflow-hidden p-0">
              <div className="scrollbar-slim overflow-x-auto">
                <table className="w-full border-collapse text-left text-[14px]">
                  <thead>
                    <tr className="border-b border-line bg-surface-soft text-[12px] uppercase tracking-wide text-muted">
                      <th className="px-4 py-3 font-bold">#</th>
                      <th className="px-4 py-3 font-bold">Тригер</th>
                      <th className="px-4 py-3 font-bold">Категорія</th>
                      <th className="px-4 py-3 font-bold">Пріоритет</th>
                      <th className="px-4 py-3 font-bold">Ескалація</th>
                    </tr>
                  </thead>
                  <tbody>
                    {SCENARIOS.map((scenario) => (
                      <tr key={scenario.id} className="border-b border-line last:border-0">
                        <td className="px-4 py-3 font-bold text-ink">{scenario.id}</td>
                        <td className="px-4 py-3 text-ink-soft">{scenario.title}</td>
                        <td className="px-4 py-3">
                          <MetaBadge meta={CATEGORY_META[scenario.category]} />
                        </td>
                        <td className="px-4 py-3">
                          <MetaBadge meta={PRIORITY_META[scenario.priority]} />
                        </td>
                        <td className="px-4 py-3">
                          {scenario.escalation === "ai" ? (
                            <span className="badge badge-pos">
                              <Sparkles size={12} strokeWidth={2.4} /> Вирішує AI
                            </span>
                          ) : (
                            <MetaBadge meta={scenario.escalation} />
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="card p-6">
              <CardTitle>Кілька важливих правил</CardTitle>
              <ul className="mt-3 space-y-2 text-[15px] text-ink-soft">
                <li>
                  • <strong>after_hours</strong>: робочий час Пн–Пт 09:00–18:00, таймзона{" "}
                  <Code>Europe/Kyiv</Code>. Сб/Нд — завжди поза робочим часом.
                </li>
                <li>
                  • <strong>Виняток для outage (C-6)</strong>: аварія завжди термінова — навіть уночі
                  не йде в after_hours.
                </li>
                <li>
                  • <strong>commercial (C-5)</strong>: бот ніколи не називає конкретних цін — лише
                  каже, що звʼяжеться менеджер з продажів.
                </li>
                <li>
                  • <strong>unknown (C-7)</strong>: спрацьовує і на безглузді повідомлення, і при
                  низькій впевненості класифікатора (<Code>confidence &lt; 0.55</Code>). Бот нічого
                  не вигадує.
                </li>
              </ul>
            </div>
          </Section>

          {/* Phrases */}
          <Section id="phrases" icon={MessageSquare} eyebrow="Тестування" title="Тестові фрази">
            <div className="card p-6">
              <CardTitle>Як тестувати</CardTitle>
              <ol className="mt-3 space-y-2 text-[15px] text-ink-soft">
                <li>1. Запусти проєкт (або відкрий живого бота — він уже працює).</li>
                <li>2. Надсилай повідомлення зі списку нижче — по одному.</li>
                <li>3. Після кожного дивись: відповідь бота + створений тикет в адмінці.</li>
                <li>4. Наприкінці запусти аналітику.</li>
              </ol>
              <div className="mt-4 space-y-2.5">
                <div className="rounded-xl bg-sky-soft px-4 py-3 text-[13.5px] text-[#2980b5]">
                  <strong>Про сесії:</strong> повідомлення від одного клієнта в межах{" "}
                  <Code>SESSION_WINDOW_MINUTES</Code> (типово 30 хв) приклеюються до{" "}
                  <strong>одного</strong> тикета. Щоб кожен сценарій створив окремий тикет — тестуй з
                  різних акаунтів, чекай &gt;30 хв або чисти БД між прогонами.
                </div>
                <div className="rounded-xl bg-violet-soft px-4 py-3 text-[13.5px] text-[#7c43c4]">
                  <strong>Про мову:</strong> класифікатор мовонезалежний (укр/рос/англ). Готові
                  відповіді бота і FAQ — англійською. Натисни на фразу, щоб скопіювати.
                </div>
              </div>
            </div>

            <div className="space-y-4">
              {SCENARIOS.map((scenario) => (
                <div key={scenario.id} className="card p-6">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="badge badge-violet">{scenario.id}</span>
                    <h3 className="mr-auto font-display text-base font-bold text-ink">
                      {scenario.title}
                    </h3>
                    <MetaBadge meta={CATEGORY_META[scenario.category]} />
                    <MetaBadge meta={PRIORITY_META[scenario.priority]} />
                  </div>

                  <div className="mt-5 grid gap-4 lg:grid-cols-2">
                    {/* What you send */}
                    <div>
                      <div className="mb-2.5 flex items-center gap-2 text-[12px] font-bold uppercase tracking-wide text-muted">
                        <Send size={13} strokeWidth={2.4} /> Надіслати боту
                      </div>
                      <div className="space-y-2">
                        {scenario.phrases.map((phrase) => (
                          <CopyPhrase key={phrase.text} lang={phrase.lang} text={phrase.text} />
                        ))}
                      </div>
                    </div>

                    {/* What to expect */}
                    <div className="rounded-2xl border border-line bg-surface-soft/70 p-4">
                      <div className="flex items-center gap-2">
                        <span className="brand-fill grid h-7 w-7 place-items-center rounded-lg text-white">
                          <Bot size={14} strokeWidth={2.4} />
                        </span>
                        <span className="font-display text-[13px] font-bold text-ink">
                          Очікувана відповідь
                        </span>
                      </div>
                      <p className="mt-2.5 text-[14px] leading-relaxed text-ink-soft">
                        {scenario.reply}
                      </p>
                      <div className="mt-3.5 border-t border-line pt-3">
                        <p className="mb-2 text-[11px] font-bold uppercase tracking-wide text-muted">
                          Результат тикета
                        </p>
                        <div className="flex flex-wrap gap-1.5">
                          {scenario.escalation === "ai" ? (
                            <span className="badge badge-pos">
                              <Sparkles size={12} strokeWidth={2.4} /> Вирішує AI
                            </span>
                          ) : (
                            <MetaBadge meta={scenario.escalation} />
                          )}
                          {scenario.flags.map((flag) => (
                            <span
                              key={flag}
                              className="inline-flex items-center rounded-md border border-line bg-surface px-2 py-1 font-mono text-[11px] text-muted"
                            >
                              {flag}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Section>

          {/* Telegram */}
          <Section id="telegram" icon={Send} eyebrow="Тестування" title="Бот у Telegram">
            <div className="card overflow-hidden p-0">
              <div className="brand-fill flex flex-col gap-4 p-6 text-white sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-center gap-3">
                  <span className="grid h-12 w-12 shrink-0 place-items-center rounded-2xl bg-white/20">
                    <Bot size={24} strokeWidth={2.2} />
                  </span>
                  <div>
                    <div className="font-display text-lg font-bold">Живий бот уже працює</div>
                    <div className="font-mono text-sm text-white/85">{BOT_HANDLE}</div>
                  </div>
                </div>
                <a
                  href={BOT_URL}
                  target="_blank"
                  rel="noreferrer"
                  className="btn btn-dark shrink-0"
                >
                  Відкрити в Telegram <ExternalLink size={15} strokeWidth={2.3} />
                </a>
              </div>
              <div className="p-6">
                <ol className="space-y-2 text-[15px] text-ink-soft">
                  <li>1. Відкрий бота за посиланням вище і натисни «Start».</li>
                  <li>
                    2. Надсилай тестові фрази з розділу{" "}
                    <a href="#phrases" className="font-semibold text-[#7c43c4]">Тестові фрази</a>{" "}
                    — по одному повідомленню.
                  </li>
                  <li>3. Дивись відповідь бота в чаті та створений тикет в адмін-панелі.</li>
                </ol>
                <p className="mt-4 text-[14px] leading-relaxed text-muted">
                  Канал працює на long-polling, тож публічний URL не потрібен. Хочеш свого бота —
                  створи токен у <Code>@BotFather</Code> і поклади у <Code>TELEGRAM_BOT_TOKEN</Code>.
                </p>
              </div>
            </div>
          </Section>

          {/* Support widget */}
          <Section id="support-widget" icon={Headset} eyebrow="Тестування" title="Віджет Zendesk на /support">
            <div className="card p-6">
              <p className="text-[15px] leading-relaxed text-ink-soft">
                Сторінка <Code>/support</Code> — це публічний лендинг із чат-віджетом у правому
                нижньому куті. Він імітує клієнта Zendesk: повідомлення створює{" "}
                <strong>реальний тикет у Zendesk</strong> через inbound-loop, а відповіді агента
                поллінгом повертаються у віджет. Паралельно тикет видно в адмінці.
              </p>
              <Link to="/support" className="btn btn-gradient mt-5">
                <Headset size={16} strokeWidth={2.3} /> Відкрити сторінку підтримки
              </Link>
            </div>

            <div className="card p-6">
              <CardTitle>Як протестувати</CardTitle>
              <ol className="mt-3 space-y-2 text-[15px] text-ink-soft">
                <li>1. Переконайся, що задані <Code>ZENDESK_SUBDOMAIN/EMAIL/API_TOKEN</Code>.</li>
                <li>2. Відкрий <Code>/support</Code> і натисни «Chat with us».</li>
                <li>3. Введи імʼя та email, надішли будь-яку тестову фразу.</li>
                <li>4. Дочекайся відповіді у віджеті та перевір тикет у Zendesk + адмінці.</li>
              </ol>
              <div className="mt-4 rounded-xl bg-mint-soft px-4 py-3 text-[13.5px] text-[#138a76]">
                <strong>Якщо Zendesk не налаштований:</strong> канал вважається недоступним
                (лог-попередження, без падіння) — для швидкого тесту скористайся ботом у Telegram або
                симулятором.
              </div>
            </div>
          </Section>

          {/* Debug */}
          <Section id="debug" icon={Bug} eyebrow="Тестування" title="DEBUG-логи">
            <div className="card p-6">
              <p className="text-[15px] leading-relaxed text-ink-soft">
                Щоб бачити повний шлях повідомлення (що йде в OpenAI, відповідь/токени, рішення
                роутера, фінальну відповідь) — увімкни DEBUG у <Code>.env</Code> і перезапусти:
              </p>
              <CodeBlock code={`LOG_LEVEL=DEBUG`} />
              <p className="text-[14px] leading-relaxed text-muted">
                У логах по одному повідомленню видно ланцюжок:
              </p>
              <CodeBlock
                code={`Incoming message | channel=telegram client_id=... text='...'
Analyzer result  | category=... confidence=... sentiment=...
Router decision  | priority=... escalation_target=... resolved_by_ai=...
Agent reply      | '...'
Sending reply    | channel=telegram reply='...'`}
              />
              <p className="text-[14px] leading-relaxed text-muted">
                Для звичайного прогону поверни <Code>LOG_LEVEL=INFO</Code> — DEBUG логує повні
                промпти й тексти.
              </p>
            </div>

            <div className="card flex items-start gap-3 p-5">
              <span className="bg-surface-soft grid h-9 w-9 shrink-0 place-items-center rounded-xl text-muted">
                <Terminal size={17} strokeWidth={2.3} />
              </span>
              <div className="text-[14px] leading-relaxed text-ink-soft">
                <strong>Якщо щось не так:</strong> немає <Code>OpenAI ... request</Code> → перевір
                ключ/wiring; <Code>faq_chunks_found=0</Code> → FAQ не знайшов збігів; немає{" "}
                <Code>Telegram message sent</Code> → дивись <Code>Telegram send failed</Code>.
              </div>
            </div>
          </Section>

          {/* Analytics */}
          <Section id="analytics" icon={BarChart3} eyebrow="Результат" title="Аналітичний звіт">
            <div className="card p-6">
              <CardTitle>Підсумкова перевірка</CardTitle>
              <p className="mt-3 text-[15px] leading-relaxed text-ink-soft">
                Після прогону всіх сценаріїв запусти аналітику з CLI або через HTTP-ендпоінт.
              </p>
              <p className="mt-4 text-[13px] font-bold uppercase tracking-wide text-muted">CLI</p>
              <CodeBlock
                code={`make report
# або
python -m app.cli report`}
              />
              <p className="mt-2 text-[13px] font-bold uppercase tracking-wide text-muted">
                HTTP-ендпоінт (потрібна JWT-авторизація)
              </p>
              <CodeBlock code={`GET /api/analytics`} />
            </div>

            <div className="card p-6">
              <CardTitle>Що має бути у звіті</CardTitle>
              <ul className="mt-3 space-y-2 text-[15px] text-ink-soft">
                <li>• Всього тикетів (по каналах і по днях).</li>
                <li>
                  • Розподіл за категоріями (how_to, billing, delivery_issue, after_hours,
                  commercial, outage, unknown, other).
                </li>
                <li>• % ескалацій і % вирішених AI.</li>
                <li>• Розподіл тональності (positive / neutral / negative).</li>
                <li>• Обсяг after-hours тикетів.</li>
              </ul>
            </div>
          </Section>

          <footer className="mt-20 border-t border-line pt-8 text-sm text-muted">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <span>Gatum AI Helpdesk — прототип тестового завдання.</span>
              <div className="flex items-center gap-2">
                <a href={BOT_URL} target="_blank" rel="noreferrer" className="btn btn-ghost">
                  <Send size={15} strokeWidth={2.3} /> Бот
                </a>
                <Link to="/support" className="btn btn-ghost">
                  <Headset size={15} strokeWidth={2.3} /> /support
                </Link>
              </div>
            </div>
          </footer>
        </main>
      </div>
    </div>
  );
}
