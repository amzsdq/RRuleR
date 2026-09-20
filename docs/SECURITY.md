# Public-Repository Security Boundary

RRuleR is intentionally public. Public visibility is an architectural constraint, not an afterthought.

## Never persist

- API keys, tokens, passwords, app passwords;
- browser cookies, storage state, authentication headers;
- private ChatGPT conversation content;
- private-repository source or issue content;
- personal or sensitive user data;
- secret-bearing Actions logs or artifacts.

## Allowed durable forms

- public-safe policies and specifications;
- opaque identifiers that are not credentials;
- hashes and public commit SHAs;
- sanitized status/evidence summaries;
- public URLs and public repository references;
- machine state that contains no secret or private payload.

## Actions

- default workflow permissions should be minimal;
- individual workflows should declare the smallest required `permissions`;
- third-party Actions should be pinned according to repository security policy;
- untrusted fork code must not receive privileged write/secrets context;
- do not place authentication/session material into repository secrets merely because the secret store itself is encrypted if the workflow design does not require it.

## Reference repositories

A private/reference repository may be read only when explicitly allowed, but its private contents must not be copied into RRuleR. Persist only generic public-safe conclusions or opaque references when necessary.

## Incident rule

If sensitive material is accidentally committed, deleting the current file is insufficient because Git history may preserve it. Treat the repository as exposed and rotate/revoke the credential first, then perform history remediation appropriate to the incident.

## Design consequence

Any RRuleR feature that requires secret-bearing persistent state must use an external private storage boundary rather than weakening this public-safe invariant.
