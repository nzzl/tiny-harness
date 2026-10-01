# Task

Status: locally verified; publication and remote CI pending

## Outcome and scope
Prepare and publish nzzl/tiny-harness as a public v0.1 release after addressing
adoption findings. Add tested Python/Node recipes and clarify snapshot/environment
boundaries. Preserve the small generic runner and existing required checks.
The repository was clean at c393cf0 when this task began.

The user explicitly authorized replacing personal author/committer email addresses
with their GitHub noreply address before publication. This overrides the contract's
usual prohibition on history rewriting for this specific metadata-only operation.
Preserve code/history structure and retain a local backup. Publish only sanitized
history. Publish the v0.1.0 tag only after all configured GitHub CI jobs pass.

## Acceptance criteria
- [x] Python example rejects editable-source false passes and external fallbacks.
- [x] Node example installs locked dependencies, rejects staged failures, and recovers.
- [x] Documentation states the inherited-environment boundary precisely.
- [x] Required lint/tests and separate Node example pass locally.
- [ ] Published author/committer email addresses use GitHub noreply.
- [ ] GitHub CI passes before tagging v0.1.0.

## Checkpoint
Prepared optional recipes, Python source-origin regressions, an offline npm fixture,
and a dedicated Node CI job. The runner still installs only its original five
files; adopting repositories explicitly select/configure their own checks.

Evidence: required lint and all 30 behavioral tests passed on macOS with Python
3.9.6 and 3.14.7. The separate npm recipe probe passed locally with Node 20/npm 10,
including offline locked installation and staged-failure/repaired-source cases.
Workflow YAML and local documentation links were checked.

Next: commit through the harness, back up and sanitize email metadata, then publish.
GitHub CI and the v0.1.0 tag are subsequent external steps; inspect the repository's
Actions results and tag for their final status. This checkpoint accompanies the
release-preparation commit and does not assert that remote validation has passed.
