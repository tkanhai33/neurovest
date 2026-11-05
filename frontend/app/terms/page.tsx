export default function TermsPage() {
  return (
    <main className="min-h-screen bg-[#020814] px-5 py-16 text-slate-200 sm:px-8">
      <article className="mx-auto max-w-3xl rounded-3xl border border-cyan-300/15 bg-slate-950/80 p-7 shadow-2xl sm:p-10">
        <p className="nv-eyebrow">NeuroVest beta</p>
        <h1 className="mt-3 text-3xl font-black text-white">
          Beta Terms and Disclosures
        </h1>
        <p className="mt-4 text-sm leading-7 text-slate-400">
          Effective date: October 9, 2026. These are draft
          controlled-beta terms and disclosures. Obtain qualified legal
          and compliance review before offering NeuroVest publicly,
          charging users, or accepting investment.
        </p>

        <section className="mt-10 space-y-7 text-sm leading-7 text-slate-300">
          <div>
            <h2 className="text-lg font-bold text-white">
              Controlled beta
            </h2>
            <p className="mt-2">
              NeuroVest is an early-access product. Features may
              change, be interrupted, or be removed while the service
              is tested and improved.
            </p>
          </div>

          <div>
            <h2 className="text-lg font-bold text-white">
              No investment advice
            </h2>
            <p className="mt-2">
              NeuroVest provides software tools, information, and
              read-only analysis. It does not provide personalized
              investment, legal, tax, or financial advice.
            </p>
          </div>

          <div>
            <h2 className="text-lg font-bold text-white">
              Paper-only execution
            </h2>
            <p className="mt-2">
              NeuroVest order activity is paper simulation only.
              Connected brokerage data is read-only. NeuroVest does
              not place live brokerage orders through a connected
              brokerage account.
            </p>
          </div>

          <div>
            <h2 className="text-lg font-bold text-white">
              Appropriate use
            </h2>
            <p className="mt-2">
              Do not attempt to access another person’s account,
              bypass security controls, or use the service unlawfully.
              Beta access may be suspended to protect users and the
              platform.
            </p>
          </div>
        </section>

        <a
          href="/register"
          className="mt-10 inline-flex rounded-xl bg-cyan-300 px-4 py-2.5 text-sm font-black text-slate-950"
        >
          Back to registration
        </a>
      </article>
    </main>
  );
}
