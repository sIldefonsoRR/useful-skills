# A2B Checks Catalog

Search patterns are starting points, not verdicts. Exclude `node_modules`, `vendor`, `.venv`, `dist`, `build`, and lockfiles. Adapt patterns to the languages present.

## A0 - Agent surface inventory

Find where the code talks to a model and what the model can trigger.

- LLM SDKs: `anthropic`, `@anthropic-ai/`, `openai`, `google.generativeai`, `@google/genai`, `mistralai`, `cohere`, `ollama`, `litellm`, `bedrock`, `vertexai`
- Agent frameworks: `langchain`, `langgraph`, `llama_index`, `crewai`, `autogen`, `semantic_kernel`, `ai` (Vercel AI SDK: `generateText`, `streamText`, `tool(`), `claude_agent_sdk`, `@anthropic-ai/claude-agent-sdk`
- Tool definitions: `tools=`, `tools:`, `function_call`, `tool_choice`, `@tool`, `tool(`, `input_schema`, `parameters:` near tool names
- MCP: `@modelcontextprotocol/`, `mcp.server`, `FastMCP`, `McpServer`, `server.tool(`, `.mcp.json`, `mcp_servers`
- Dispatch: code that maps a model-returned tool name to a function (`tool_use`, `tool_calls`, `getattr(`, `handlers[name]`)

Record each component, its location, and what it can reach (DB, shell, FS, HTTP, email, payments, other services).

## A1 - Prompt injection reaching tool calls

Untrusted content enters the model context in a turn where tools are available.

- Sources: user messages, fetched web pages, uploaded files, emails, tickets, DB rows, search results, previous tool results, other agents' output.
- Fail when untrusted content is concatenated into system/developer prompts, or when tool-enabled turns read untrusted content with no isolation (separate no-tools call, quarantined summarizer, or human approval before side effects).
- Look for: f-strings / template literals building prompts from request bodies or fetched data; `system=` built from variables.

## A2 - LLM output reaching dangerous sinks

Model output (tool args or text) used without validation in:

- Shell: `subprocess`, `os.system`, `exec(`, `child_process`, `execSync`, `spawn(` with `shell: true`
- Code eval: `eval(`, `exec(`, `Function(`, `vm.run`, `pickle.loads`, `yaml.load(` (unsafe loader)
- SQL: string-built queries, `raw(`, `.execute(f"`, `` `SELECT ${ ``, `text(` with interpolation, any "run_sql" tool
- Filesystem: `open(`, `fs.writeFile`, `path.join` with model-supplied paths (traversal, overwrite)
- HTTP: `requests.get(`, `fetch(`, `axios` with model-supplied URLs (SSRF to `169.254.169.254`, localhost, internal hosts)
- Rendering: model output inserted as HTML (`innerHTML`, `dangerouslySetInnerHTML`, `|safe`, `v-html`)

Fail when there is no schema validation, allowlist, parameterization, or sandbox between model output and sink.

## A3 - Authorization on agent-callable actions

- Does each tool enforce the **end user's** permissions, or does it run with a service account / admin key / DB superuser?
- Are object IDs from the model checked for ownership (BOLA/IDOR via agent)? Model-chosen `user_id`, `account_id`, `tenant_id` is a Critical sign.
- Are endpoints that the agent calls also reachable without the agent and properly authenticated?
- Fail on confused-deputy patterns: privileged credential + model-chosen target.

## A4 - Excessive agency

- Generic tools: `run_sql`, `execute_command`, `http_request`, `read_file`/`write_file` without path roots, `send_email` to any address.
- Destructive or financial actions (delete, transfer, refund, deploy, send) without human-in-the-loop confirmation.
- Credential scopes broader than the tools need (full-access API keys, write tokens for read-only tools).

## A5 - Tool argument validation

- Tool inputs validated with a schema at execution time (zod, pydantic, JSON Schema validator), not only declared to the model.
- Enums / allowlists for operation names, table names, hosts, paths.
- Fail when declared schema exists but the handler uses raw `args` without validating.

## A6 - Secrets exposure to or through the model

- API keys, DB URLs, tokens placed into prompts or system prompts.
- Tools that can return env vars, config files, `.env`, or credentials.
- Hardcoded keys in repo (`sk-`, `sk-ant-`, `AKIA`, `ghp_`, `xox`), or exposed in client bundles (`NEXT_PUBLIC_*`, `VITE_*` holding LLM keys) letting anyone call the model/backend directly.
- Full prompts or tool args logged with secrets or PII.

## A7 - Data exfiltration channels

- Agent can fetch arbitrary URLs (data in query string), render markdown images/links from model output in a client, send email/webhooks, or write to public locations.
- Fail when an injected instruction could combine "read sensitive data" + "send to attacker-chosen destination" in one agent session.

## A8 - Resource abuse and loop control

- Max iterations / max tool calls per run, token limits, timeouts.
- Rate limiting per user on agent endpoints.
- Recursion or agent-spawns-agent without depth limit.
- Fail when an unauthenticated or low-privilege user can trigger unbounded paid model calls or backend load.

## A9 - Multi-agent and agent-to-agent trust

- Output from one agent fed to another as instructions rather than data.
- A2A / sub-agent messages accepted without authentication.
- Orchestrators granting sub-agents the parent's full tool set.

## A10 - MCP server and tool supply chain

- MCP servers exposed over HTTP/SSE without authentication or with wildcard CORS.
- Third-party MCP servers or tools loaded from unpinned versions, remote URLs, or `npx -y <pkg>` without version.
- Dynamic tool registration from untrusted config.
- Tool descriptions loaded from external sources (tool-poisoning vector).

## A11 - Output handling to users and downstream systems

- Model output trusted for security decisions (e.g., "is this user an admin?", "approve refund?") without deterministic checks.
- Model output written to DB and later executed or rendered elsewhere (stored injection).

## A12 - Audit logging and detection

- Tool calls logged with user identity, tool name, args (redacted), result status.
- Ability to trace a backend action back to the agent session and originating input.
- Fail when side-effecting tool calls leave no audit trail.
