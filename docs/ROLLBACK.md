# Safe rollback

Every published change is a Git commit on main. The Packet Tracer file, experiment inputs, measured CSVs, dashboard, and documentation are committed together in reviewable checkpoints.

Named checkpoint tags are also available: checkpoint-2026-10-13-evaluation points to the 30-seed and dashboard stage, and checkpoint-2026-10-13-iot points to the Packet Tracer IoT stage. Tags identify snapshots; they are not releases.

To inspect the checkpoints:

```bash
git log --oneline --decorate -10
git tag --list 'checkpoint-*'
git show --stat <commit>
```

To undo a published change while preserving the history of the shared branch, create a revert commit and push it:

```bash
git pull --ff-only
git revert <commit>
python3 -m unittest discover -s tests -v
git push origin main
```

To recover one file from an older commit without undoing other work:

```bash
git restore --source=<commit> -- packet_tracer/topology/AURA-UDP-campus.pkt
git diff -- packet_tracer/topology/AURA-UDP-campus.pkt
git add packet_tracer/topology/AURA-UDP-campus.pkt
git commit -m "restore: previous Packet Tracer topology"
git push origin main
```

Avoid force pushing the shared main branch. A release tag will be created only after the remaining Packet Tracer registration and endpoint checks pass.
