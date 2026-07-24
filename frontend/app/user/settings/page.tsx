import PageHeader from "../../../components/app-shell/PageHeader";

import {
  Panel,
  StatusBadge,
  StatusMessage,
} from "../../../components/ui";

const settingsAreas = [
  {
    title: "Profile & Identity",
    description:
      "Name, email address, profile image, time zone, and language preferences.",
  },
  {
    title: "Activity Metrics",
    description:
      "Recent account activity, login history, usage information, and pending actions.",
  },
  {
    title: "Billing & Subscriptions",
    description:
      "Current plan, renewal information, payment methods, and invoice history.",
  },
  {
    title: "Security & Authentication",
    description:
      "Password management and authenticated session controls.",
  },
  {
    title: "Notifications",
    description:
      "Email, SMS, and in-application notification preferences.",
  },
  {
    title: "Support & Documentation",
    description:
      "Administrative support requests, ticket tracking, and platform documentation.",
  },
];

export default function UserSettingsPage() {
  return (
    <main className="space-y-6">
      <PageHeader
        eyebrow="NeuroVest Account"
        title="Settings."
        description="Manage your account identity, security, subscription, notifications, and support access."
        badge={
          <StatusBadge tone="info">
            Personal account
          </StatusBadge>
        }
      />

      <StatusMessage tone="info">
        Settings capabilities will be connected only to qualified,
        server-authoritative account services. No fabricated billing,
        session, notification, or support records are displayed.
      </StatusMessage>

      <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        {settingsAreas.map((area) => (
          <Panel
            key={area.title}
            variant="elevated"
            className="p-6"
          >
            <h2 className="text-xl font-black text-white">
              {area.title}
            </h2>

            <p className="mt-3 text-sm leading-7 text-slate-400">
              {area.description}
            </p>
          </Panel>
        ))}
      </section>
    </main>
  );
}
