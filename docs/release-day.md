# Release Day Notes

## Recommended order
1. Merge final release-prep PRs.
2. Run the predeploy rehearsal:
   - `chmod +x scripts/predeploy-rehearsal.sh`
   - `./scripts/predeploy-rehearsal.sh`
3. If desired, trigger the `Release Draft` GitHub Action.
4. Review the generated GitHub Release draft.
5. Create/push the `v0.3.0` tag if not already created.
6. Publish the GitHub Release.
7. Share the demo path (local or hosted URL).
## Non-blocking items
- custom domain setup
- extra cosmetic polish
- hosted demo data import refinement

## Blocking items
- failing tests
- broken web build
- broken demo bootstrap
- missing changelog or release notes
