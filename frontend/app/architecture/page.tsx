"use client";

import Link from "next/link";

const principles = [
  {
    title: "You stay in control",
    text:
      "NeuroVest is designed so investment intelligence supports your decisions without automatically becoming an execution instruction.",
  },
  {
    title: "Risk stays in the workflow",
    text:
      "Risk awareness remains attached to decision and execution workflows instead of being treated as a separate afterthought.",
  },
  {
    title: "Secure account boundaries",
    text:
      "Authenticated access and role boundaries determine which product capabilities a user can reach.",
  },
  {
    title: "Important actions stay reviewable",
    text:
      "Important system activity is designed to remain observable so decisions and actions can be understood after they occur.",
  },
  {
    title: "Test before real-world use",
    text:
      "Strategy and execution workflows can be evaluated in controlled environments before real-world execution is considered.",
  },
  {
    title: "Brokerage boundaries remain explicit",
    text:
      "Connected brokerage functionality is treated as a protected product boundary rather than unrestricted AI authority.",
  },
];

export default function ArchitecturePage() {
  return (
    <main className="resourcePage">
      <nav>
        <Link href="/" className="brand">
          <span>N</span>
          NeuroVest
        </Link>

        <div className="navLinks">
          <Link href="/">Product</Link>
          <Link href="/disclosures">Disclosures</Link>
          <Link href="/login">Sign in</Link>
        </div>
      </nav>

      <section className="hero">
        <p className="eyebrow">
          BUILT DIFFERENTLY UNDER THE HOOD
        </p>

        <h1>
          Intelligence that informs.
          <span> Controls that remain yours.</span>
        </h1>

        <p className="lead">
          NeuroVest is designed around authenticated access, risk-aware
          workflows, separation of authority and reviewable system activity.
          Those choices support a simpler product promise: useful investment
          intelligence without handing unrestricted control to the AI.
        </p>
      </section>

      <section className="principles">
        {principles.map((principle) => (
          <article key={principle.title}>
            <span className="check">✓</span>

            <h2>{principle.title}</h2>

            <p>{principle.text}</p>
          </article>
        ))}
      </section>

      <section className="flow">
        <p className="eyebrow">
          HIGH-LEVEL PRODUCT FLOW
        </p>

        <h2>
          Information moves through controlled layers.
        </h2>

        <div className="flowRow">
          {[
            "Account",
            "Portfolio & Market Context",
            "Neuro",
            "Strategy",
            "Risk",
            "Controlled Action",
          ].map((item, index, array) => (
            <div className="flowItem" key={item}>
              <span>{item}</span>

              {index < array.length - 1 && (
                <b aria-hidden="true">→</b>
              )}
            </div>
          ))}
        </div>

        <p className="note">
          This is intentionally a high-level overview and does not expose
          credentials, private infrastructure, security-sensitive deployment
          details or internal secrets.
        </p>
      </section>

      <section className="cta">
        <p className="eyebrow">
          THE PRODUCT COMES FIRST
        </p>

        <h2>
          Architecture matters because it supports trust.
        </h2>

        <p>
          You should not need to understand the internals to use NeuroVest.
          The controls underneath the platform exist to make the experience
          clearer, safer and more accountable.
        </p>

        <Link href="/register">
          Get started →
        </Link>
      </section>

      <footer>
        <span>© 2026 NeuroVest</span>

        <div>
          <Link href="/">Home</Link>
          <Link href="/disclosures">Disclosures</Link>
          <Link href="/user/support">Support</Link>
        </div>
      </footer>

      <style jsx global>{`
        * {
          box-sizing: border-box;
        }

        html,
        body {
          margin: 0;
          background: #020713;
          color: #f7fafc;
          font-family:
            Inter,
            ui-sans-serif,
            system-ui,
            -apple-system,
            BlinkMacSystemFont,
            "Segoe UI",
            sans-serif;
        }

        a {
          color: inherit;
          text-decoration: none;
        }

        .resourcePage {
          min-height: 100vh;
          background:
            radial-gradient(
              circle at 50% -10%,
              rgba(86, 232, 255, 0.09),
              transparent 34rem
            ),
            #020713;
        }

        .resourcePage nav {
          max-width: 1184px;
          height: 76px;
          margin: 0 auto;
          padding: 0 28px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          border-bottom: 1px solid rgba(148, 163, 184, 0.12);
        }

        .brand {
          display: flex;
          align-items: center;
          gap: 10px;
          font-weight: 800;
        }

        .brand span {
          width: 32px;
          height: 32px;
          display: grid;
          place-items: center;
          border: 1px solid rgba(86, 232, 255, 0.38);
          border-radius: 9px;
          color: #56e8ff;
          background: rgba(86, 232, 255, 0.07);
        }

        .navLinks {
          display: flex;
          gap: 26px;
          color: #8999ae;
          font-size: 13px;
        }

        .hero {
          max-width: 980px;
          margin: 0 auto;
          padding: 115px 28px 80px;
        }

        .eyebrow {
          color: #56e8ff;
          font-size: 11px;
          font-weight: 850;
          letter-spacing: 0.22em;
        }

        .hero h1 {
          max-width: 900px;
          margin: 20px 0 25px;
          font-size: clamp(46px, 6vw, 76px);
          line-height: 1.02;
          letter-spacing: -0.055em;
        }

        .hero h1 span {
          color: #9eacc0;
        }

        .lead {
          max-width: 760px;
          color: #8f9eb3;
          font-size: 17px;
          line-height: 1.75;
        }

        .principles {
          max-width: 1128px;
          margin: 0 auto;
          padding: 20px 28px 90px;
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 14px;
        }

        .principles article {
          min-height: 235px;
          padding: 28px;
          border: 1px solid rgba(148, 163, 184, 0.15);
          border-radius: 15px;
          background: #07101e;
        }

        .check {
          width: 20px;
          height: 20px;
          display: grid;
          place-items: center;
          margin-bottom: 42px;
          border-radius: 50%;
          color: #52e6a4;
          background: rgba(82, 230, 164, 0.08);
          font-size: 11px;
        }

        .principles h2 {
          margin: 0 0 12px;
          font-size: 19px;
        }

        .principles p {
          margin: 0;
          color: #7d8da3;
          font-size: 13px;
          line-height: 1.7;
        }

        .flow {
          max-width: 1128px;
          margin: 0 auto;
          padding: 90px 28px;
          border-top: 1px solid rgba(148, 163, 184, 0.12);
        }

        .flow h2 {
          margin: 18px 0 38px;
          font-size: clamp(36px, 4vw, 50px);
          letter-spacing: -0.04em;
        }

        .flowRow {
          display: flex;
          align-items: center;
          flex-wrap: wrap;
          gap: 10px;
        }

        .flowItem {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .flowItem span {
          padding: 12px 15px;
          border: 1px solid rgba(86, 232, 255, 0.17);
          border-radius: 10px;
          color: #bfd0df;
          background: rgba(86, 232, 255, 0.035);
          font-size: 12px;
        }

        .flowItem b {
          color: #56e8ff;
          font-weight: 500;
        }

        .note {
          max-width: 720px;
          margin-top: 32px;
          color: #61748b;
          font-size: 11px;
          line-height: 1.7;
        }

        .cta {
          max-width: 1070px;
          margin: 35px auto 90px;
          padding: 65px 28px;
          text-align: center;
          border: 1px solid rgba(86, 232, 255, 0.16);
          border-radius: 20px;
          background: #07101e;
        }

        .cta h2 {
          margin: 16px 0 0;
          font-size: 38px;
          letter-spacing: -0.04em;
        }

        .cta p:not(.eyebrow) {
          max-width: 650px;
          margin: 18px auto 28px;
          color: #8292a7;
          line-height: 1.7;
        }

        .cta a {
          display: inline-flex;
          padding: 13px 20px;
          border-radius: 10px;
          color: #001018;
          background: #56e8ff;
          font-weight: 800;
          font-size: 13px;
        }

        footer {
          max-width: 1128px;
          margin: 0 auto;
          padding: 30px 28px;
          border-top: 1px solid rgba(148, 163, 184, 0.12);
          display: flex;
          justify-content: space-between;
          color: #53667d;
          font-size: 10px;
        }

        footer div {
          display: flex;
          gap: 20px;
        }

        @media (max-width: 800px) {

          .navLinks {
            display: none;
          }

          .hero {
            padding-top: 80px;
          }

          .principles {
            grid-template-columns: 1fr;
          }

          footer {
            flex-direction: column;
            gap: 18px;
          }
        }
      `}</style>
    </main>
  );
}
