export default function PrivacyPage() {
  return (
    <main className="min-h-screen bg-[#020814] px-5 py-16 text-slate-200 sm:px-8">
      <article className="mx-auto max-w-3xl rounded-3xl border border-cyan-300/15 bg-slate-950/80 p-7 shadow-2xl sm:p-10">
        <p className="nv-eyebrow">NeuroVest beta</p>
        <h1 className="mt-3 text-3xl font-black text-white">
          Privacy Notice
        </h1>
        <p className="mt-4 text-sm leading-7 text-slate-400">
          Effective date: October 9, 2026. This is a plain-language
          beta privacy notice and should be reviewed by qualified
          Canadian privacy counsel before a public or paid launch.
        </p>

        <section className="mt-10 space-y-7 text-sm leading-7 text-slate-300">
          <div>
            <h2 className="text-lg font-bold text-white">
              What NeuroVest uses
            </h2>
            <p className="mt-2">
              NeuroVest uses account and authentication information
              needed to provide your workspace. If you choose to
              connect a supported brokerage account, NeuroVest may
              retrieve read-only portfolio information needed to
              display connected-account context.
            </p>
          </div>

          <div>
            <h2 className="text-lg font-bold text-white">
              Brokerage connections
            </h2>
            <p className="mt-2">
              Connected brokerage information is used for read-only
              portfolio intelligence. NeuroVest does not use this
              connection to place live brokerage orders. Paper-order
              simulation is separate from any connected account.
            </p>
          </div>

          <div>
            <h2 className="text-lg font-bold text-white">
              How information is used
            </h2>
            <p className="mt-2">
              Information is used to authenticate you, protect account
              access, provide owner-scoped views, operate support
              features, and maintain security and audit records.
            </p>
          </div>

          <div>
            <h2 className="text-lg font-bold text-white">
              Your choices
            </h2>
            <p className="mt-2">
              Brokerage connection is optional. For privacy questions
              or deletion requests, contact the NeuroVest team through
              the in-product support channel.
            </p>
          </div>

          <div>
            <h2 className="text-lg font-bold text-white">
              Beta status
            </h2>
            <p className="mt-2">
              NeuroVest is operating as a controlled beta. Features,
              data handling processes, and this notice may change as
              the product is refined.
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
