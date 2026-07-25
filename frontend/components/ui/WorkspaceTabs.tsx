"use client";

import type {
  ReactNode,
} from "react";

export type WorkspaceTabItem<
  TabId extends string,
> = {
  id: TabId;
  label: string;
  description?: string;
  icon?: ReactNode;
};

type WorkspaceTabsProps<
  TabId extends string,
> = {
  items: readonly WorkspaceTabItem<TabId>[];
  activeId: TabId;
  onChange: (id: TabId) => void;
  label: string;
  className?: string;
};

export default function WorkspaceTabs<
  TabId extends string,
>({
  items,
  activeId,
  onChange,
  label,
  className = "",
}: WorkspaceTabsProps<TabId>) {
  return (
    <div
      role="tablist"
      aria-label={label}
      className={[
        "nv-workspace-tabs",
        className,
      ]
        .filter(Boolean)
        .join(" ")}
    >
      {items.map((item) => {
        const selected =
          item.id === activeId;

        return (
          <button
            key={item.id}
            type="button"
            role="tab"
            aria-selected={selected}
            className={[
              "nv-workspace-tab",
              selected
                ? "nv-workspace-tab-active"
                : "",
            ]
              .filter(Boolean)
              .join(" ")}
            onClick={() => {
              onChange(item.id);
            }}
          >
            {item.icon ? (
              <span
                aria-hidden="true"
                className="nv-workspace-tab-icon"
              >
                {item.icon}
              </span>
            ) : null}

            <span className="nv-workspace-tab-label">
              {item.label}
            </span>

            {item.description ? (
              <span className="nv-workspace-tab-description">
                {item.description}
              </span>
            ) : null}
          </button>
        );
      })}
    </div>
  );
}
