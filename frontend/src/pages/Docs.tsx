import {
  ArrowLeft,
  BarChart3,
  Bot,
  Check,
  Copy,
  FlaskConical,
  Info,
  ListChecks,
  type LucideIcon,
  MessageSquare,
  Rocket,
} from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";

type TabId = "overview" | "run" | "scenarios" | "testing" | "analytics";

const TABS: { id: TabId; label: string; icon: LucideIcon }[] = [
  { id: "overview", label: "Огляд", icon: Info },
  { id: "run", label: "Запуск", icon: Rocket },
  { id: "scenarios", label: "Сценарії", icon: ListChecks },
  { id: "testing", label: "Тестування", icon: FlaskConical },
  { id: "analytics", label: "Аналітика", icon: BarChart3 },
];

function CodeBlock({ code }: { code: string }) {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    await navigator.clipboard.writeText(code);
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

function SectionTitle({ children }: { children: React.ReactNode }) {
  return <h2 className="font-display text-xl font-bold text-ink">{children}</h2>;
}

function OverviewTab() {
  return (
    <div className="space-y-6">
      <div className="card p-6">
        <SectionTitle>Що це за проєкт</SectionTitle>
        <p className="mt-3 text-[15px] leading-relaxed text-ink-soft">
          Багатоканальний AI-агент підтримки для платформи <strong>Gatum</strong> (SMS/SMPP).
          Він спілкується з клієнтами в кількох каналах, на кожну розмову створює структурований
          тикет, ескалює складні випадки до потрібної команди та рахує аналітику. У комплекті —
          React адмін-панель.
        </p>
        <div className="mt-4 inline-flex items-center gap-2 rounded-xl bg-warn/10 px-3 py-2 text-[13px] font-semibold text-[#b9791a]">
          <Info size={15} strokeWidth={2.3} />
          Це прототип тестового завдання, а не продакшн.
        </div>
      </div>

      <div className="grid gap-5 sm:grid-cols-3">
        <div className="card p-5">
          <span className="badge badge-violet">Telegram</span>
          <p className="mt-2 text-sm text-muted">Реальний канал через long-polling бота.</p>
        </div>
        <div className="card p-5">
          <span className="badge badge-sky">Zendesk</span>
          <p className="mt-2 text-sm text-muted">Реальний канал через inbound-поллінг тикетів.</p>
        </div>
        <div className="card p-5">
          <span className="badge badge-mint">Симулятор</span>
          <p className="mt-2 text-sm text-muted">Мок WhatsApp/Teams для прогону всіх сценаріїв.</p>
        </div>
      </div>

      <div className="card p-6">
        <SectionTitle>Як це працює</SectionTitle>
        <p className="mt-3 text-[15px] leading-relaxed text-ink-soft">
          Повідомлення з будь-якого каналу потрапляє у <Code>conversation_service</Code>, який
          веде сесію та тикет і викликає <Code>agent.pipeline</Code>:
        </p>
        <ul className="mt-4 space-y-2.5 text-[15px] text-ink-soft">
          <li className="flex gap-3">
            <span className="mt-0.5 grid h-6 w-6 shrink-0 place-items-center rounded-lg bg-violet-soft text-xs font-bold text-[#7c43c4]">
              1
            </span>
            <span>
              <strong>analyzer</strong> — один структурований виклик GPT-4o: класифікація +
              витяг сутностей + тональність.
            </span>
          </li>
          <li className="flex gap-3">
            <span className="mt-0.5 grid h-6 w-6 shrink-0 place-items-center rounded-lg bg-violet-soft text-xs font-bold text-[#7c43c4]">
              2
            </span>
            <span>
              <strong>router</strong> — чиста детермінована логіка: категорія → пріоритет,
              ескалація, чи вирішено AI.
            </span>
          </li>
          <li className="flex gap-3">
            <span className="mt-0.5 grid h-6 w-6 shrink-0 place-items-center rounded-lg bg-violet-soft text-xs font-bold text-[#7c43c4]">
              3
            </span>
            <span>
              <strong>responder + retriever</strong> — формує відповідь, для how_to підтягує
              FAQ.
            </span>
          </li>
        </ul>
        <p className="mt-4 text-[15px] leading-relaxed text-ink-soft">
          Далі тикет зберігається у PostgreSQL, а оновлення транслюються в адмінку через
          WebSocket.
        </p>
      </div>

      <div className="card p-6">
        <SectionTitle>Стек</SectionTitle>
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
    </div>
  );
}

function RunTab() {
  return (
    <div className="space-y-6">
      <div className="card p-6">
        <SectionTitle>Вимоги</SectionTitle>
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
        <SectionTitle>Запуск однією командою</SectionTitle>
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

      <div className="card p-6">
        <SectionTitle>Корисні команди</SectionTitle>
        <CodeBlock
          code={`make report   # аналітика з CLI
make seed     # завантажити демо-тикети
make test     # юніт-тести (на хості)`}
        />
      </div>

      <div className="card p-6">
        <SectionTitle>Локальна розробка (без Docker)</SectionTitle>
        <CodeBlock
          code={`cd backend && uv sync && uv run uvicorn app.main:app --port 8000
cd frontend && npm install && npm run dev    # :5173 з проксі на :8000`}
        />
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <div className="card p-6">
          <div className="flex items-center gap-2">
            <span className="brand-fill grid h-9 w-9 place-items-center rounded-xl text-white">
              <Bot size={17} strokeWidth={2.3} />
            </span>
            <SectionTitle>Telegram-токен</SectionTitle>
          </div>
          <p className="mt-3 text-[15px] leading-relaxed text-ink-soft">
            Напиши <Code>@BotFather</Code>, команда <Code>/newbot</Code>, скопіюй токен у
            <Code>TELEGRAM_BOT_TOKEN</Code>. Використовується long-polling, тож публічний
            URL/тунель не потрібен.
          </p>
        </div>

        <div className="card p-6">
          <div className="flex items-center gap-2">
            <span className="brand-fill grid h-9 w-9 place-items-center rounded-xl text-white">
              <MessageSquare size={17} strokeWidth={2.3} />
            </span>
            <SectionTitle>Zendesk</SectionTitle>
          </div>
          <p className="mt-3 text-[15px] leading-relaxed text-ink-soft">
            Створи безкоштовний trial. У Admin Center → APIs увімкни token access і створи API
            token. Задай <Code>ZENDESK_SUBDOMAIN</Code>, <Code>ZENDESK_EMAIL</Code>,
            <Code>ZENDESK_API_TOKEN</Code>. Якщо не задано — Zendesk вважається недоступним
            (лог-попередження, без падіння).
          </p>
        </div>
      </div>
    </div>
  );
}

type Scenario = {
  id: string;
  trigger: string;
  category: string;
  priority: string;
  escalation: string;
  priorityTone: "neutral" | "warn" | "danger";
};

const SCENARIOS: Scenario[] = [
  { id: "C-1", trigger: "Як користуватися платформою", category: "how_to", priority: "normal", escalation: "— (вирішує AI)", priorityTone: "neutral" },
  { id: "C-2", trigger: "Поповнення балансу", category: "billing", priority: "normal", escalation: "finance", priorityTone: "neutral" },
  { id: "C-3", trigger: "Недоставлені SMS", category: "delivery_issue", priority: "high", escalation: "l2_support", priorityTone: "warn" },
  { id: "C-4", trigger: "Поза робочим часом", category: "after_hours", priority: "normal", escalation: "ранкова черга", priorityTone: "neutral" },
  { id: "C-5", trigger: "Ціни / комерція", category: "commercial", priority: "normal", escalation: "sales", priorityTone: "neutral" },
  { id: "C-6", trigger: "Збій / помилка API", category: "outage", priority: "urgent", escalation: "l2_support", priorityTone: "danger" },
  { id: "C-7", trigger: "Нерозпізнане повідомлення", category: "unknown", priority: "normal", escalation: "general_support", priorityTone: "neutral" },
  { id: "C-8", trigger: "Скарга (негатив)", category: "other", priority: "high", escalation: "support_lead", priorityTone: "warn" },
];

function ScenariosTab() {
  return (
    <div className="space-y-6">
      <div className="card p-6">
        <SectionTitle>8 сценаріїв підтримки</SectionTitle>
        <p className="mt-3 text-[15px] leading-relaxed text-ink-soft">
          Агент обробляє 7 обов'язкових сценаріїв (C-1…C-7) плюс бонусний C-8 (розпізнавання
          негативної тональності). Кожен сценарій має фіксовані категорію, пріоритет і ціль
          ескалації.
        </p>
      </div>

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
                  <td className="px-4 py-3 text-ink-soft">{scenario.trigger}</td>
                  <td className="px-4 py-3">
                    <Code>{scenario.category}</Code>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`badge badge-${scenario.priorityTone}`}>
                      {scenario.priority}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-ink-soft">{scenario.escalation}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="card p-6">
        <SectionTitle>Кілька важливих правил</SectionTitle>
        <ul className="mt-3 space-y-2 text-[15px] text-ink-soft">
          <li>
            • <strong>after_hours</strong>: робочий час Пн–Пт 09:00–18:00, таймзона
            <Code>Europe/Kyiv</Code>. Сб/Нд — завжди поза робочим часом.
          </li>
          <li>
            • <strong>Виняток для outage (C-6)</strong>: аварія завжди термінова — навіть уночі
            не йде в after_hours.
          </li>
          <li>
            • <strong>commercial (C-5)</strong>: бот ніколи не називає конкретних цін — лише
            каже, що зв'яжеться менеджер з продажів.
          </li>
          <li>
            • <strong>unknown (C-7)</strong>: спрацьовує і на безглузді повідомлення, і при
            низькій впевненості класифікатора (<Code>confidence &lt; 0.55</Code>). Бот нічого не
            вигадує.
          </li>
        </ul>
      </div>
    </div>
  );
}

