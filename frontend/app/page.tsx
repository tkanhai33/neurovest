import Link from "next/link";

const platformFeatures = [
  {
    eyebrow: "Market Intelligence",
    title: "See more than price.",
    description:
      "Approved market data, portfolio context, historical observations, and strategy signals are brought together through controlled read paths.",
    items: [
      "Live market observation",
      "Historical context",
      "Portfolio visibility",
    ],
  },
  {
    eyebrow: "Strategy and Risk",
    title: "Every decision meets a boundary.",
    description:
      "Independent strategy and risk systems evaluate decisions before anything can progress toward an execution boundary.",
    items: [
      "Multi-strategy evaluation",
      "Risk-gate enforcement",
      "Decision audit trails",
    ],
  },
  {
    eyebrow: "Neuro Intelligence",
    title: "Local intelligence. Visible flow.",
    description:
      "Neuro combines local inference, controlled context, and observable runtime traces without surrendering authority to the frontend.",
    items: [
      "Local Ollama inference",
      "Context-aware analysis",
      "Observable execution paths",
    ],
  },
];

const safetyItems = [
  {
    title: "Simulation first",
    detail:
      "Live trading remains disabled while the platform is qualified.",
  },
  {
    title: "Risk governed",
    detail:
      "Frontend requests cannot bypass server-authoritative safety gates.",
  },
  {
    title: "Observable",
    detail:
      "Declared architecture and real runtime activity remain distinguishable.",
  },
  {
    title: "User controlled",
    detail:
      "Neuro supports decisions without operating beyond approved authority.",
  },
];

const systemFlow = [
  "Frontend",
  "Authentication",
  "Context",
  "Market Data",
  "Strategy",
  "Risk",
  "Neuro",
  "Validation",
  "Response",
];

