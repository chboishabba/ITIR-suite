# ITIR x SensibLaw Mode Switching, Everyday UI/UX, and Scenario Templates (2026-03-28)

## Purpose
Define the next product-layer refinement above the unified architecture:
- when the system should operate in strict vs light mode
- what the normal-user UI/UX should emphasize
- how common everyday scenarios should map into reusable templates

This note stays at the docs/product-contract layer.
It does not introduce new runtime behavior.

## Main Decision
The suite should remain one system with a bounded operating-mode switch rather
than splitting into separate products.

Mode affects:
- output density
- review strictness
- escalation thresholds
- interaction tone
- recommended-action surface

It does not change the core pipeline.

Bottom line:
- same system, two operating modes
- light mode:
  clarity and next step
- strict mode:
  obligation, SLA, escalation
- automatic switching:
  risk, time, conflict, evidence, and user state
- UI rule:
  simple by default, depth opt-in

## 1. Mode-Switching Logic
Use a bounded decision surface rather than ad hoc switching.

### Switch inputs
- risk severity
- deadline pressure
- institutional exposure
- evidence density
- trust fragility / retraumatization sensitivity
- user intent:
  prove / preserve / escalate / decide / organize

### Deterministic trigger reading
#### 1. Risk
- low:
  no meaningful harm risk -> light
- moderate:
  financial or reputational risk -> light by default, strict on demand
- high:
  safety, eviction, hard legal exposure, coercive loss -> strict

#### 2. Time pressure
- no deadline -> light
- known deadline under 72 hours -> strict for obligation handling at minimum
- imminent deadline under 24 hours -> strict end to end

#### 3. Conflict level
- no dispute -> light
- ambiguous disagreement -> hybrid
- active dispute or clear power asymmetry -> strict

#### 4. Evidence completeness
- sparse -> light:
  suggest and collect
- partial -> hybrid:
  structure and flag gaps
- strong / multi-source -> strict:
  promote, preserve, and act

#### 5. Trust state
- calm / exploratory -> light
- uncertain / overwhelmed -> hybrid:
  gentle surface with bounded structure
- distressed / mistrustful -> strict constraints:
  high abstention, explicit provenance, no over-assertion

### Safe override rule
If the system detects elevated risk while the user is in everyday mode, it
should recommend switching upward rather than silently staying light.

If the user wants a lighter interaction despite elevated structure, the system
may keep the interaction surface light while preserving a stricter internal
record.

### Mode decision matrix
| Risk | Time | Conflict | Evidence | Mode |
| --- | --- | --- | --- | --- |
| Low | Low | Low | Sparse | Light |
| Moderate | Low | Moderate | Partial | Hybrid |
| Moderate | Moderate | Moderate | Partial | Strict for obligations |
| High | Any | Any | Any | Strict |

### Behavioural differences
| Aspect | Light Mode | Strict Mode |
| --- | --- | --- |
| Output | Suggestions | Obligations: actor + time + fallback |
| Tone | Conversational | Neutral, precise, non-moralizing |
| Evidence | Optional linking | Mandatory provenance |
| Uncertainty | Softer surface | Explicit: candidate / disputed / abstain |
| Actions | Next best step | Required step + SLA + escalation |
| Governance | Minimal visible overhead | Full audit + escalation |

### Always-on guardrails
- no identity assertions without evidence
- no moralizing language
- no hidden assumptions
- abstain when uncertain
- local-first / privacy-preserving by default

## 1A. Mode Controller Product Spec
### Purpose
Select and enforce light, hybrid, or strict mode so the suite remains usable
for ordinary users while still becoming safety- and escalation-ready for
high-risk cases.

### Inputs
- risk level
- time pressure
- conflict level
- evidence completeness
- user state

### Outputs
- mode selection
- behavior profile:
  tone, depth, obligations
- UI configuration
- governance enforcement level

### Minimal deterministic logic
- if risk is high -> strict
- if time is urgent -> strict
- if conflict is adversarial -> strict
- if user state is distressed -> hybrid or strict with stronger safety
  constraints
- else -> light

### Behaviour profiles
#### Light
- short explanation
- one to three suggested actions
- minimal evidence surface

#### Hybrid
- structured explanation
- evidence links
- optional obligation preview

#### Strict
- obligations:
  actor + time + fallback
- explicit uncertainty
- audit trail

## 1B. Obligation Layer Product Spec
### Core primitive
`Obligation`

### Fields
- need
- responsible actor
- required action
- deadline
- status:
  open / in-progress / done / breached
- evidence links
- fallback actor
- escalation rule

### Behaviour
- created by alignment engine
- enforced only in hybrid / strict modes
- breach triggers escalation
- all changes logged for auditability

## 2. Everyday UI/UX Layer
The everyday surface should optimize for:
- low-friction input
- fast orientation
- one clear next step
- low moralizing / low bureaucratic tone

### Core everyday screens / surfaces
- home / quick capture:
  what happened, what matters, what outcome do you want
- understanding view:
  what this looks like, what likely matters, what is still unclear
- next-step view:
  one to three actions max, each with effort, expected outcome, confidence
- evidence view:
  progressive disclosure for sources, extracted facts, linked rules
- timeline / graph:
  simple timeline first, graph only on demand
- strict-mode panel:
  actor, action, deadline, fallback, escalation / document generation
