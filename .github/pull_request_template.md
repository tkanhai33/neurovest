# NeuroVest Change Review

## Change classification

- [ ] Documentation only
- [ ] Frontend presentation
- [ ] Backend behavior
- [ ] Authentication or authorization
- [ ] AI, prompt, context, or model behavior
- [ ] Market-data or portfolio behavior
- [ ] Risk, strategy, or execution behavior
- [ ] Database schema or migration
- [ ] CI, deployment, infrastructure, or security

## Summary

Describe exactly what changed and why.

## Existing architecture boundary

Identify the existing stack, layer, service, route, or contract that owns this change.

Do not introduce a parallel service, duplicate runtime, alternate route, or new architectural layer unless the existing architecture cannot safely own the behavior and the change is explicitly approved.

## Safety impact

- [ ] No live brokerage capability was enabled.
- [ ] No autonomous deployment or source mutation was enabled.
- [ ] No risk gate, kill switch, approval boundary, or authorization boundary was bypassed.
- [ ] No secret, password, raw token, credential, or protected user data was added to source control.
- [ ] Paper, simulation, locked, and emergency-stop behavior remains fail-closed.
- [ ] AI output remains advisory unless a separately qualified control explicitly permits an action.

## Data and migration impact

- [ ] No database change
- [ ] Forward migration included
- [ ] Rollback or recovery procedure included
- [ ] Existing data compatibility verified
- [ ] Sensitive-data retention and logging reviewed

Describe any data impact:

## Verification performed

List exact commands and results.

```text
Command:
Result:
Required qualification
 Relevant focused tests passed
 Full affected-stack tests passed
 Application import passed
 Architecture or import-cycle qualification passed where applicable
 Runtime qualification completed where behavior changed
 Failure-path behavior was tested
 Archive or recovery evidence was created before mutation
Release disposition
 Development only
 Controlled early-user candidate
 Production candidate
 Live brokerage — NOT APPROVED
 AI autonomy — NOT APPROVED
Reviewer notes

Record unresolved risks, follow-up stages, and explicit approval boundaries.
