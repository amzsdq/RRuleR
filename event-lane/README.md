# Event Wake Lab Lane

This branch/PR is a **non-production experimental event lane** for `control/event-wake-candidate.v1.json`.

Purpose: provide a dedicated GitHub pull-request commit-update surface for a future ChatGPT Work event-trigger feasibility test without coupling normal `main` control-state commits to wake events.

Rules:

- No secrets, credentials, session state, or private source material.
- The lane is inactive until an eligible Work event trigger is explicitly provisioned.
- Each test generation must use a unique event ID and expected authority epoch.
- At most one continuation generation may be outstanding.
- Only a current authority owner may emit the next test generation.
- Event acknowledgement alone must not emit another generation.
- Quarter-shift scheduled continuation remains the fallback during testing.
- On duplicate substantive execution, authority rollback, or event storm, stop emitting lane commits.

The PR should remain draft while used as a laboratory lane.