- trust controls:
  why this, show alternatives, mark incorrect/incomplete, keep local/share

### UI/UX rules
- default to one recommended next step, not five equal options
- reveal depth progressively
- avoid legalistic or therapeutic over-framing unless the user requests it
- surface uncertainty clearly without paralysis
- make escalation paths visible but not constantly foregrounded
- default to light mode unless bounded triggers push upward
- always allow override

### Tone structure
Keep the visible answer split into:
- what I see
- possible interpretations
- what you can do next

### Primary flow
#### Normal/light-first flow
1. user inputs situation
2. system auto-selects mode
3. show:
   what this looks like, what matters, what to do next
4. optional:
   show evidence, switch to strict mode

#### Strict flow
1. system auto-switches or user elevates
2. show:
   obligations list, deadlines, escalation path
3. actions:
   generate document, notify actor, escalate

### Trust controls
Always visible:
- why this output
- show alternatives
- mark incorrect
- keep local / share

## 3. Common Everyday Scenario Templates
These templates reuse the same architecture with lighter inputs and outputs.

### A. Work / manager conversation
Typical input:
- we had a weird chat; not sure what they meant

Light output:
- likely interpretation:
  expectation mismatch or feedback signal
- what matters:
  role clarity and deliverables
- next steps:
  brief follow-up summary, ask for one to two concrete expectations, observe
  next interaction

Strict upgrade:
- obligation:
  clarify expectations in writing within 24 to 48 hours
- actor:
  user and manager
- fallback:
  HR or documented escalation

### B. Email / communication
Typical input:
- draft or received email

Light output:
- intent detection:
  inform, request, pushback
- risks:
  tone or ambiguity
- suggested reply:
  short and neutral

Strict upgrade:
- communication record
- commitment extraction:
  who agreed to what, by when

### C. Tenancy, everyday friction to dispute
Typical input:
- landlord came without notice

Light output:
- what matters:
  notice requirement and documentation
- next steps:
  log incident, send neutral clarification message, keep photos and records

Strict mode:
- obligation:
  landlord must comply with notice requirement
- deadline:
  before next entry attempt
- fallback:
  formal breach or tribunal path

### D. Money / bills
Typical input:
- got a fee I do not understand

Light output:
- categorize fee
- likely reasons
- next steps:
  ask for itemized explanation, check contract terms, set reminder

Strict upgrade:
- obligation:
  provider must explain or correct
- deadline and escalation:
  complaint pathway if not resolved

### E. Health / appointments
Typical input:
- doctor said X; not sure it fits

Light output:
- separate observation from diagnosis
- questions to ask next visit
- symptom tracking suggestion

Strict upgrade when harm risk appears:
- obligation:
  second opinion or continuity action
- contradiction capture
- complaint-path escalation if needed

### F. Personal planning
Typical input:
- I feel stuck this week

Light output:
- friction nodes:
  overload, ambiguity, delay
- three-step plan:
  today, tomorrow, later
- effort tags

Strict upgrade:
- normally none unless deadlines or risk thresholds appear

### G. Conflict, low to high
Typical input:
- argument with partner or roommate

Light output:
- facts vs interpretations split
- de-escalation steps
- clarifying questions

Strict upgrade when safety or legal risk appears:
- obligation mapping:
  boundaries and agreements
- documentation
- support contacts / escalation path

## 4. Mode and UX KPIs
### Mode KPIs
- correct auto-mode selection rate
- user mode override rate
- time to first action

### UX KPIs
- first-pass usefulness:
  this helped me
- actions taken within 24 hours
- rework due to tone mismatch

### Safety KPIs
- retraumatization flags
- escalation success rate
- obligation completion rate in strict mode

## 5. C4 Placement
Mode should be treated as an explicit cross-container decision, not a hidden
prompt preference.

- input interface:
  detects initial triggers such as risk, time pressure, and conflict
- alignment engine:
  confirms evidence/context basis for the chosen mode
- mode controller:
  selects light, hybrid, or strict
- obligation layer:
  active for strict and bounded hybrid cases
- output engine:
  renders guidance vs obligations
- governance layer:
  enforces guardrails and audit behavior

This means the mode controller is part of the documented container/application
view, not merely a UX setting.

## 6. Relationship To Case Libraries
The everyday templates do not replace the formal case libraries.

Instead:
- they sit above the same shared service flow
- they use lighter default thresholds
- they can escalate into stricter libraries when risk or institutional exposure
  increases

So the system shape becomes:
- shared architecture
- case libraries
- operating modes
- scenario templates on top

## 7. Best Next Milestone Refinement
The next bounded design pass should produce:
- one explicit mode-switch decision table
- one lightweight UI flow for everyday users
- three to five common everyday templates tied to the same obligation/action
  primitive
- one bounded mode-controller placement in the container/application view
- one starter KPI slice for mode correctness and UX usefulness
- one consolidated obligation object contract over need / actor / deadline /
  status / fallback

That is the smallest step that makes the system feel usable for ordinary users
without weakening the high-stakes architecture.

## Final System Summary
The documented system is now:
- one architecture
- two operating modes
- one explicit mode controller
- dual graph construction
- obligation execution for hybrid/strict handling
- governance and audit surfaces
- KPI-driven improvement loops

This is no longer only:
- a tool that helps people think

It is now documented as:
- a controlled service that turns human situations into structured,
  actionable, accountable outcomes
