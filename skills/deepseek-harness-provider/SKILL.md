---
name: "deepseek-harness-provider"
description: "Configure a custom model provider (base URL, API key, models) for DeepSeek Harness dsh: settings.yaml route, credentials.yaml refs, hot reload, probe."
---

# Configure a custom model provider in DeepSeek Harness (dsh)

Use when the user asks to add or configure a model provider (PackyAPI, a gateway, a self-hosted server) for DeepSeek Harness (`dsh`, the `@deepseek-ai/dsh` agent harness, web UI on port 3080).

## 1. Locate the harness and its config home

- Config home is `$DSH_HOME` or `~/.dsh` by default. Two files matter:
  - `settings.yaml` — provider routes and model lists
  - `.credentials.yaml` — API keys, write-only; never put a key value in settings.yaml
- Confirm it runs: `lsof -i :3080 -sTCP:LISTEN`; version: `npx @deepseek-ai/dsh --version`.
- Read both files before editing. `settings.yaml` may already hold unrelated sections (e.g. `ui-onboarding`) — merge, never replace.

## 2. Probe the endpoint and key before writing anything

A working route needs a reachable URL, the right auth shape, and a usable key. Test first with the key from a masked store / env (reference the env var by name; never print it):

- `anthropic-messages`: `curl -sS -m 25 -w "\nHTTP:%{http_code}\n" "https://GATEWAY/v1/models?limit=1000" -H "x-api-key: $KEY" -H "anthropic-version: 2023-06-01"`
- `openai-completions` / `openai-responses`: `GET {baseURL}/models` with `Authorization: Bearer $KEY`

A 401 here means wrong auth header, wrong path, or bad key — resolve that before writing config; a 200 gives you the real model ids to put in the route. If discovery returns an unparseable shape, enter model ids by hand (they work the same).

## 3. Write the provider route in settings.yaml

Add a block under `llm-pi-ai.providers.<id>` (lowercase id):

```yaml
llm-pi-ai:
  providers:
    my-gateway:
      apiKeyEnv: MY_GATEWAY_API_KEY   # credential reference NAME, not the value
      api: anthropic-messages          # openai-completions | openai-responses | anthropic-messages
      baseURL: https://gateway.example
      models:
        - id: model-a
        - id: model-b
          input: [text, image]         # hand-entered models default to text-only
```

- `apiKeyEnv` is resolved per request; the secret never enters settings.yaml.
- Hand-entered models are treated as text-only unless the model declares `input: [text, image]`.
- The provider id is permanent (requests, saved sessions, defaults, and credential refs use it). Rename = add the new provider, delete the old one.
- Optional per-model/route fields: `contextWindow`, `maxTokens`, `reasoningEfforts`, `compat` (e.g. `supportsDeveloperRole: false`, `maxTokensField: max_tokens`, `thinkingFormat: deepseek`). Full schema: docs/user/guide/providers.md in the deepseek-ai/deepseek-harness repo, or the `dsh-llm-pi-ai` package README.

## 4. Store the API key in the credentials file

`~/.dsh/.credentials.yaml` uses a versioned layout (confirmed in `dsh-credentials-local` source):

```yaml
version: 1
refs:
  MY_GATEWAY_API_KEY: sk-...
records:   # preserve existing records (e.g. client-connection/browser-session)
  ...
```

- `refs` maps POSIX-identifier names to non-empty string values; `records` maps `<scope>/<id>` to tagged record mappings.
- Resolution order for a reference: the launching environment (wins, read-only) > stored `refs` > `<cwd>/.env` > `$DSH_HOME/.env`.
- Write the file with the value pulled from the injected env var in a script (never echo it), and confirm the file stays 0600.

## 5. Verify, no restart needed

- Both files hot-reload: settings are re-read per request; `.credentials.yaml` is file-watched (100 ms debounce). No server restart.
- Check error codes on the next request: `MISSING_CREDENTIAL` = the `apiKeyEnv` ref resolves to nothing; `UNKNOWN_MODEL` = model id not on the route; `INVALID_CREDENTIAL` = key unusable.
- Confirm the provider shows up under Settings → Models in the Web UI, or run one session request with the new model.