export default function LandingPage() {
  return (
    <main className="min-h-screen overflow-hidden bg-[#020617] text-white">
      <div className="landing-grid pointer-events-none fixed inset-0 opacity-50" />

      <header className="relative z-20 border-b border-white/5 bg-[#020617]/70 backdrop-blur-xl">
        <div className="mx-auto flex max-w-[1440px] items-center justify-between px-6 py-5 lg:px-10">
          <Link
            href="/"
            className="group flex items-center gap-3"
            aria-label="NeuroVest home"
          >
            <span className="flex h-10 w-10 items-center justify-center rounded-xl border border-cyan-300/30 bg-cyan-400/10 shadow-[0_0_28px_rgba(34,211,238,0.16)]">
              <span className="h-3 w-3 rotate-45 border border-cyan-200" />
            </span>

            <span>
              <span className="block text-sm font-black uppercase tracking-[0.36em] text-white">
                NeuroVest
              </span>
              <span className="block text-[10px] uppercase tracking-[0.26em] text-cyan-300/70">
                Intelligence Platform
              </span>
            </span>
          </Link>

          <nav
            className="hidden items-center gap-7 text-sm text-slate-400 lg:flex"
            aria-label="Primary navigation"
          >
            <a href="#platform" className="transition hover:text-white">
              Platform
            </a>
            <a href="#how-it-works" className="transition hover:text-white">
              How it works
            </a>
            <a href="#safety" className="transition hover:text-white">
              Safety
            </a>
            <a href="#architecture" className="transition hover:text-white">
              Architecture
            </a>
          </nav>

          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="hidden rounded-xl border border-slate-700/80 px-4 py-2.5 text-sm font-bold text-slate-200 transition hover:border-cyan-300/40 hover:text-white sm:inline-flex"
            >
              Sign in
            </Link>

            <Link
              href="/register"
              className="inline-flex rounded-xl bg-cyan-300 px-4 py-2.5 text-sm font-black text-slate-950 shadow-[0_0_28px_rgba(34,211,238,0.22)] transition hover:bg-cyan-200"
            >
              Create account
            </Link>
          </div>
        </div>
      </header>

      <section className="relative">
        <div className="landing-orb landing-orb-cyan" />
        <div className="landing-orb landing-orb-violet" />

        <div className="relative mx-auto grid min-h-[770px] max-w-[1440px] items-center gap-16 px-6 py-20 lg:grid-cols-[0.92fr_1.08fr] lg:px-10 lg:py-24">
          <div className="relative z-10">
            <div className="inline-flex items-center gap-3 rounded-full border border-cyan-300/20 bg-cyan-400/5 px-4 py-2 text-xs font-bold uppercase tracking-[0.24em] text-cyan-200">
              <span className="h-2 w-2 rounded-full bg-cyan-300 shadow-[0_0_14px_rgba(34,211,238,0.9)]" />
              Private · Observable · Controlled
            </div>

            <h1 className="mt-8 max-w-4xl text-5xl font-black leading-[0.98] tracking-[-0.045em] text-white sm:text-6xl xl:text-8xl">
              Intelligence for
              <span className="landing-gradient-text block">
                every market decision.
              </span>
            </h1>

            <p className="mt-7 max-w-2xl text-lg leading-8 text-slate-400 sm:text-xl">
              A locally powered financial intelligence platform built to
              observe markets, evaluate strategies, enforce risk boundaries,
              and make system activity visible.
            </p>

            <div className="mt-10 flex flex-col gap-3 sm:flex-row">
              <Link
                href="/login"
                className="inline-flex items-center justify-center rounded-2xl bg-cyan-300 px-6 py-4 text-sm font-black text-slate-950 shadow-[0_0_40px_rgba(34,211,238,0.22)] transition hover:-translate-y-0.5 hover:bg-cyan-200"
              >
                Enter NeuroVest
                <span className="ml-3" aria-hidden="true">
                  →
                </span>
              </Link>

              <a
                href="#platform"
                className="inline-flex items-center justify-center rounded-2xl border border-slate-700 bg-slate-950/40 px-6 py-4 text-sm font-bold text-slate-200 transition hover:border-cyan-300/30 hover:bg-slate-900/70"
              >
                Explore the platform
              </a>
            </div>

            <div className="mt-10 grid max-w-2xl gap-3 sm:grid-cols-3">
              {[
                ["Simulation-first", "Controlled qualification"],
                ["Risk-governed", "Server-authoritative"],
                ["Locally powered", "Private AI runtime"],
              ].map(([title, detail]) => (
                <div
                  key={title}
                  className="rounded-2xl border border-white/5 bg-white/[0.025] p-4"
                >
                  <p className="text-sm font-black text-white">{title}</p>
                  <p className="mt-1 text-xs text-slate-500">{detail}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="relative mx-auto w-full max-w-[720px]">
            <div className="absolute inset-10 rounded-full bg-cyan-400/10 blur-[110px]" />
            <div className="absolute inset-x-20 bottom-10 top-28 rounded-full bg-fuchsia-500/10 blur-[120px]" />

            <div className="neuro-art-frame relative min-h-[560px] overflow-hidden rounded-[2.5rem] border border-white/10 bg-slate-950/55 p-5 shadow-[0_0_90px_rgba(34,211,238,0.08)] backdrop-blur-xl sm:min-h-[650px]">
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_35%,rgba(34,211,238,0.12),transparent_36%),radial-gradient(circle_at_50%_72%,rgba(168,85,247,0.10),transparent_38%)]" />

              <div className="absolute left-5 top-5 flex items-center gap-2 rounded-full border border-emerald-300/20 bg-emerald-400/5 px-3 py-2 text-[10px] font-bold uppercase tracking-[0.22em] text-emerald-200">
                <span className="h-2 w-2 rounded-full bg-emerald-300" />
                Runtime protected
              </div>

              <div className="absolute right-5 top-5 rounded-full border border-amber-300/20 bg-amber-400/5 px-3 py-2 text-[10px] font-bold uppercase tracking-[0.22em] text-amber-200">
                Live execution disabled
              </div>

              <div className="relative flex min-h-[520px] items-center justify-center sm:min-h-[610px]">
                <div className="relative flex h-[370px] w-[310px] items-center justify-center sm:h-[470px] sm:w-[390px]">
                  <div className="neuro-placeholder-ring absolute inset-0 rounded-full border border-cyan-300/15" />
                  <div className="neuro-placeholder-ring neuro-placeholder-ring-delay absolute inset-10 rounded-full border border-fuchsia-300/15" />

                  <div className="relative z-10 max-w-[270px] text-center">
                    <div className="mx-auto flex h-24 w-24 items-center justify-center rounded-[2rem] border border-cyan-300/25 bg-cyan-400/5 shadow-[0_0_50px_rgba(34,211,238,0.12)]">
                      <span className="text-4xl font-black text-cyan-200">
                        N
                      </span>
                    </div>

                    <p className="mt-7 text-xs font-black uppercase tracking-[0.34em] text-cyan-200">
                      Neuro Visual
                    </p>

                    <h2 className="mt-3 text-3xl font-black text-white">
                      Guardian intelligence
                    </h2>

                    <p className="mt-4 text-sm leading-6 text-slate-500">
                      Reserved for the future Neuro artwork. The production
                      layout remains complete until the final visual is added.
                    </p>

                    <code className="mt-5 block break-all rounded-xl border border-slate-800 bg-slate-950/70 px-3 py-2 text-[10px] text-slate-500">
                      /images/neuro/neuro-hero.png
                    </code>
                  </div>
                </div>
              </div>

              <div className="absolute bottom-5 left-5 right-5 grid gap-2 sm:grid-cols-3">
                {[
                  ["AI", "LOCAL"],
                  ["BROKER", "LOCKED"],
                  ["MODE", "READ ONLY"],
                ].map(([label, value]) => (
                  <div
                    key={label}
                    className="rounded-xl border border-white/5 bg-slate-950/70 px-3 py-3 backdrop-blur"
                  >
                    <p className="text-[9px] uppercase tracking-[0.2em] text-slate-600">
                      {label}
                    </p>
                    <p className="mt-1 text-xs font-black text-slate-200">
                      {value}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="border-y border-white/5 bg-slate-950/60">
        <div className="mx-auto grid max-w-[1440px] gap-px bg-white/5 px-6 lg:grid-cols-4 lg:px-10">
          {safetyItems.map((item) => (
            <div
              key={item.title}
              className="bg-[#020617] px-6 py-8"
            >
              <p className="text-sm font-black uppercase tracking-[0.18em] text-cyan-200">
                {item.title}
              </p>
              <p className="mt-3 text-sm leading-6 text-slate-500">
                {item.detail}
              </p>
            </div>
          ))}
        </div>
      </section>

      <section
        id="platform"
        className="relative mx-auto max-w-[1440px] px-6 py-28 lg:px-10"
      >
        <div className="max-w-3xl">
          <p className="text-xs font-black uppercase tracking-[0.34em] text-cyan-300">
            One controlled platform
          </p>

          <h2 className="mt-5 text-4xl font-black tracking-[-0.03em] text-white sm:text-6xl">
            Built to observe, evaluate, and explain.
          </h2>

          <p className="mt-6 text-lg leading-8 text-slate-400">
            NeuroVest separates data, domain decisions, runtime orchestration,
            safety, and presentation through explicit system boundaries.
          </p>
        </div>

        <div className="mt-14 grid gap-6 lg:grid-cols-3">
          {platformFeatures.map((feature, index) => (
            <article
              key={feature.title}
              className="group relative overflow-hidden rounded-[2rem] border border-white/10 bg-slate-950/65 p-7 transition hover:-translate-y-1 hover:border-cyan-300/25"
            >
              <div className="absolute right-5 top-4 text-7xl font-black text-white/[0.025]">
                0{index + 1}
              </div>

              <p className="relative text-xs font-black uppercase tracking-[0.28em] text-cyan-300">
                {feature.eyebrow}
              </p>

              <h3 className="relative mt-5 text-2xl font-black text-white">
                {feature.title}
              </h3>

              <p className="relative mt-4 min-h-[96px] text-sm leading-7 text-slate-400">
                {feature.description}
              </p>

              <div className="relative mt-7 space-y-3">
                {feature.items.map((item) => (
                  <div
                    key={item}
                    className="flex items-center gap-3 text-sm text-slate-300"
                  >
                    <span className="h-1.5 w-1.5 rounded-full bg-cyan-300 shadow-[0_0_10px_rgba(34,211,238,0.8)]" />
                    {item}
                  </div>
                ))}
              </div>
            </article>
          ))}
        </div>
      </section>

      <section
        id="architecture"
        className="border-y border-white/5 bg-[#030712]"
      >
        <div className="mx-auto max-w-[1440px] px-6 py-28 lg:px-10">
          <div className="grid gap-14 lg:grid-cols-[0.72fr_1.28fr] lg:items-center">
            <div>
              <p className="text-xs font-black uppercase tracking-[0.34em] text-fuchsia-300">
                Observable by design
              </p>

              <h2 className="mt-5 text-4xl font-black tracking-[-0.03em] text-white sm:text-5xl">
                See how a request moves through NeuroVest.
              </h2>

              <p className="mt-6 text-lg leading-8 text-slate-400">
                Declared architecture stays visible while real runtime traces
                illuminate only the components and connections that actually
                execute.
              </p>

              <Link
                href="/login"
                className="mt-8 inline-flex items-center text-sm font-black text-cyan-200"
              >
                Open the secured dashboard
                <span className="ml-3">→</span>
              </Link>
            </div>

            <div className="rounded-[2rem] border border-white/10 bg-slate-950/75 p-5 sm:p-8">
              <div className="flex flex-wrap items-center gap-2">
                {systemFlow.map((item, index) => (
                  <div
                    key={item}
                    className="flex items-center gap-2"
                  >
                    <div className="rounded-xl border border-cyan-300/15 bg-cyan-400/5 px-3 py-3 text-xs font-black text-cyan-100 sm:px-4">
                      {item}
                    </div>

                    {index < systemFlow.length - 1 && (
                      <span className="text-cyan-400/50">→</span>
                    )}
                  </div>
                ))}
              </div>

              <div className="mt-8 grid gap-3 sm:grid-cols-3">
                {[
                  ["Declared nodes", "Architecture"],
                  ["Observed nodes", "Runtime"],
                  ["Trace replay", "Evidence"],
                ].map(([title, detail]) => (
                  <div
                    key={title}
                    className="rounded-xl border border-slate-800 bg-slate-900/50 p-4"
                  >
                    <p className="text-sm font-black text-white">{title}</p>
                    <p className="mt-1 text-xs text-slate-500">{detail}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section
        id="safety"
        className="mx-auto max-w-[1440px] px-6 py-28 lg:px-10"
      >
        <div className="overflow-hidden rounded-[2.5rem] border border-amber-300/15 bg-[linear-gradient(135deg,rgba(120,53,15,0.12),rgba(15,23,42,0.7),rgba(88,28,135,0.08))] p-8 sm:p-12">
          <div className="grid gap-12 lg:grid-cols-[1fr_0.9fr]">
            <div>
              <p className="text-xs font-black uppercase tracking-[0.34em] text-amber-300">
                Built to fail closed
              </p>

              <h2 className="mt-5 text-4xl font-black tracking-[-0.03em] text-white sm:text-6xl">
                Safety is part of the architecture.
              </h2>

              <p className="mt-6 max-w-3xl text-lg leading-8 text-slate-400">
                Authentication remains server-authoritative. Broker execution,
                portfolio mutation, and live trading remain unavailable until
                separately qualified and approved.
              </p>
            </div>

            <div className="grid gap-3">
              {[
                "Live trading disabled",
                "Broker execution isolated",
                "Risk boundaries enforced",
                "Authentication server-authoritative",
                "Important decisions auditable",
              ].map((item) => (
                <div
                  key={item}
                  className="flex items-center justify-between rounded-2xl border border-white/5 bg-slate-950/60 px-5 py-4"
                >
                  <span className="text-sm font-bold text-slate-200">
                    {item}
                  </span>
                  <span className="text-emerald-300">✓</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section
        id="how-it-works"
        className="border-t border-white/5 bg-slate-950/40"
      >
        <div className="mx-auto max-w-[1440px] px-6 py-28 lg:px-10">
          <div className="text-center">
            <p className="text-xs font-black uppercase tracking-[0.34em] text-cyan-300">
              How it works
            </p>

            <h2 className="mt-5 text-4xl font-black tracking-[-0.03em] text-white sm:text-6xl">
              Observe. Evaluate. Explain. Record.
            </h2>
          </div>

          <div className="mt-14 grid gap-5 md:grid-cols-2 xl:grid-cols-4">
            {[
              [
                "01",
                "Observe",
                "Gather approved market, portfolio, and account context.",
              ],
              [
                "02",
                "Evaluate",
                "Run strategy and risk assessments through controlled services.",
              ],
              [
                "03",
                "Explain",
                "Return grounded results with visible operational context.",
              ],
              [
                "04",
                "Record",
                "Preserve reviewable decision and runtime evidence.",
              ],
            ].map(([number, title, detail]) => (
              <div
                key={number}
                className="rounded-[2rem] border border-white/10 bg-slate-950/70 p-7"
              >
                <p className="text-sm font-black text-cyan-300">{number}</p>
                <h3 className="mt-8 text-2xl font-black text-white">{title}</h3>
                <p className="mt-4 text-sm leading-7 text-slate-500">
                  {detail}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="relative overflow-hidden border-t border-white/5">
        <div className="landing-orb landing-orb-footer" />

        <div className="relative mx-auto max-w-[1100px] px-6 py-28 text-center">
          <p className="text-xs font-black uppercase tracking-[0.34em] text-cyan-300">
            Stay in command
          </p>

          <h2 className="mt-6 text-4xl font-black tracking-[-0.04em] text-white sm:text-6xl">
            Your market intelligence should work for you.
          </h2>

          <p className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-slate-400">
            Enter the controlled NeuroVest environment to explore the current
            dashboard, runtime graph, and read-only intelligence systems.
          </p>

          <Link
            href="/login"
            className="mt-10 inline-flex rounded-2xl bg-cyan-300 px-7 py-4 text-sm font-black text-slate-950 shadow-[0_0_38px_rgba(34,211,238,0.22)] transition hover:bg-cyan-200"
          >
            Sign in to NeuroVest
          </Link>
        </div>
      </section>

      <footer className="border-t border-white/5 bg-[#01040c]">
        <div className="mx-auto flex max-w-[1440px] flex-col gap-8 px-6 py-10 lg:flex-row lg:items-center lg:justify-between lg:px-10">
          <div>
            <p className="text-sm font-black uppercase tracking-[0.3em] text-white">
              NeuroVest
            </p>
            <p className="mt-2 text-sm text-slate-600">
              Private. Observable. Controlled.
            </p>
          </div>

          <div className="flex flex-wrap gap-5 text-sm text-slate-500">
            <a href="#platform" className="hover:text-white">
              Platform
            </a>
            <a href="#safety" className="hover:text-white">
              Safety
            </a>
            <a href="#architecture" className="hover:text-white">
              Architecture
            </a>
            <Link href="/login" className="hover:text-white">
              Sign in
            </Link>
          </div>

          <div className="text-xs leading-5 text-slate-600">
            <p>Broker execution: Disabled</p>
            <p>Live trading: Disabled</p>
          </div>
        </div>
      </footer>
    </main>
  );
}
