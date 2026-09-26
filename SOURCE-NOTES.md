# Source review and design decisions

Inspected the user-supplied `ikigai-48-hour-test` kit and the global
`gated-build-workflow/SKILL.md` explicitly referenced by its setup instructions.
The kit is intentionally not a Git repository. All four supplied files were read:

| Actual source | Useful mechanism | Tiny Harness treatment |
| --- | --- | --- |
| `CLAUDE.md` | Short agreement, fresh verification, proportionality, behavior-focused tests, meaningful commit messages | Retained in a model-neutral contract; required check configuration replaces the unresolved verify-command placeholder. Local commits are autonomous. |
| `SETUP.md` | Explicit installation and optional end-of-turn test hook | Replaced model-specific global installation with an additive per-repository installer. Preserve all existing hooks/configuration; use one validation-and-commit command. |
| `SOLVING-PROMPT.md` | Inspect actual abstractions, bound scope, document assumptions and evidence | Retained in contract/task record. Removed assessment prompt, financial-product requirements, fixed endpoints, preferred architecture, fork/submission rules. |
| `DOMAIN-PACK-JVM-TRANSACTIONAL.md` | Test real guarantees and understand tool blind spots | Retained as general testing judgment. Removed JVM tools, money/transaction traps, mutation-score target, and domain-specific design rules. |
| Referenced `gated-build-workflow/SKILL.md` | Source-first reconnaissance, spec/acceptance criteria, failure analysis, continuous evidence, audit documentation claims | Combined spec/decisions/errors/recovery into one task record. Removed mandatory phase stops, operator-only verification, cold adversarial gate, cross-model audit, mutation gauntlet, arbitration, fixed commit ordering, and one-reopening closure ritual. |

No `AGENTS.md`, runnable script, installed hook, validation implementation, task
tracker, or license/attribution notice was present in the kit. Setup describes a
Stop hook to be written later; it does not supply one. The referenced global
skill is also Markdown. Consequently, **none of the inspected source controls
were executable enforcement**. The verify command in `CLAUDE.md` was unresolved.
There was no underlying application in this source directory to inspect.

Repeated phase approvals, new-decision reapproval, an optional full-suite Stop
hook, independent operator verification, and the formal audit protocol overlap
as controls on progression. They can make sense for supervised assessment, but
conflict with the requested low-friction autonomy. Tiny Harness keeps explicit
scope/acceptance and visible validation, and requests authorization only when
the action exceeds existing authorization or information genuinely blocks work.

Fresh staged snapshots address a specific reliability gap: a working tree can
pass while the proposed commit omits a fix or dependency. Configuration is
explicit and intentionally fails until populated. No path-based skip system,
approval state machine, model integration, or permanent validation receipt is
needed. Every check reruns before every wrapper-created commit. This trades
dependency setup time for an honest account of what was actually staged.

The source belongs to the user and is acknowledged here as the conceptual basis.
Tiny Harness is newly written; no source files, source-specific task text,
private paths, credentials, or global agent settings are redistributed. The
source had no supplied license to preserve; the MIT notice applies to the new
Tiny Harness implementation and documentation, not to the original kit. The
source directory and referenced skill were read only and left unchanged.
