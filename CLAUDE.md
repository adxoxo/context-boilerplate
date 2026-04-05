# CLAUDE.md

<!--
  HOW THIS FILE WORKS
  ───────────────────
  There are two versions of this file:

  1. BLANK (this file) — kept in your personal boilerplate repo.
     Copy it into every new project root before you start.

  2. FILLED — generated during the brainstorm phase by telling Claude Code:
     "Let's brainstorm a new project. Ask me everything you need,
      then generate a filled CLAUDE.md from our conversation."

  Claude Code reads this file automatically at the start of every session.
  The more complete it is, the better every session will be.

  WORKFLOW SUMMARY
  ────────────────
  Step 1 │ Brainstorm with Claude Code → it fills this file
           During brainstorm, answer the design feeling questions in Section 3A.
           That feeling drives everything: colors, fonts, spacing, motion.
  Step 2 │ Drop screenshots in /references → run: python extract_design_tokens.py
           The script reads your design feeling from this file and uses it as a lens.
  Step 3 │ Tell Claude Code: "Read CLAUDE.md and start Phase 1"
  Step 4 │ Each new session: "Read CLAUDE.md, today we're doing [X]"
-->

---

## 1. PROJECT CONTEXT

**Name:**
**Type:**
**Users:**
**Core problem solved:**
**Stack:**
**Current phase:**

---

## 2. ARCHITECTURE

**Folder structure:**
```
src/
  app/            # Next.js App Router pages
  components/
    ui/           # shadcn/ui primitives — do not modify
    shared/       # reusable app-level components
    [feature]/    # feature-scoped components
  lib/            # utils, helpers, constants
  hooks/          # custom React hooks
  services/       # API calls, external integrations
  types/          # shared TypeScript types
```

**Key decisions:**
**API pattern:**
**Auth:**
**State management:**

---

## 3. DESIGN SYSTEM

<!--
  SECTION 3A must be filled during the brainstorm phase — before screenshots,
  before tokens, before any code. The feeling comes first.
  Section 3B is filled after running extract_design_tokens.py.
-->

### 3A. Design Feeling
<!--
  These questions are what a designer asks before touching any tool.
  Answer them during brainstorm. extract_design_tokens.py reads this
  section and uses it as a lens when analyzing your reference screenshots.

  If you're unsure, describe it like you're explaining the vibe of a place,
  a song, or a brand you admire. Specificity beats accuracy here.
-->

**What feeling should the user have the moment they open this app?**
<!-- e.g. "Calm and in control, like opening a well-organized notebook" -->
<!-- e.g. "Energized, like a dashboard that takes you seriously" -->
<!-- e.g. "Warm and welcoming, like a local cafe that knows your order" -->

**What emotion should the design never trigger?**
<!-- e.g. "Never feel corporate or cold" -->
<!-- e.g. "Never feel cluttered or overwhelming" -->
<!-- e.g. "Never feel cheap or amateur" -->

**If this app were a physical place, what would it be?**
<!-- e.g. "A minimalist co-working space in Tokyo" -->
<!-- e.g. "A specialty coffee shop with exposed concrete and warm lighting" -->
<!-- e.g. "A clean hospital — trustworthy, precise, no unnecessary decoration" -->

**Pick one word that should define the visual personality:**
<!-- e.g. Precise / Warm / Bold / Playful / Elegant / Raw / Calm / Sharp -->

**Reference brands or products whose aesthetic you admire for this project:**
<!-- e.g. "Linear for the density and precision, Notion for the calm, Stripe for the trust" -->
<!-- These are separate from your screenshot references — this is about feeling, not copying -->

**Light, dark, or both?**
<!-- This affects every token Gemini extracts -->

---

### 3B. Tokens
<!--
  Filled automatically after running: python extract_design_tokens.py
  The script reads Section 3A above and passes it to Gemini as context.
  Paste the printed summary here after running.
-->

**Colors:**
```
primary:
secondary:
accent:
background:
surface:
border:
text-primary:
text-secondary:
text-muted:
error:
success:
```

**Typography:**
```
heading font:
body font:
size scale:    xs=12  sm=14  base=16  lg=18  xl=20  2xl=24  3xl=30  4xl=36
weight scale:  normal=400  medium=500  semibold=600  bold=700
```

**Spacing / Radius / Shadows:**
```
spacing:    xs=4  sm=8  md=16  lg=24  xl=32  2xl=48
radius:     sm=6  md=10  lg=16  xl=24  full=9999
shadow-sm:
shadow-md:
shadow-lg:
```

---

