# Release Checklist — `v0.3.0`

## Code + docs
- [ ] main is clean
- [ ] README reflects final release state
- [ ] CHANGELOG updated
- [ ] release notes finalized
- [ ] demo walkthrough finalized

## Validation
- [ ] backend tests pass
- [ ] web build passes
- [ ] Docker stack boots cleanly
- [ ] seed script works
- [ ] dashboard/customer/invoice pages load cleanly

## Release hygiene
- [ ] merge release-prep PR(s)
- [ ] run `./scripts/prepare-release.sh v0.3.0` (or `./scripts/predeploy-rehearsal.sh` for full morning rehearsal)
- [ ] create tag `v0.3.0`
- [ ] publish GitHub Release

## Deploy (preferred)
- [ ] Render blueprint/config committed
- [ ] hosted frontend reachable
- [ ] hosted backend reachable
- [ ] demo data path works in hosted env or is clearly documented as follow-up
- [ ] custom domain configured if straightforward

## Non-blocking if time slips
- [ ] custom domain under omaression.com
- [ ] extra visual polish beyond obvious cleanup
