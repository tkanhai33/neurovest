# NeuroVest Global Design System

## Purpose

This contract defines the shared visual foundation for the User,
Administrator, and Developer workspaces.

The three workspaces may expose different navigation and capabilities,
but they must use the same layout geometry, typography hierarchy,
component language, interaction states, and responsive behavior.

## Core principles

1. Shared structure before page-specific styling.
2. Server-authoritative state must remain visually distinguishable from
   estimates, placeholders, and unavailable data.
3. Role differences use restrained accent treatment, not separate design
   systems.
4. Controls must expose clear hover, focus, active, loading, disabled,
   success, warning, and failure states.
5. Financial and operational information must prioritize legibility over
   decoration.
6. Reduced-motion preferences must be respected.
7. New pages must use shared primitives before introducing page-local
   visual patterns.

## Workspace hierarchy

All authenticated workspaces use:

- `AppShell`
- `WorkspaceContextBar`
- `RoleAwareWorkspaceNav`
- `PageContainer`
- `PageHeader`

Workspace roles:

- User: customer portfolio and account experience
- Administrator: identity, support, audit, and platform administration
- Developer: internal diagnostics, runtime state, graph, learning, and
  observability

## Canonical tokens

### Surfaces

- `--nv-bg-0`: deepest application background
- `--nv-bg-1`: primary application background
- `--nv-bg-2`: secondary application background
- `--nv-bg-3`: high-contrast inset background
- `--nv-bg-elevated`: elevated panel
- `--nv-bg-glass`: translucent shell surface
- `--nv-bg-muted`: subdued panel

### Text

- `--nv-text-strong`: headings and primary values
- `--nv-text`: normal content
- `--nv-text-muted`: descriptions and secondary values
- `--nv-text-subtle`: metadata and low-priority labels

### Semantic accents

- Cyan: product identity, active navigation, informational emphasis
- Violet: elevated/internal context
- Emerald: healthy/successful state
- Amber: caution, restricted state, pending action
- Red: failure, destructive action, denied state

Semantic color must communicate meaning. It must not be used randomly
for decoration.

### Geometry

- Small radius: controls and compact elements
- Medium radius: cards and inputs
- Large radius: panels and sections
- Extra-large radius: application shells and major hero surfaces

### Spacing

Page sections use a consistent vertical rhythm:

- Compact separation: `0.75rem`
- Component separation: `1rem`
- Section separation: `1.5rem`
- Major section separation: `2rem`

## Shared primitives

### PageContainer

Controls page width, responsive gutter, and vertical section rhythm.

### PageHeader

Provides workspace eyebrow, page title, description, badge, and actions.

### SectionHeader

Provides section eyebrow, heading, description, badge, and actions.

### Panel

Provides canonical background, border, radius, and elevation variants.

### MetricGrid

Provides consistent responsive stat-card geometry.

### WorkspaceTabs

Provides accessible tab navigation with shared active and inactive states.

### Button and Input

All actions and form controls use the shared Button and Input primitives
unless a documented interaction requires a specialized control.

## Page migration rule

Existing pages are migrated in this order:

1. Developer dashboard
2. User dashboard
3. Administrator dashboard
4. Authentication pages
5. Internal cards and workspace panels

Page migration must not alter API behavior, authorization, role policy,
portfolio ownership, order safety, or trading controls.

## Prohibited patterns

New code must not introduce:

- duplicate page shells
- separate role-specific design systems
- hard-coded application backgrounds where a token exists
- repeated panel class strings where `Panel` is appropriate
- repeated heading structures where `SectionHeader` is appropriate
- unlabelled icon-only actions
- missing keyboard focus states
- animated effects without reduced-motion handling
- fabricated operational or financial values

## Current normalization boundary

This stage establishes the contract and shared shell only.

It does not claim that every existing page has already been migrated.