### 3C. Mandatory UI Rules
1. Design tokens only — never hardcode colors, sizes, or spacing
2. Every interactive element must have: hover, focus-visible, active, disabled states
3. All transitions: `transition-all duration-200 ease-in-out`
4. Cards: `rounded-xl border border-border bg-surface shadow-sm`
5. Minimum padding on any container: `p-4`
6. Max 3 font sizes per view
7. Every async action needs a loading state (Skeleton or spinner)
8. Every empty data state needs: icon + message + CTA
9. Mobile-first. Every component must be responsive.
10. Lucide React for all icons — no mixing libraries

### 3D. Anti-Patterns (NEVER)
- Hardcoded color values
- Pure #000 or #fff backgrounds
- Purple gradients on white (generic AI look)
- Inter, Roboto, Arial as heading font
- Missing hover / focus / disabled states
- Inline styles — Tailwind classes only
- Mixing component or icon libraries
- Any visual choice that contradicts the design feeling in Section 3A

### 3E. Gold Standard Component
<!-- Fill after your first polished component exists -->
<!-- e.g. src/components/shared/LoyaltyCard.tsx -->
<!-- Every new component should match this quality bar -->

---

## 4. CODING STANDARDS

**Language:** TypeScript strict mode. No `any`. All shared types in `src/types/`.

**Component structure:**
```tsx
interface Props {
  // explicit types
}

export function ComponentName({ prop1, prop2 }: Props) {
  // 1. hooks
  // 2. derived state
  // 3. handlers
  // 4. render
}
```

**Naming:**
- Components and types: PascalCase
- Files: kebab-case (`loyalty-card.tsx`)
- Hooks: `useFeatureName`
- Constants: SCREAMING_SNAKE_CASE
- No `I` prefix on interfaces

**Import order:** external libs → internal (@/) → relative → types

**Error handling:** Always handle async errors explicitly. Surface to user via toast or inline error state. No silent catches.

**No magic numbers.** Extract all to named constants.

---

## 5. TEST-DRIVEN DEVELOPMENT

### Stack
<!-- e.g. Vitest + React Testing Library + Playwright -->

### File Conventions
- Component tests: co-located as `ComponentName.test.tsx`
- E2E tests: `tests/e2e/feature-name.spec.ts`
- Shared test utilities: `src/lib/test-utils.ts`

### Coverage Priority
1. Critical business logic (calculations, auth flows, payment triggers)
2. Shared components — everything in `components/shared/`
3. API service functions — everything in `services/`
4. Core user journey E2E flows

### Component Test Checklist
```
□ Renders without crashing
□ Correct output given props
□ User interactions trigger correct handlers
□ Loading state renders correctly
□ Error state renders correctly
□ Empty state renders correctly
□ Keyboard navigation works
```

### Rules
- Test behavior, not implementation. Never assert on internal state.
- One concept per test.
- Use `userEvent` over `fireEvent` in RTL.
- Mock at the API boundary, not internal functions.
- E2E covers full user journeys, not individual components.

### TDD Flow per Feature
```
1. Write failing test for core behavior
2. Write minimum code to pass it
3. Refactor without breaking tests
4. Add edge case tests (empty, error, loading)
5. Add E2E for the full user flow
```

---

## 6. BUILD PLAN

<!-- Generated during brainstorm. Claude only works within current session scope. -->

**Phase 1 — MVP**
- [ ]
- [ ]
- [ ]

**Phase 2 —**
- [ ]

**Phase 3 —**
- [ ]

**Current session scope:**
<!-- Update this line at the start of every session -->
<!-- e.g. "Building the loyalty stamp card component and its Supabase integration" -->

---

## 7. DECISIONS LOG

| Decision | Rationale | Date |
|----------|-----------|------|
|          |           |      |

---

## 8. ENV VARIABLES

```
# Never hardcode. Reference only.
NEXT_PUBLIC_SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
NEXT_PUBLIC_APP_URL=
```

---

## 9. SESSION RULES FOR CLAUDE CODE

1. **Always read this entire file before doing anything.**
2. **Only work within the current session scope** (Section 6) unless explicitly told otherwise.
3. Before creating a new component — check if one exists in `components/shared/`.
4. Before adding a package — check `package.json` first.
5. After completing a feature — update the Build Plan checkboxes in Section 6.
6. Every UI component must pass all Mandatory UI Rules (Section 3C) before it's done.
7. Every visual decision must align with the design feeling in Section 3A.
8. When in doubt on design — match the Gold Standard component, not framework defaults.
9. Tests ship with every new component and service function. No exceptions.
10. If this file has empty sections, ask the user to fill them before proceeding.
