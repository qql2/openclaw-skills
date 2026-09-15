---
name: "dsh-profile-plugins"
description: "dsh \"duplicate prefix route\"/plugin tree boot failure — find the double-mounted bundle, disable the duplicate row in cordis.patch.yml, verify boot."
---

# Fix a dsh profile whose plugin tree fails to boot

Use when `dsh web` (the `@deepseek-ai/dsh` harness, web UI on port 3080) starts with a plugin-tree error instead of a URL, e.g. `webserver: duplicate prefix route "/sidebar/api"` — one bad row aborts the whole tree.

## 1. Read the profile's layers

Profile home is `~/.dsh/profiles/<name>/` (the web UI profile is `web`).

- `cordis.yml` — the profile root, an empty entry list. Never edit it.
- `package.json` → `dsh.profile.bundles` — the ordered bundle stack; patches apply in this order.
- `cordis.patch.yml` — the user patch layer, applied **after every bundle**. This is where you fix things.
- Each bundle package's own `cordis.patch.yml` (its `dsh.bundle.patch`) shows the loader rows it inserts (`id:` + `name:`). Read them before concluding anything.

## 2. Identify the double-mounted plugin

`duplicate prefix route` means one plugin registered the same route path twice — normally two loader rows mount the same package.

- Find the path's owner: `grep -rn 'path: "/x"' node_modules/<plugin>/lib/index.js`. Expect `ctx.webServer.register({ kind: "prefix", path: ... })`.
- Look for two rows resolving to that package: a **standalone bundle** row (e.g. `id: better-sidebar`, `name: dsh-better-sidebar`) and an **aggregate bundle** that nests it (e.g. `@linxin666/dsh-web-all` inserts `id: web-ui-better-sidebar`, `name: dsh-better-sidebar`). Aggregates ship their own copy under `node_modules/<aggregate>/node_modules/`, so the two rows can even run different versions.
- Check the standalone package's own patch file for a `!!js` `disabled` guard that backs its row off when another enabled row mounts the package. **It only sees rows earlier in the entry list.** If the aggregate sits *after* the standalone in `dsh.profile.bundles` — which happens when the aggregate was added last — the guard evaluates false and both rows stay enabled. That ordering inversion is the usual root cause; the package itself documents it as a known limitation.

## 3. Disable the duplicate row in the user patch layer

Back up `cordis.patch.yml` and `package.json` first, then append to `cordis.patch.yml`:

```yaml
- id: web-ui-better-sidebar
  disabled: true
```

- The user layer applies last, so this disable is deterministic — unlike the order-dependent `!!js` guard.
- Prefer disabling the **aggregate's** row when the standalone package is the newer version the user just installed.
- Merge with the file's existing entries (e.g. an unrelated `- id: x` / `disabled: true`); never replace the file.
- Do not reorder `dsh.profile.bundles` unless the user asks — it works, but then correctness depends on bundle order.

## 4. Verify by booting

- `npx --no-install @deepseek-ai/dsh web > /tmp/dsh-web-boot.log 2>&1 &`, then read the log after ~40s. Success is `dsh web: http://127.0.0.1:3080/?token=...` with no error lines.
- Kill the test instance and confirm the port is free: `pkill -f "dsh web"`, then `lsof -nP -iTCP:3080 -sTCP:LISTEN` (empty = free). The boot opens the user's default browser, so say so.
- A new duplicate error means another pair — repeat from step 2 for that path.

## 5. Latent duplicates

Not every double mount fails at boot. Plugins that register routes lazily (e.g. `@linxin666/dsh-remote-web-ui` registers its pairing routes only when the feature is enabled) mount twice silently. When a duplicate error appears only after the user enables a feature, suspect this and apply the same fix.
