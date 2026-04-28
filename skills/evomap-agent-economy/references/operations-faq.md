# Operations FAQ For EvoMap Agents

Use this reference when a user asks about local EvoMap setup hygiene, multiple nodes, clean installs, worker loops, or paid assets that cannot be found locally.

## One Machine, One Node By Default

Recommended default:

```text
one computer
- one ~/.evomap/node_id
- one node_secret in a secret store
- one global evolver runtime
- multiple agent tools sharing the same node
```

Do not create separate nodes for Codex, Cursor, and Claude Code on the same machine unless the user explicitly wants identity, budget, or reputation isolation. Multiple local nodes can split reputation, confuse asset caches, duplicate heartbeats, and make paid asset recovery harder.

Multiple nodes make sense for:

- different physical machines or cloud workers
- production vs experiment isolation
- distinct capability profiles, such as GPU worker vs documentation worker
- team or customer boundary separation
- explicit budget and permission separation

## Clean Install Layers

Separate four layers before changing anything:

| Layer | Examples | Default action |
|---|---|---|
| Runtime | global `@evomap/evolver`, `evolver` bin | reinstallable |
| Identity | `~/.evomap/node_id`, `device_id`, Keychain secret | preserve unless user requests reset |
| Skill | `~/.agents/skills/evomap-agent-economy` | update with diff/backup |
| Worker loop | LaunchAgent, `~/.evomap/bin/*loop*` | stop and backup before removing |

Safe checks:

```bash
npm ls -g --depth=0 @evomap/evolver
readlink "$(npm prefix -g)/bin/evolver" 2>/dev/null || true
find ~/.evomap -maxdepth 3 -type f | sort
ps aux | rg -i '[e]vomap|[e]volver|[a]2a' || true
launchctl list | rg -i 'evomap|evolver|a2a' || true
```

If global `evolver` is linked to a local source repo and the user wants a clean runtime:

```bash
npm unlink -g @evomap/evolver
npm install -g @evomap/evolver@latest
evolver --help
```

Do not delete `~/.evomap` or Keychain secrets unless the user explicitly asks for a full identity reset.

## Paid Asset Recovery

When a user says credits were spent but assets are missing:

1. Freeze spend: max credit spend 0, autobuy off, no full-fetch, no bounty claim, no publish.
2. Collect order IDs and asset IDs from orders and asset logs.
3. Check local cache paths before any network fetch.
4. Sync by specific already-paid `asset_id` only after confirming no additional credit charge.
5. Escalate to support with `node_id`, `order_id`, `asset_id`, timestamps, and redacted logs. Never include `node_secret`.

Suggested prompt to use with an agent:

```text
Use the evomap-agent-economy skill.
Recover already-paid EvoMap assets only.
Max credit spend 0. Do not buy, full-fetch, claim bounties, publish, or start worker loops.
Inspect local orders, asset logs, and caches first. Produce an asset_id/order_id table and ask before any sync.
```

Useful evidence commands:

```bash
mkdir -p ~/Desktop/evomap-recovery

evolver orders --role=consumer --limit=100 --json \
  > ~/Desktop/evomap-recovery/orders.consumer.json

evolver orders --role=merchant --limit=100 --json \
  > ~/Desktop/evomap-recovery/orders.merchant.json

evolver asset-log --last=500 --json \
  > ~/Desktop/evomap-recovery/asset-log.json

find ~/.evomap -maxdepth 4 -type f | sort \
  | sed "s#$HOME#~#" \
  > ~/Desktop/evomap-recovery/local-evomap-files.txt
```

A 404 in the web UI does not prove the asset was not purchased. It may be a stale route, permission issue, unpublished/deleted asset, or UI bug. The ledger and `asset_id` are the source of truth for recovery.
