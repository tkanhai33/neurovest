"use client";

import Link from "next/link";

const disclosures = [
  {
    title: "Investment risk",
    text:
      "Investing involves risk, including the possible loss of principal. Market values can rise or fall and historical results do not guarantee future performance.",
  },
  {
    title: "Investment intelligence, not guaranteed outcomes",
    text:
      "NeuroVest can organize market information, portfolio context, research, model outputs, strategy information and AI-generated explanations. These tools can support analysis, but they cannot guarantee an investment outcome or eliminate investment risk.",
  },
  {
    title: "AI limitations",
    text:
      "AI-generated information can be incomplete, uncertain or incorrect. Important information should be independently evaluated rather than relying on an AI response as the sole basis for a financial decision.",
  },
  {
    title: "Strategy and model outputs",
    text:
      "Strategy analysis, model signals, backtests and historical evaluations are informational tools. Historical or simulated performance does not guarantee future results.",
  },
  {
    title: "Paper trading",
    text:
      "Paper-trading results are simulated. Simulated execution does not reproduce every condition of real markets, including liquidity, slippage, latency, order handling and changing market conditions.",
  },
  {
    title: "Brokerage information",
    text:
      "Where supported brokerage connections are used, third-party data may be delayed, incomplete or subject to the availability and terms of the connected provider.",
  },
  {
    title: "User responsibility",
    text:
      "Users remain responsible for their investment decisions and for evaluating whether an investment, strategy or action is appropriate for their circumstances.",
  },
];

export default function DisclosuresPage() {
  return (
    <main className="disclosurePage">
      <nav>
        <Link href="/" className="brand">
          <span>N</span>
          NeuroVest
        </Link>

        <Link href="/" className="backLink">
          ← Back to NeuroVest
        </Link>
      </nav>

      <article>
        <p className="eyebrow">
          IMPORTANT INFORMATION
        </p>

        <h1>
          Disclosures
        </h1>

        <p className="intro">
          NeuroVest provides software, investment-intelligence tools and
          controlled investing workflows. The information below describes
          important limitations users should understand when using the
          platform.
        </p>

        {disclosures.map((item) => (
          <section key={item.title}>
            <h2>{item.title}</h2>
            <p>{item.text}</p>
          </section>
        ))}

        <div className="notice">
          These disclosures are general product information and should be
          reviewed with qualified Canadian legal and compliance counsel before
          final commercial launch.
        </div>
      </article>

      <footer>
        <span>© 2026 NeuroVest</span>

        <div>
          <Link href="/">Home</Link>
          <Link href="/architecture">Architecture</Link>
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

        .disclosurePage {
          min-height: 100vh;
          background:
            radial-gradient(
              circle at 50% -10%,
              rgba(86, 232, 255, 0.07),
              transparent 32rem
            ),
            #020713;
        }

        .disclosurePage nav {
          max-width: 980px;
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

        .backLink {
          color: #8d9db2;
          font-size: 12px;
        }

        article {
          max-width: 820px;
          margin: 0 auto;
          padding: 105px 28px 90px;
        }

        .eyebrow {
          color: #56e8ff;
          font-size: 11px;
          font-weight: 850;
          letter-spacing: 0.22em;
        }

        h1 {
          margin: 17px 0 24px;
          font-size: clamp(50px, 7vw, 78px);
          letter-spacing: -0.055em;
        }

        .intro {
          margin-bottom: 60px;
          color: #98a7ba;
          font-size: 17px;
          line-height: 1.8;
        }

        section {
          padding: 30px 0;
          border-top: 1px solid rgba(148, 163, 184, 0.13);
        }

        section h2 {
          margin: 0 0 13px;
          font-size: 20px;
        }

        section p {
          margin: 0;
          color: #8292a7;
          font-size: 14px;
          line-height: 1.8;
        }

        .notice {
          margin-top: 35px;
          padding: 24px;
          border: 1px solid rgba(255, 216, 77, 0.16);
          border-radius: 13px;
          color: #a8a28c;
          background: rgba(255, 216, 77, 0.025);
          font-size: 12px;
          line-height: 1.7;
        }

        footer {
          max-width: 980px;
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

        @media (max-width: 680px) {

          article {
            padding-top: 75px;
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