type TestExample = {
  id: string;
  title: string;
  expects: string;
  ua: string;
  en: string;
};

const TEST_EXAMPLES: TestExample[] = [
  {
    id: "C-1",
    title: "Як користуватися платформою (how_to)",
    expects: "Відповідь з FAQ з покроковою інструкцією. Ескалації немає, resolved_by_ai = true.",
    ua: "Як мені відправити масову SMS-розсилку?",
    en: "How do I send a bulk SMS campaign?",
  },
  {
    id: "C-2",
    title: "Поповнення балансу (billing)",
    expects: "Інструкція «Billing → Top up balance» + прохання прислати підтвердження. escalation = finance.",
    ua: "Як поповнити баланс? Дайте, будь ласка, реквізити для оплати.",
    en: "How can I top up my balance? What is the wallet address for payment?",
  },
  {
    id: "C-3",
    title: "Недоставлені SMS (delivery_issue)",
    expects: "Бот просить номер, час і Sender ID, передає в L2. priority = high. Сутності — у metadata.",
    ua: 'Мої SMS на номер +380501234567 о 14:30 не доставилися. Sender ID був "MyApp".',
    en: 'My SMS to +380501234567 at 14:30 was not delivered. Sender ID was "MyApp".',
  },
  {
    id: "C-4",
    title: "Поза робочим часом (after_hours)",
    expects: "Миттєве підтвердження + тикет у ранкову чергу. metadata.was_after_hours = true.",
    ua: "У мене технічне питання щодо платформи.",
    en: "I have a technical question about the platform.",
  },
  {
    id: "C-5",
    title: "Ціни / комерція (commercial)",
    expects: "Ввічливе підтвердження, «менеджер зв'яжеться». Ціни НЕ називаються. escalation = sales.",
    ua: "Скільки коштує масова SMS-розсилка? Чи можна знижку за великий обсяг?",
    en: "What is your pricing for bulk SMS? Can we get a discount for high volume?",
  },
  {
    id: "C-6",
    title: "Збій / помилка API (outage)",
    expects: "Бот просить текст помилки/час/IP, підтверджує терміновість, ескалює негайно. priority = urgent.",
    ua: 'Впало SMPP-з\'єднання, помилка "bind_failed". IP 192.168.1.100, час 15:45, акаунт acme.',
    en: 'Our SMPP connection keeps dropping. Error: "bind_failed". IP: 192.168.1.100. Time 15:45.',
  },
  {
    id: "C-7",
    title: "Нерозпізнане повідомлення (unknown)",
    expects: "Ввічливе «передаю спеціалісту», тикет із сирим текстом. escalation = general_support.",
    ua: "У чому сенс життя?",
    en: "asdkjh qweqwe ???",
  },
  {
    id: "C-8",
    title: "Скарга / негатив (other + sentiment)",
    expects: "Бот розпізнає негатив, тикет з HIGH priority, сповіщає support_lead. sentiment = negative.",
    ua: "Ваш сервіс жахливий! Я дуже розчарований якістю обслуговування.",
    en: "Your service is terrible! I'm so frustrated and disappointed with the platform.",
  },
];

