"use client";

import Link from "next/link";
import NeuroHeroModel from "@/components/landing/NeuroHeroModel";


const capabilities = [
  {
    eyebrow: "PORTFOLIO INTELLIGENCE",
    title: "See the whole picture.",
    description:
      "See your positions, market context and portfolio signals together so you can understand what changed and what deserves your attention.",
    detail:
      "Positions · Analytics · Market context",
  },
  {
    eyebrow: "AI INVESTMENT RESEARCH",
    title: "Ask better questions.",
    description:
      "Ask Neuro about companies, markets and your portfolio, then bring research and financial context into one understandable conversation.",
    detail:
      "Research · Context · AI assistance",
  },
  {
    eyebrow: "STRATEGY INTELLIGENCE",
    title: "Test the idea before trusting it.",
    description:
      "Review evidence, historical behavior and risk before deciding whether an investment idea deserves your trust.",
    detail:
      "Strategies · Historical evaluation · Review",
  },
];


const protections = [
  {
    title: "You stay in control",
    description:
      "NeuroVest is designed around governed actions and explicit user control rather than unrestricted autonomous execution.",
  },
  {
    title: "Risk checked",
    description:
      "Risk controls sit between investment intelligence and execution-capable workflows.",
  },
  {
    title: "Paper first",
    description:
      "Strategies can be evaluated in controlled paper workflows before real-world execution is ever considered.",
  },
  {
    title: "Decisions stay traceable",
    description:
      "Important system decisions are designed to remain observable so behavior can be reviewed instead of hidden behind the AI.",
  },
];


const productAreas = [
  {
    number: "01",
    title: "Portfolio",
    text: "Understand positions, portfolio context and analytics from one secured workspace.",
  },
  {
    number: "02",
    title: "Research",
    text: "Bring market data, news and investment research into the same decision environment.",
  },
  {
    number: "03",
    title: "Neuro",
    text: "Use AI as an investment-intelligence layer rather than an unexplained black box.",
  },
  {
    number: "04",
    title: "Strategies",
    text: "Review ideas, model signals and strategy evidence before treating them as actionable.",
  },
  {
    number: "05",
    title: "Risk",
    text: "Keep risk awareness and execution controls attached to the investment workflow.",
  },
  {
    number: "06",
    title: "Brokerage",
    text: "Connect supported brokerage information to give NeuroVest useful portfolio context.",
  },
];


const trustItems = [
  "Execution stays under your control",
  "Risk checks remain part of the workflow",
  "Secure authenticated account access",
  "Important decisions stay reviewable",
  "Strategies can be tested before real-world use",
  "Brokerage connections stay inside protected boundaries",
];


const footerGroups = [
  {
    title: "Product",
    links: [
      ["Dashboard", "/dashboard"],
      ["Portfolio", "/user/dashboard"],
      ["Strategies", "/strategy-library"],
      ["Neuro AI", "/chat"],
      ["Support", "/user/support"],
    ],
  },
  {
    title: "Investing & Trust",
    links: [
      ["How NeuroVest works", "#how-it-works"],
      ["Safety & controls", "#safety"],
      ["Security", "#security"],
      ["System architecture", "/architecture"],
      ["Disclosures", "/disclosures"],
    ],
  },
  {
    title: "Account",
    links: [
      ["Get started", "/register"],
      ["Sign in", "/login"],
      ["Settings", "/user/settings"],
      ["Brokerage", "/user/brokerage"],
    ],
  },
];


function CheckIcon() {
  return (
    <span className="checkIcon" aria-hidden="true">
      ✓
    </span>
  );
}


