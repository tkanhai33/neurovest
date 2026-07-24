import PageHeader from "../../../components/app-shell/PageHeader";

import {
  Panel,
  StatCard,
  StatusBadge,
} from "../../../components/ui";

const plans = [
  {
    tier: "Free",
    price: "$0",
    features: [
      "Talk with Neuro",
      "Paper trading",
      "Simulation",
      "No broker connection",
    ],
  },
  {
    tier: "Tier 1",
    price: "$19.99",
    features: [
      "Everything in Free",
      "Broker connection",
      "Controlled trade access",
    ],
  },
  {
    tier: "Tier 2",
    price: "$29.99",
    features: [
      "Everything in Tier 1",
      "Built-in strategies",
      "Session AI training",
      "No custom uploads",
    ],
  },
  {
    tier: "Tier 3",
    price: "$39.99",
    features: [
      "Everything in Tier 2",
      "User-created strategies",
      "Custom strategy management",
    ],
  },
];

export default function AdminUserStatsPage() {
  return (
    <main className="space-y-6">

      <PageHeader
        eyebrow="NeuroVest Administration"
        title="User statistics."
        description="Subscription distribution, account activity, licensing and broker eligibility."
        badge={
          <StatusBadge tone="info">
            Administrative overview
          </StatusBadge>
        }
      />

      <section className="grid gap-4 md:grid-cols-4">

        <StatCard
          label="Registered Users"
          value="—"
          detail="Awaiting server statistics."
        />

        <StatCard
          label="Active Sessions"
          value="—"
          detail="Server authoritative."
        />

        <StatCard
          label="Broker Eligible"
          value="—"
          detail="Tier controlled."
        />

        <StatCard
          label="Monthly Revenue"
          value="—"
          detail="Subscription derived."
        />

      </section>

      <Panel
        variant="default"
        className="p-6"
      >
        <div className="flex items-center justify-between">
          <div>

            <p className="nv-eyebrow">
              Licensing
            </p>

            <h2 className="mt-3 text-2xl font-black text-white">
              Subscription structure
            </h2>

            <p className="mt-3 text-sm leading-7 text-slate-400">
              These plans define platform capability tiers. Values shown
              here are configuration, not live customer counts.
            </p>

          </div>

          <StatusBadge tone="success">
            Controlled licensing
          </StatusBadge>

        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-4">

          {plans.map((plan) => (

            <Panel
              key={plan.tier}
              variant="muted"
              className="p-5"
            >

              <p className="nv-eyebrow">
                {plan.tier}
              </p>

              <h3 className="mt-3 text-3xl font-black text-white">
                {plan.price}
              </h3>

              <p className="text-sm text-slate-500">
                per month
              </p>

              <ul className="mt-6 space-y-3 text-sm text-slate-300">

                {plan.features.map((feature) => (
                  <li key={feature}>
                    • {feature}
                  </li>
                ))}

              </ul>

            </Panel>

          ))}

        </div>

      </Panel>

    </main>
  );
}
