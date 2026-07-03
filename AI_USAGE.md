# AI Usage

## Tools Used

- ChatGPT/Codex for code review, implementation help, and test ideas.
- Terminal commands for running backend tests and frontend build/lint checks.

## Useful Prompts

1. "Check if the project meets all project requirements. Make a deep look."
   This helped identify gaps against the brief rather than only checking whether
   the app ran.

2. "Make it align with the rules in the PDF and make it ready."
   This helped focus the work on the business-rule interpretation, required
   documentation, and submission readiness.

## Where AI Got It Wrong

An early frontend implementation looked plausible but had a typo in the approved
leave filter: `satus` instead of `status`. That meant approved leave did not
render even though the backend returned it correctly. Linting and a manual
requirements review caught the issue.