export default function Home() {

  return (
    <main className="siteShell">
      <header className="navigation">
        <Link href="/" className="brand" aria-label="NeuroVest home">
          <span className="brandMark">N</span>

          <span className="brandText">
            Neuro<span>Vest</span>
          </span>
        </Link>

        <nav className="desktopNav" aria-label="Main navigation">
          <a href="#product">Product</a>
          <a href="#safety">Safety</a>
          <a href="#how-it-works">How it works</a>
          <a href="#pricing">Pricing</a>
        </nav>

        <div className="navActions">
          <Link href="/login" className="signIn">
            Sign in
          </Link>

          <Link href="/register" className="primaryButton smallButton">
            Get started
          </Link>
        </div>
      </header>


      <section className="hero">
        <div className="heroGlow heroGlowOne" />
        <div className="heroGlow heroGlowTwo" />

        <div className="heroContent">
          <div className="eyebrow">
            AI INVESTMENT INTELLIGENCE · BUILT AROUND CONTROL
          </div>

          <h1>
            Invest with intelligence.
            <span> Stay in control.</span>
          </h1>

          <p className="heroCopy">
            NeuroVest brings AI-powered research, portfolio intelligence,
            strategy analysis and risk-aware workflows together in one
            secured investing workspace.
          </p>

          <div className="heroActions">
            <Link href="/register" className="primaryButton">
              Get started
              <span aria-hidden="true">→</span>
            </Link>

            <a href="#safety" className="secondaryButton">
              See how you&apos;re protected
            </a>
          </div>

          <div className="heroTrust">
            <span>
              <CheckIcon />
              Human-controlled
            </span>

            <span>
              <CheckIcon />
              Paper-first workflows
            </span>

            <span>
              <CheckIcon />
              Risk-aware
            </span>

            <span>
              <CheckIcon />
              Traceable decisions
            </span>
          </div>
        </div>


        <div
          className="heroProduct neuroHeroProduct"
          aria-label="Neuro animated product companion"
        >
          <div className="neuroHeroHalo neuroHeroHaloOuter" />
          <div className="neuroHeroHalo neuroHeroHaloInner" />

          <div className="neuroHeroStatus">
            <span className="statusDot" />
            <span>NEURO · ACTIVE</span>
          </div>

          <NeuroHeroModel />

          <div className="neuroHeroMessage neuroHeroMessageTop">
            Understand your portfolio.
          </div>

          <div className="neuroHeroMessage neuroHeroMessageBottom">
            See risk before acting.
          </div>

          <div className="neuroHeroCaption">
            <span>AI INVESTMENT INTELLIGENCE</span>
            <strong>Built to inform. You stay in control.</strong>
          </div>
        </div>
      </section>


      <section className="trustStrip" aria-label="NeuroVest protections">
        <div>
          <strong>CONTROL</strong>
          <span>You authorize what matters.</span>
        </div>

        <div>
          <strong>RISK</strong>
          <span>Guardrails stay in the workflow.</span>
        </div>

        <div>
          <strong>TRANSPARENCY</strong>
          <span>Important decisions stay traceable.</span>
        </div>

        <div>
          <strong>SECURITY</strong>
          <span>Secure account access and protected boundaries.</span>
        </div>
      </section>


      <section className="section productSection" id="product">
        <div className="sectionIntro centered">
          <div className="eyebrow">ONE INVESTING WORKSPACE</div>

          <h2>
            Understand more.
            <span> Guess less.</span>
          </h2>

          <p>
            NeuroVest connects the information investors normally chase
            across different tools and puts it into one intelligent,
            risk-aware environment.
          </p>
        </div>

        <div className="capabilityGrid">
          {capabilities.map((capability) => (
            <article className="capabilityCard" key={capability.title}>
              <div className="cardEyebrow">{capability.eyebrow}</div>

              <h3>{capability.title}</h3>

              <p>{capability.description}</p>

              <div className="cardDetail">{capability.detail}</div>
            </article>
          ))}
        </div>
      </section>


      <section className="section neuroSection">
        <div className="neuroVisual">
          <div className="neuroOrb">
            <div className="orbCore">N</div>
          </div>

          <div className="questionCard questionOne">
            What changed in my portfolio?
          </div>

          <div className="questionCard questionTwo">
            Where is my risk concentrated?
          </div>

          <div className="questionCard questionThree">
            Explain this strategy.
          </div>
        </div>

        <div className="sectionIntro">
          <div className="eyebrow">MEET NEURO</div>

          <h2>
            AI that works with
            <span> investment context.</span>
          </h2>

          <p>
            Neuro is designed to help you explore markets, understand
            portfolio information, investigate strategies and make sense of
            the signals around your investments.
          </p>

          <ul className="featureList">
            <li>
              <CheckIcon />
              Ask questions about investment and portfolio context
            </li>

            <li>
              <CheckIcon />
              Bring research and market information into the conversation
            </li>

            <li>
              <CheckIcon />
              Explore strategy and risk information in plain language
            </li>

            <li>
              <CheckIcon />
              Keep AI inside governed product boundaries
            </li>
          </ul>

          <Link href="/chat" className="textLink">
            Explore Neuro
            <span>→</span>
          </Link>
        </div>
      </section>


      <section className="safetySection" id="safety">
        <div className="section safetyInner">
          <div className="sectionIntro safetyIntro">
            <div className="eyebrow warningEyebrow">
              SAFETY IS PART OF THE PRODUCT
            </div>

            <h2>
              Powerful intelligence.
              <span> Guardrails included.</span>
            </h2>

            <p>
              Financial AI should not require blind trust. NeuroVest is
              designed so risk controls, review and user authority remain
              part of the workflow.
            </p>
          </div>

          <div className="protectionGrid">
            {protections.map((protection) => (
              <article className="protectionCard" key={protection.title}>
                <div className="protectionIcon">
                  <CheckIcon />
                </div>

                <h3>{protection.title}</h3>

                <p>{protection.description}</p>
              </article>
            ))}
          </div>

          <div className="executionBanner">
            <div>
              <span className="statusDot" />
              <div>
                <small>EXECUTION STATUS</small>
                <strong>Controlled by design</strong>
              </div>
            </div>

            <p>
              Intelligence can inform a decision without automatically
              becoming one.
            </p>
          </div>
        </div>
      </section>


      <section className="section" id="how-it-works">
        <div className="sectionIntro centered">
          <div className="eyebrow">WHAT YOU GET</div>

          <h2>
            One product.
            <span> Six connected views.</span>
          </h2>

          <p>
            Move from understanding your portfolio to researching an idea,
            evaluating strategy and reviewing risk without losing context.
          </p>
        </div>

        <div className="productAreaGrid">
          {productAreas.map((area) => (
            <article className="productArea" key={area.number}>
              <span>{area.number}</span>
              <h3>{area.title}</h3>
              <p>{area.text}</p>
            </article>
          ))}
        </div>
      </section>


      <section className="section trustSection" id="security">
        <div className="trustCopy">
          <div className="eyebrow">TRUST SHOULD BE EARNED</div>

          <h2>
            Built for people who
            <span> want control.</span>
          </h2>

          <p>
            NeuroVest does not treat security, risk and observability as
            footnotes. They are part of how the product is designed to
            operate.
          </p>

                    <p className="trustNote">
            Designed so intelligence supports your decisions without taking
            control away from you.
          </p>
        </div>

        <div className="trustChecklist">
          {trustItems.map((item) => (
            <div key={item}>
              <CheckIcon />
              <span>{item}</span>
            </div>
          ))}
        </div>
      </section>


      <section className="section pricingSection" id="pricing">
        <div className="sectionIntro centered">
          <div className="eyebrow">NEUROVEST MEMBERSHIP</div>

          <h2>
            Start with intelligence.
            <span> Upgrade when you need more.</span>
          </h2>

          <p>
            Start with the core NeuroVest experience, then unlock advanced
            AI, research, strategy and connected portfolio intelligence as
            your needs grow.
          </p>

          
        </div>

        <div className="pricingGrid">
          <article className="priceCard">
            <div className="priceTop">
              <span>START</span>
              <h3>Explore NeuroVest</h3>
              <p>
                Get into the platform and experience the core investing
                workspace.
              </p>
            </div>

            <div className="price">
              <strong>Free</strong>
              <span>to get started</span>
            </div>

            <ul>
              <li><CheckIcon /> Core dashboard</li>
              <li><CheckIcon /> Market information</li>
              <li><CheckIcon /> Portfolio workspace</li>
              <li><CheckIcon /> Controlled product experience</li>
            </ul>

            <Link href="/register" className="secondaryButton fullButton">
              Get started
            </Link>
          </article>

          <article className="priceCard featuredPrice">
            <div className="popularTag">FULL INTELLIGENCE</div>

            <div className="priceTop">
              <span>NEUROVEST</span>
              <h3>Unlock the full platform</h3>
              <p>
                Advanced AI, strategy, research and connected investment
                intelligence.
              </p>
            </div>

            <div className="price">
              <strong>Early access</strong>
              <span>Full membership launching soon</span>
            </div>

            <ul>
              <li><CheckIcon /> Neuro AI intelligence</li>
              <li><CheckIcon /> Strategy analysis</li>
              <li><CheckIcon /> Research workflows</li>
              <li><CheckIcon /> Risk-aware tooling</li>
              <li><CheckIcon /> Brokerage-connected context</li>
            </ul>

            <Link href="/register" className="primaryButton fullButton">
              Join early access
            </Link>
          </article>
        </div>

        <p className="pricingDisclosure">
          Investing involves risk. NeuroVest provides technology and
          investment-intelligence tools; it does not guarantee investment
          performance or protection from market losses.
        </p>
      </section>


      <section className="finalCta">
        <div className="finalGlow" />

        <div className="eyebrow">INVESTING INTELLIGENCE, WITH CONTROL</div>

        <h2>
          See more of the picture.
          <span> Keep the final say.</span>
        </h2>

        <p>
          Bring your portfolio, research, AI and strategy intelligence into
          one controlled workspace.
        </p>

        <div className="heroActions centeredActions">
          <Link href="/register" className="primaryButton">
            Get started
            <span>→</span>
          </Link>

          <Link href="/login" className="secondaryButton">
            Sign in
          </Link>
        </div>
      </section>


      <footer className="footer">
        <div className="footerTop">
          <div className="footerBrand">
            <Link href="/" className="brand">
              <span className="brandMark">N</span>

              <span className="brandText">
                Neuro<span>Vest</span>
              </span>
            </Link>

            <p>
              AI-powered investment intelligence designed around
              understanding, risk awareness and user control.
            </p>
          </div>

          <div className="footerLinks">
            {footerGroups.map((group) => (
              <div key={group.title}>
                <strong>{group.title}</strong>

                {group.links.map(([label, href]) => (
                  <Link href={href} key={label}>
                    {label}
                  </Link>
                ))}
              </div>
            ))}
          </div>
        </div>

        <div className="footerBottom">
          <span>© 2026 NeuroVest. All rights reserved.</span>

          <span>
            Investing involves risk, including possible loss of principal.
          </span>
        </div>
      </footer>


      <style jsx global>{`
        :root {
          --background: #020713;
          --surface: #07101f;
          --surface-2: #0a1425;
          --border: rgba(148, 163, 184, 0.16);
          --border-bright: rgba(82, 229, 255, 0.28);
          --text: #f7fafc;
          --muted: #91a0b7;
          --cyan: #56e8ff;
          --cyan-soft: #8ff1ff;
          --purple: #c985ff;
          --yellow: #ffd84d;
          --green: #52e6a4;
        }

        * {
          box-sizing: border-box;
        }

        html {
          scroll-behavior: smooth;
        }

        body {
          margin: 0;
          background: var(--background);
          color: var(--text);
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

        button {
          font: inherit;
        }

        .siteShell {
          min-height: 100vh;
          overflow: hidden;
          background:
            radial-gradient(
              circle at 50% -20%,
              rgba(20, 76, 110, 0.18),
              transparent 36rem
            ),
            #020713;
        }

        .navigation {
          position: relative;
          z-index: 50;
          height: 76px;
          max-width: 1240px;
          margin: 0 auto;
          padding: 0 28px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          border-bottom: 1px solid rgba(255, 255, 255, 0.04);
        }

        .brand {
          display: inline-flex;
          align-items: center;
          gap: 11px;
          font-weight: 800;
        }

        .brandMark,
        .miniMark {
          display: grid;
          place-items: center;
          border: 1px solid rgba(86, 232, 255, 0.5);
          background:
            linear-gradient(
              145deg,
              rgba(86, 232, 255, 0.18),
              rgba(201, 133, 255, 0.08)
            );
          color: var(--cyan);
          box-shadow: 0 0 24px rgba(86, 232, 255, 0.1);
        }

        .brandMark {
          width: 34px;
          height: 34px;
          border-radius: 10px;
        }

        .brandText {
          font-size: 19px;
          letter-spacing: -0.03em;
        }

        .brandText span {
          color: var(--cyan);
        }

        .desktopNav {
          display: flex;
          align-items: center;
          gap: 32px;
          color: #9ca9bc;
          font-size: 14px;
        }

        .desktopNav a:hover,
        .signIn:hover {
          color: white;
        }

        .navActions {
          display: flex;
          align-items: center;
          gap: 18px;
        }

        .signIn {
          color: #aab5c6;
          font-size: 14px;
        }

        .primaryButton,
        .secondaryButton {
          min-height: 48px;
          padding: 0 21px;
          border-radius: 11px;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 12px;
          font-weight: 750;
          font-size: 14px;
          transition:
            transform 160ms ease,
            border-color 160ms ease,
            background 160ms ease;
        }

        .primaryButton {
          color: #001018;
          background:
            linear-gradient(
              135deg,
              #8ef4ff,
              #4fdcff
            );
          box-shadow:
            0 10px 35px rgba(71, 221, 255, 0.14);
        }

        .primaryButton:hover,
        .secondaryButton:hover {
          transform: translateY(-2px);
        }

        .secondaryButton {
          border: 1px solid rgba(148, 163, 184, 0.22);
          background: rgba(10, 20, 37, 0.58);
          color: #dbe5f2;
        }

        .smallButton {
          min-height: 39px;
          padding: 0 16px;
          border-radius: 9px;
        }

        .hero {
          position: relative;
          max-width: 1240px;
          min-height: 720px;
          margin: 0 auto;
          padding: 88px 28px 72px;
          display: grid;
          grid-template-columns: minmax(0, 0.88fr) minmax(560px, 1.12fr);
          gap: 72px;
          align-items: center;
        }

        .heroGlow {
          position: absolute;
          pointer-events: none;
          filter: blur(1px);
        }

        .heroGlowOne {
          width: 600px;
          height: 500px;
          left: -300px;
          top: 0;
          background:
            radial-gradient(
              circle,
              rgba(201, 133, 255, 0.08),
              transparent 65%
            );
        }

        .heroGlowTwo {
          width: 700px;
          height: 600px;
          right: -260px;
          top: 20px;
          background:
            radial-gradient(
              circle,
              rgba(86, 232, 255, 0.09),
              transparent 65%
            );
        }

        .heroContent {
          position: relative;
          z-index: 2;
        }

        .eyebrow,
        .cardEyebrow {
          color: var(--cyan);
          font-size: 11px;
          line-height: 1.4;
          font-weight: 850;
          letter-spacing: 0.22em;
        }

        .hero h1 {
          max-width: 650px;
          margin: 20px 0 24px;
          font-size: clamp(48px, 5.4vw, 78px);
          line-height: 0.99;
          letter-spacing: -0.055em;
        }

        .hero h1 span,
        .sectionIntro h2 span,
        .finalCta h2 span,
        .trustCopy h2 span {
          color: #a7b6ca;
        }

        .heroCopy {
          max-width: 610px;
          margin: 0;
          color: #9aa9be;
          font-size: 18px;
          line-height: 1.75;
        }

        .heroActions {
          margin-top: 34px;
          display: flex;
          flex-wrap: wrap;
          gap: 12px;
        }

        .heroTrust {
          margin-top: 29px;
          display: flex;
          flex-wrap: wrap;
          gap: 12px 22px;
          color: #8898ad;
          font-size: 12px;
        }

        .heroTrust span {
          display: inline-flex;
          align-items: center;
          gap: 7px;
        }

        .checkIcon {
          width: 18px;
          height: 18px;
          flex: 0 0 18px;
          border-radius: 50%;
          display: inline-grid;
          place-items: center;
          color: var(--green);
          background: rgba(82, 230, 164, 0.09);
          font-size: 11px;
          font-weight: 900;
        }

        .heroProduct {
          position: relative;
          z-index: 2;
          perspective: 1200px;
        }

        .productWindow {
          overflow: hidden;
          border: 1px solid rgba(86, 232, 255, 0.18);
          border-radius: 18px;
          background: #060d19;
          box-shadow:
            0 50px 120px rgba(0, 0, 0, 0.42),
            0 0 70px rgba(86, 232, 255, 0.05);
          transform: rotateY(-2deg) rotateX(1deg);
        }

        .windowHeader {
          height: 49px;
          padding: 0 16px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          border-bottom: 1px solid var(--border);
          background: rgba(255, 255, 255, 0.015);
          font-size: 11px;
        }

        .windowBrand {
          display: flex;
          align-items: center;
          gap: 8px;
          font-weight: 750;
        }

        .miniMark {
          width: 23px;
          height: 23px;
          border-radius: 7px;
          font-size: 10px;
        }

        .windowStatus {
          display: flex;
          align-items: center;
          gap: 7px;
          color: #8aa0b5;
          letter-spacing: 0.08em;
        }

        .windowStatus > span,
        .statusDot {
          width: 7px;
          height: 7px;
          border-radius: 50%;
          background: var(--green);
          box-shadow: 0 0 12px rgba(82, 230, 164, 0.65);
        }

        .windowBody {
          min-height: 390px;
          display: grid;
          grid-template-columns: 112px 1fr;
        }

        .previewSidebar {
          padding: 24px 12px;
          border-right: 1px solid var(--border);
          display: flex;
          flex-direction: column;
          gap: 8px;
          color: #63758c;
          font-size: 10px;
        }

        .previewSidebar div {
          padding: 9px 10px;
          border-radius: 7px;
        }

        .previewSidebar .sidebarActive {
          color: var(--cyan-soft);
          background: rgba(86, 232, 255, 0.07);
        }

        .previewMain {
          padding: 25px;
        }

        .previewTopline {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 20px;
        }

        .previewTopline > div {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }

        .previewTopline small,
        .metricCard small,
        .intelligenceHeader small,
        .executionBanner small {
          color: #65778d;
          font-size: 9px;
          letter-spacing: 0.1em;
        }

        .previewTopline strong {
          font-size: 20px;
        }

        .protectedBadge {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 7px 9px;
          border: 1px solid rgba(82, 230, 164, 0.15);
          border-radius: 999px;
          color: #82ddb5;
          background: rgba(82, 230, 164, 0.05);
          font-size: 9px;
        }

        .metricGrid {
          margin-top: 24px;
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 10px;
        }

        .metricCard {
          min-width: 0;
          padding: 15px;
          border: 1px solid var(--border);
          border-radius: 10px;
          background: #081120;
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .metricCard strong {
          overflow: hidden;
          text-overflow: ellipsis;
          font-size: 15px;
        }

        .metricCard span {
          color: #62748a;
          font-size: 9px;
        }

        .intelligenceCard {
          margin-top: 13px;
          padding: 18px;
          border: 1px solid rgba(86, 232, 255, 0.14);
          border-radius: 12px;
          background:
            linear-gradient(
              145deg,
              rgba(86, 232, 255, 0.035),
              rgba(201, 133, 255, 0.025)
            );
        }

        .intelligenceHeader {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .intelligenceHeader > div {
          display: flex;
          flex-direction: column;
          gap: 5px;
        }

        .intelligenceHeader strong {
          font-size: 12px;
        }

        .intelligenceHeader > span {
          padding: 6px 8px;
          border: 1px solid rgba(201, 133, 255, 0.18);
          border-radius: 7px;
          color: #d8adff;
          font-size: 9px;
        }

        .intelligenceCard p {
          margin: 22px 0 16px;
          color: #b4c0d0;
          font-size: 11px;
          line-height: 1.6;
        }

        .responseLine {
          display: flex;
          align-items: center;
          gap: 8px;
          color: #60748b;
          font-size: 9px;
        }

        .responseLine span {
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: var(--cyan);
          box-shadow: 0 0 10px rgba(86, 232, 255, 0.7);
        }

        .neuroHeroProduct {
          position: relative;
          min-height: 515px;
          overflow: hidden;
          isolation: isolate;
          display: block;
          background:
            radial-gradient(
              circle at 52% 45%,
              rgba(86, 232, 255, 0.11),
              transparent 34%
            ),
            linear-gradient(
              180deg,
              rgba(8, 18, 34, 0.93),
              rgba(3, 9, 20, 0.98)
            );
        }

        .neuroHeroProduct::before {
          content: "";
          position: absolute;
          inset: 0;
          z-index: 0;
          pointer-events: none;
          background:
            linear-gradient(
              90deg,
              rgba(86, 232, 255, 0.025) 1px,
              transparent 1px
            ),
            linear-gradient(
              rgba(86, 232, 255, 0.025) 1px,
              transparent 1px
            );
          background-size: 46px 46px;
          mask-image:
            linear-gradient(
              to bottom,
              transparent,
              black 25%,
              black 75%,
              transparent
            );
        }

        .neuroModelRoot {
          position: absolute;
          z-index: 3;
          inset: 22px 20px 26px;
        }

        .neuroModelStage,
        .neuroModelFallback {
          position: absolute;
          inset: 0;
        }

        .neuroModelStage {
          z-index: 2;
          pointer-events: none;
          opacity: 0;
          transition:
            opacity 420ms ease;
        }

        .neuroModelStageVisible {
          opacity: 1;
        }

        .neuroModelStageLoading {
          opacity: 0;
        }

        .neuroModelFallback {
          z-index: 1;
          display: grid;
          place-items: center;
          opacity: 1;
          transition:
            opacity 420ms ease;
        }

        .neuroModelFallbackVisible {
          opacity: 1;
        }

        .neuroModelFallbackHidden {
          opacity: 0;
          pointer-events: none;
        }

        .neuroModelStage model-viewer {
          --poster-color: transparent;
        }

        .neuroModelFallback img {
          width: min(92%, 520px);
          height: auto;
          object-fit: contain;
          filter:
            drop-shadow(
              0 32px 45px rgba(0, 0, 0, 0.4)
            );
        }

        .neuroHeroHalo {
          position: absolute;
          z-index: 1;
          left: 50%;
          top: 47%;
          translate: -50% -50%;
          border: 1px solid rgba(86, 232, 255, 0.1);
          border-radius: 50%;
          pointer-events: none;
        }

        .neuroHeroHaloOuter {
          width: 390px;
          height: 390px;
          box-shadow:
            0 0 90px rgba(86, 232, 255, 0.045);
        }

        .neuroHeroHaloInner {
          width: 260px;
          height: 260px;
          border-color: rgba(86, 232, 255, 0.16);
        }

        .neuroHeroStatus {
          position: absolute;
          z-index: 6;
          top: 20px;
          right: 22px;
          display: flex;
          align-items: center;
          gap: 8px;
          color: #8296ad;
          font-size: 9px;
          font-weight: 800;
          letter-spacing: 0.14em;
        }

        .statusDot {
          width: 7px;
          height: 7px;
          border-radius: 50%;
          background: #56e6a6;
          box-shadow:
            0 0 14px rgba(86, 230, 166, 0.8);
        }

        .neuroHeroMessage {
          position: absolute;
          z-index: 6;
          padding: 10px 13px;
          border:
            1px solid rgba(86, 232, 255, 0.14);
          border-radius: 10px;
          color: #9cb0c7;
          background: rgba(4, 12, 25, 0.78);
          backdrop-filter: blur(10px);
          font-size: 10px;
          box-shadow:
            0 18px 40px rgba(0, 0, 0, 0.25);
        }

        .neuroHeroMessageTop {
          left: 22px;
          top: 56px;
        }

        .neuroHeroMessageBottom {
          right: 22px;
          bottom: 76px;
        }

        .neuroHeroCaption {
          position: absolute;
          z-index: 6;
          left: 22px;
          right: 22px;
          bottom: 18px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 20px;
          color: #687d94;
          font-size: 8px;
          letter-spacing: 0.11em;
        }

        .neuroHeroCaption strong {
          color: #aab9ca;
          font-size: 9px;
          font-weight: 600;
          letter-spacing: 0;
        }

        .trustStrip {
          max-width: 1184px;
          margin: 0 auto;
          padding: 0 28px 68px;
          display: grid;
          grid-template-columns: repeat(4, 1fr);
        }

        .trustStrip > div {
          min-height: 84px;
          padding: 19px 22px;
          border-top: 1px solid var(--border);
          border-bottom: 1px solid var(--border);
          border-right: 1px solid var(--border);
          display: flex;
          flex-direction: column;
          gap: 7px;
        }

        .trustStrip > div:first-child {
          border-left: 1px solid var(--border);
          border-radius: 12px 0 0 12px;
        }

        .trustStrip > div:last-child {
          border-radius: 0 12px 12px 0;
        }

        .trustStrip strong {
          color: #d8e3ef;
          font-size: 10px;
          letter-spacing: 0.16em;
        }

        .trustStrip span {
          color: #718298;
          font-size: 11px;
          line-height: 1.5;
        }

        .section {
          max-width: 1184px;
          margin: 0 auto;
          padding: 92px 28px;
        }

        .sectionIntro {
          max-width: 590px;
        }

        .sectionIntro.centered {
          margin: 0 auto;
          text-align: center;
        }

        .sectionIntro h2,
        .trustCopy h2,
        .finalCta h2 {
          margin: 17px 0 20px;
          font-size: clamp(38px, 4.2vw, 58px);
          line-height: 1.05;
          letter-spacing: -0.045em;
        }

        .sectionIntro p,
        .trustCopy p,
        .finalCta p {
          color: #9eacc0;
          font-size: 16px;
          line-height: 1.75;
        }

        .capabilityGrid {
          margin-top: 62px;
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 16px;
        }

        .capabilityCard {
          min-height: 320px;
          padding: 30px;
          border: 1px solid var(--border);
          border-radius: 17px;
          background:
            linear-gradient(
              160deg,
              rgba(10, 20, 37, 0.92),
              rgba(5, 11, 22, 0.8)
            );
        }

        .capabilityCard:nth-child(2) {
          border-color: rgba(86, 232, 255, 0.2);
        }

        .capabilityCard h3 {
          margin: 48px 0 16px;
          font-size: 27px;
          letter-spacing: -0.035em;
        }

        .capabilityCard p {
          margin: 0;
          color: #95a6ba;
          line-height: 1.7;
          font-size: 14px;
        }

        .cardDetail {
          margin-top: 26px;
          padding-top: 17px;
          border-top: 1px solid var(--border);
          color: #62758c;
          font-size: 10px;
          letter-spacing: 0.04em;
        }

        .neuroSection {
          display: grid;
          grid-template-columns: 1fr 0.85fr;
          gap: 100px;
          align-items: center;
        }

        .neuroVisual {
          position: relative;
          min-height: 520px;
          display: grid;
          place-items: center;
          border: 1px solid var(--border);
          border-radius: 24px;
          background:
            radial-gradient(
              circle at center,
              rgba(86, 232, 255, 0.07),
              transparent 44%
            ),
            #050b16;
        }

        .neuroOrb {
          width: 180px;
          height: 180px;
          border: 1px solid rgba(86, 232, 255, 0.2);
          border-radius: 50%;
          display: grid;
          place-items: center;
          box-shadow:
            0 0 80px rgba(86, 232, 255, 0.08),
            inset 0 0 45px rgba(201, 133, 255, 0.04);
        }

        .orbCore {
          width: 94px;
          height: 94px;
          border-radius: 30px;
          display: grid;
          place-items: center;
          color: var(--cyan);
          border: 1px solid rgba(86, 232, 255, 0.35);
          background: rgba(86, 232, 255, 0.06);
          font-size: 30px;
          font-weight: 850;
          box-shadow: 0 0 45px rgba(86, 232, 255, 0.12);
        }

        .questionCard {
          position: absolute;
          padding: 12px 16px;
          border: 1px solid var(--border);
          border-radius: 10px;
          color: #9eb0c5;
          background: rgba(7, 16, 31, 0.94);
          font-size: 11px;
          box-shadow: 0 18px 50px rgba(0, 0, 0, 0.25);
        }

        .questionOne {
          top: 85px;
          left: 32px;
        }

        .questionTwo {
          right: 26px;
          top: 175px;
        }

        .questionThree {
          left: 52px;
          bottom: 75px;
        }

        .featureList {
          margin: 28px 0 0;
          padding: 0;
          list-style: none;
          display: flex;
          flex-direction: column;
          gap: 14px;
          color: #a0aec0;
          font-size: 14px;
        }

        .featureList li {
          display: flex;
          gap: 10px;
          align-items: flex-start;
          line-height: 1.5;
        }

        .textLink {
          margin-top: 30px;
          display: inline-flex;
          align-items: center;
          gap: 12px;
          color: var(--cyan);
          font-size: 13px;
          font-weight: 750;
        }

        .safetySection {
          border-top: 1px solid rgba(255, 255, 255, 0.04);
          border-bottom: 1px solid rgba(255, 255, 255, 0.04);
          background:
            radial-gradient(
              circle at 50% 0,
              rgba(255, 216, 77, 0.035),
              transparent 36rem
            ),
            #040914;
        }

        .safetyInner {
          padding-top: 120px;
          padding-bottom: 120px;
        }

        .safetyIntro {
          max-width: 720px;
        }

        .warningEyebrow {
          color: var(--yellow);
        }

        .protectionGrid {
          margin-top: 60px;
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 14px;
        }

        .protectionCard {
          min-height: 245px;
          padding: 26px;
          border: 1px solid var(--border);
          border-radius: 15px;
          background: rgba(8, 16, 30, 0.76);
        }

        .protectionIcon {
          margin-bottom: 48px;
        }

        .protectionCard h3 {
          margin: 0 0 12px;
          font-size: 17px;
        }

        .protectionCard p {
          margin: 0;
          color: #8d9eb3;
          font-size: 12px;
          line-height: 1.7;
        }

        .executionBanner {
          margin-top: 15px;
          padding: 20px 24px;
          border: 1px solid rgba(82, 230, 164, 0.14);
          border-radius: 13px;
          background: rgba(82, 230, 164, 0.025);
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 30px;
        }

        .executionBanner > div {
          display: flex;
          align-items: center;
          gap: 13px;
        }

        .executionBanner > div > div {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .executionBanner strong {
          font-size: 13px;
        }

        .executionBanner p {
          margin: 0;
          color: #899bb0;
          font-size: 11px;
        }

        .productAreaGrid {
          margin-top: 60px;
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          border-top: 1px solid var(--border);
          border-left: 1px solid var(--border);
        }

        .productArea {
          min-height: 220px;
          padding: 28px;
          border-right: 1px solid var(--border);
          border-bottom: 1px solid var(--border);
        }

        .productArea > span {
          color: #51647b;
          font-size: 10px;
          letter-spacing: 0.14em;
        }

        .productArea h3 {
          margin: 45px 0 10px;
          font-size: 20px;
        }

        .productArea p {
          margin: 0;
          color: #8d9eb3;
          font-size: 12px;
          line-height: 1.65;
        }

        .trustSection {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 100px;
          align-items: center;
        }

        .trustCopy {
          max-width: 520px;
        }

        .trustChecklist {
          border: 1px solid var(--border);
          border-radius: 17px;
          overflow: hidden;
          background: rgba(7, 16, 31, 0.65);
        }

        .trustChecklist > div {
          min-height: 65px;
          padding: 0 22px;
          display: flex;
          align-items: center;
          gap: 13px;
          border-bottom: 1px solid var(--border);
          color: #a3b0c1;
          font-size: 13px;
        }

        .trustChecklist > div:last-child {
          border-bottom: 0;
        }

        .pricingSection {
          padding-top: 100px;
        }

        .trustNote {
          margin-top: 28px;
          max-width: 470px;
          color: #73869d;
          font-size: 12px;
          line-height: 1.7;
        }

        .pricingGrid {
          max-width: 820px;
          margin: 40px auto 0;
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 16px;
        }

        .priceCard {
          position: relative;
          min-height: 510px;
          padding: 31px;
          border: 1px solid var(--border);
          border-radius: 18px;
          background: #07101e;
          display: flex;
          flex-direction: column;
        }

        .featuredPrice {
          border-color: rgba(86, 232, 255, 0.32);
          box-shadow: 0 30px 80px rgba(86, 232, 255, 0.05);
        }

        .popularTag {
          position: absolute;
          right: 20px;
          top: 20px;
          padding: 6px 8px;
          border-radius: 6px;
          color: var(--cyan);
          background: rgba(86, 232, 255, 0.08);
          font-size: 8px;
          font-weight: 850;
          letter-spacing: 0.12em;
        }

        .priceTop > span {
          color: #64768d;
          font-size: 9px;
          font-weight: 800;
          letter-spacing: 0.15em;
        }

        .priceTop h3 {
          margin: 14px 0 10px;
          font-size: 22px;
        }

        .priceTop p {
          margin: 0;
          min-height: 68px;
          color: #90a1b6;
          font-size: 12px;
          line-height: 1.65;
        }

        .price {
          margin: 32px 0;
          padding: 25px 0;
          border-top: 1px solid var(--border);
          border-bottom: 1px solid var(--border);
          display: flex;
          flex-direction: column;
          gap: 5px;
        }

        .price strong {
          font-size: 25px;
        }

        .price span {
          color: #64768d;
          font-size: 10px;
        }

        .priceCard ul {
          margin: 0 0 28px;
          padding: 0;
          list-style: none;
          display: flex;
          flex-direction: column;
          gap: 12px;
          color: #94a3b7;
          font-size: 12px;
        }

        .priceCard li {
          display: flex;
          align-items: center;
          gap: 9px;
        }

        .fullButton {
          width: 100%;
          margin-top: auto;
        }

        .pricingDisclosure {
          max-width: 720px;
          margin: 28px auto 0;
          color: #53667d;
          text-align: center;
          font-size: 10px;
          line-height: 1.6;
        }

        .finalCta {
          position: relative;
          max-width: 1128px;
          margin: 32px auto 82px;
          padding: 72px 30px;
          overflow: hidden;
          border: 1px solid rgba(86, 232, 255, 0.16);
          border-radius: 24px;
          background: #06101e;
          text-align: center;
        }

        .finalGlow {
          position: absolute;
          width: 700px;
          height: 300px;
          top: -220px;
          left: 50%;
          transform: translateX(-50%);
          background:
            radial-gradient(
              circle,
              rgba(86, 232, 255, 0.14),
              transparent 68%
            );
        }

        .finalCta > *:not(.finalGlow) {
          position: relative;
          z-index: 2;
        }

        .finalCta h2 {
          max-width: 720px;
          margin-left: auto;
          margin-right: auto;
        }

        .finalCta p {
          max-width: 580px;
          margin-left: auto;
          margin-right: auto;
        }

        .centeredActions {
          justify-content: center;
        }

        .footer {
          max-width: 1184px;
          margin: 0 auto;
          padding: 65px 28px 35px;
          border-top: 1px solid var(--border);
        }

        .footerTop {
          display: grid;
          grid-template-columns: 0.8fr 1.2fr;
          gap: 100px;
        }

        .footerBrand p {
          max-width: 330px;
          margin-top: 20px;
          color: #697b91;
          font-size: 12px;
          line-height: 1.7;
        }

        .footerLinks {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 35px;
        }

        .footerLinks > div {
          display: flex;
          flex-direction: column;
          align-items: flex-start;
          gap: 12px;
        }

        .footerLinks strong {
          margin-bottom: 7px;
          color: #d4dfeb;
          font-size: 11px;
        }

        .footerLinks a {
          color: #687b91;
          font-size: 11px;
        }

        .footerLinks a:hover {
          color: var(--cyan);
        }

        .footerBottom {
          margin-top: 60px;
          padding-top: 25px;
          border-top: 1px solid var(--border);
          display: flex;
          justify-content: space-between;
          gap: 30px;
          color: #4f6177;
          font-size: 9px;
        }

        @media (max-width: 1000px) {
          .desktopNav {
            display: none;
          }

          .hero {
            grid-template-columns: 1fr;
            padding-top: 80px;
          }

          .heroContent {
            max-width: 760px;
          }

          .neuroHeroProduct {
            min-height: 440px;
          }

          .neuroModelRoot {
            inset: 24px 4px 44px;
          }

          .neuroHeroMessageTop {
            left: 14px;
            top: 48px;
          }

          .neuroHeroMessageBottom {
            right: 14px;
            bottom: 70px;
          }

          .neuroHeroCaption {
            left: 14px;
            right: 14px;
          }

          .heroProduct {
            max-width: 760px;
          }

          .trustStrip {
            grid-template-columns: repeat(2, 1fr);
          }

          .trustStrip > div:first-child,
          .trustStrip > div:last-child {
            border-radius: 0;
          }

          .capabilityGrid,
          .protectionGrid {
            grid-template-columns: repeat(2, 1fr);
          }

          .neuroSection,
          .trustSection {
            grid-template-columns: 1fr;
            gap: 60px;
          }

          .neuroVisual {
            order: 2;
          }

          .productAreaGrid {
            grid-template-columns: repeat(2, 1fr);
          }

          .footerTop {
            grid-template-columns: 1fr;
            gap: 50px;
          }
        }

        @media (max-width: 680px) {
          .navigation {
            height: 66px;
            padding: 0 18px;
          }

          .brandText {
            font-size: 16px;
          }

          .brandMark {
            width: 30px;
            height: 30px;
          }

          .signIn {
            display: none;
          }

          .hero {
            min-height: auto;
            padding: 70px 18px 65px;
            gap: 55px;
          }

          .hero h1 {
            font-size: 49px;
          }

          .heroCopy {
            font-size: 16px;
          }

          .heroActions {
            flex-direction: column;
          }

          .heroActions a {
            width: 100%;
          }

          .heroTrust {
            display: grid;
            grid-template-columns: 1fr 1fr;
          }

          .productWindow {
            transform: none;
          }

          .windowBody {
            grid-template-columns: 1fr;
          }

          .previewSidebar {
            display: none;
          }

          .previewMain {
            padding: 17px;
          }

          .metricGrid {
            grid-template-columns: 1fr;
          }

          .metricCard:nth-child(3) {
            display: none;
          }

          .trustStrip {
            padding: 0 18px 65px;
            grid-template-columns: 1fr;
          }

          .trustStrip > div {
            border-left: 1px solid var(--border);
          }

          .section {
            padding: 85px 18px;
          }

          .sectionIntro h2,
          .trustCopy h2,
          .finalCta h2 {
            font-size: 39px;
          }

          .capabilityGrid,
          .protectionGrid,
          .productAreaGrid,
          .pricingGrid {
            grid-template-columns: 1fr;
          }

          .capabilityCard {
            min-height: 280px;
          }

          .capabilityCard h3 {
            margin-top: 50px;
          }

          .neuroVisual {
            min-height: 440px;
          }

          .questionOne {
            left: 14px;
          }

          .questionTwo {
            right: 14px;
          }

          .questionThree {
            left: 22px;
          }

          .executionBanner {
            align-items: flex-start;
            flex-direction: column;
          }

          .finalCta {
            margin: 30px 18px 80px;
            padding: 70px 22px;
          }

          .footer {
            padding-left: 18px;
            padding-right: 18px;
          }

          .footerLinks {
            grid-template-columns: 1fr 1fr;
          }

          .footerBottom {
            flex-direction: column;
          }
        }
      `}</style>
          
    </main>
  );
}