function TestingTab() {
  return (
    <div className="space-y-6">
      <div className="card p-6">
        <SectionTitle>Як тестувати</SectionTitle>
        <ol className="mt-3 space-y-2 text-[15px] text-ink-soft">
          <li>1. Запусти проєкт (бот має висіти на long-polling з валідним токеном).</li>
          <li>2. Відкрий чат з ботом у Telegram або скористайся симулятором в адмінці.</li>
          <li>3. Надсилай повідомлення зі списку нижче — по одному.</li>
          <li>4. Після кожного дивись: відповідь бота + створений тикет в адмін-панелі.</li>
          <li>5. Наприкінці запусти аналітику.</li>
        </ol>
        <div className="mt-4 space-y-2.5">
          <div className="rounded-xl bg-sky-soft px-4 py-3 text-[13.5px] text-[#2980b5]">
            <strong>Про сесії:</strong> повідомлення від одного клієнта в межах
            <Code>SESSION_WINDOW_MINUTES</Code> (типово 30 хв) приклеюються до{" "}
            <strong>одного</strong> тикета. Щоб кожен сценарій створив окремий тикет — тестуй з
            різних акаунтів, чекай &gt;30 хв або чисти БД між прогонами.
          </div>
          <div className="rounded-xl bg-violet-soft px-4 py-3 text-[13.5px] text-[#7c43c4]">
            <strong>Про мову:</strong> класифікатор мовонезалежний (укр/рос/англ). Готові
            відповіді бота і FAQ — англійською.
          </div>
        </div>
      </div>

      <div className="card p-6">
        <SectionTitle>DEBUG-логи</SectionTitle>
        <p className="mt-3 text-[15px] leading-relaxed text-ink-soft">
          Щоб бачити повний шлях повідомлення (що йде в OpenAI, відповідь/токени, рішення
          роутера, фінальну відповідь) — увімкни DEBUG у <Code>.env</Code> і перезапусти:
        </p>
        <CodeBlock code={`LOG_LEVEL=DEBUG`} />
        <p className="text-[14px] leading-relaxed text-muted">
          Для звичайного прогону поверни <Code>LOG_LEVEL=INFO</Code> — DEBUG логує повні промпти
          й тексти.
        </p>
      </div>

      <div className="space-y-4">
        <SectionTitle>Приклади повідомлень</SectionTitle>
        {TEST_EXAMPLES.map((example) => (
          <div key={example.id} className="card p-6">
            <div className="flex items-center gap-3">
              <span className="badge badge-violet">{example.id}</span>
              <h3 className="font-display text-base font-bold text-ink">{example.title}</h3>
            </div>
            <p className="mt-2 text-[14px] leading-relaxed text-muted">
              <strong className="text-ink-soft">Очікується:</strong> {example.expects}
            </p>
            <div className="mt-3 grid gap-3 sm:grid-cols-2">
              <div>
                <span className="text-[12px] font-bold uppercase tracking-wide text-muted">
                  Українською
                </span>
                <CodeBlock code={example.ua} />
              </div>
              <div>
                <span className="text-[12px] font-bold uppercase tracking-wide text-muted">
                  English
                </span>
                <CodeBlock code={example.en} />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function AnalyticsTab() {
  return (
    <div className="space-y-6">
      <div className="card p-6">
        <SectionTitle>Підсумкова перевірка: аналітичний звіт</SectionTitle>
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
        <SectionTitle>Що має бути у звіті</SectionTitle>
        <ul className="mt-3 space-y-2 text-[15px] text-ink-soft">
          <li>• Всього тикетів (по каналах і по днях).</li>
          <li>
            • Розподіл за категоріями (how_to, billing, delivery_issue, commercial, outage,
            unknown, other).
          </li>
          <li>• % ескалацій і % вирішених AI.</li>
          <li>• Розподіл тональності (positive / neutral / negative).</li>
          <li>• Обсяг after-hours тикетів.</li>
        </ul>
      </div>
    </div>
  );
}

const TAB_CONTENT: Record<TabId, () => JSX.Element> = {
  overview: OverviewTab,
  run: RunTab,
  scenarios: ScenariosTab,
  testing: TestingTab,
  analytics: AnalyticsTab,
};

export default function Docs() {
  const [active, setActive] = useState<TabId>("overview");
  const ActiveContent = TAB_CONTENT[active];

  return (
    <div className="mesh-bg min-h-dvh">
      <header className="mx-auto flex max-w-5xl items-center justify-between px-6 py-6">
        <div className="flex items-center gap-2 font-display text-lg font-bold">
          <span className="brand-fill grid h-9 w-9 place-items-center rounded-xl text-white">
            <MessageSquare size={18} strokeWidth={2.4} />
          </span>
          <span className="brand-text">gatum</span>
        </div>
        <Link to="/support" className="btn btn-ghost">
          <ArrowLeft size={16} strokeWidth={2.3} /> На головну
        </Link>
      </header>

      <main className="mx-auto max-w-5xl px-6 pb-24">
        <section className="animate-rise py-10 text-center sm:py-14">
          <span className="badge badge-violet mx-auto">Документація · прототип</span>
          <h1 className="mx-auto mt-5 max-w-3xl font-display text-4xl font-extrabold leading-tight text-ink sm:text-5xl">
            Як <span className="brand-text">запустити</span> і протестувати агента
          </h1>
          <p className="mx-auto mt-4 max-w-xl text-lg text-muted">
            Багатоканальний AI-агент підтримки Gatum: огляд, запуск, сценарії та тестування.
          </p>
        </section>

        <nav className="sticky top-3 z-10 mb-8 flex flex-wrap justify-center gap-2 rounded-full border border-line bg-surface/80 p-2 backdrop-blur">
          {TABS.map((tab) => {
            const isActive = tab.id === active;
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActive(tab.id)}
                className={`btn ${isActive ? "btn-gradient" : "btn-ghost border-0"}`}
              >
                <tab.icon size={16} strokeWidth={2.3} />
                {tab.label}
              </button>
            );
          })}
        </nav>

        <div className="animate-rise" key={active}>
          <ActiveContent />
        </div>
      </main>
    </div>
  );
}
