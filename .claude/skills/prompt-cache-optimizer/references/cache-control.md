# cache_control — concrete syntax and worked examples

Load this when you're actually writing code to enable prompt caching. The mechanics and ordering rules are in `SKILL.md`; this file is the implementation detail.

> Always confirm current minimums, TTLs, and pricing against the official docs — <https://docs.claude.com/en/docs/build-with-claude/prompt-caching> — before quoting exact numbers to a user. The *structure* below is stable; the *numbers* can change with new models.

---

## Where `cache_control` can go

You attach `cache_control: { type: "ephemeral" }` to a cacheable block. It marks the **end** of a cacheable prefix — everything from the start of the request up to and including that block becomes the cached prefix. Valid attachment points:

- A block in the `system` array (system prompt as structured blocks).
- A tool definition in the `tools` array (caches tools up to that point).
- A content block inside a `messages[]` entry (caches the conversation prefix up to there).

You can set up to **4 breakpoints**. Use more than one when different layers change at different rates.

---

## Python (anthropic SDK)

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-5",  # confirm the current model id
    max_tokens=1024,
    # 1) TOOLS — first in cache order. Breakpoint after the last tool caches them all.
    tools=[
        {
            "name": "get_weather",
            "description": "Get current weather for a city.",
            "input_schema": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
            # breakpoint on the LAST tool -> caches the whole tools block as prefix
            "cache_control": {"type": "ephemeral"},
        },
    ],
    # 2) SYSTEM — stable instructions + large stable docs, breakpoint on the last stable block.
    system=[
        {"type": "text", "text": "You are a careful assistant. <invariant instructions>"},
        {
            "type": "text",
            "text": "<a large, stable document or style guide reused every call>",
            "cache_control": {"type": "ephemeral"},  # caches tools + system prefix
        },
    ],
    # 3) MESSAGES — volatile tail goes LAST, with NO breakpoint after the new user turn.
    messages=[
        {"role": "user", "content": "What's the weather in Lisbon?"},
    ],
)

u = response.usage
print(u.cache_creation_input_tokens, u.cache_read_input_tokens, u.input_tokens)
```

## TypeScript (@anthropic-ai/sdk)

```ts
import Anthropic from "@anthropic-ai/sdk";
const client = new Anthropic();

const response = await client.messages.create({
  model: "claude-sonnet-4-5", // confirm current model id
  max_tokens: 1024,
  tools: [
    {
      name: "get_weather",
      description: "Get current weather for a city.",
      input_schema: {
        type: "object",
        properties: { city: { type: "string" } },
        required: ["city"],
      },
      cache_control: { type: "ephemeral" }, // last tool -> caches tools prefix
    },
  ],
  system: [
    { type: "text", text: "You are a careful assistant. <invariant instructions>" },
    {
      type: "text",
      text: "<large stable document reused every call>",
      cache_control: { type: "ephemeral" }, // caches tools + system prefix
    },
  ],
  messages: [{ role: "user", content: "What's the weather in Lisbon?" }],
});

const { cache_creation_input_tokens, cache_read_input_tokens, input_tokens } =
  response.usage;
```

## Raw HTTP

```jsonc
{
  "model": "claude-sonnet-4-5",
  "max_tokens": 1024,
  "tools": [
    { "name": "get_weather", "description": "...", "input_schema": { /* ... */ },
      "cache_control": { "type": "ephemeral" } }
  ],
  "system": [
    { "type": "text", "text": "<invariant instructions>" },
    { "type": "text", "text": "<large stable doc>", "cache_control": { "type": "ephemeral" } }
  ],
  "messages": [
    { "role": "user", "content": "What's the weather in Lisbon?" }
  ]
}
```

---

## Multi-breakpoint pattern (layers that change at different rates)

Use separate breakpoints so a change in a fast-moving layer only invalidates the tail, not the whole prefix. Order is still tools → system → messages.

```
[ tools ............................ ] ← breakpoint 1 (rarely changes)
[ system: invariant instructions ... ]
[ system: large stable doc ......... ] ← breakpoint 2 (changes per task)
[ messages: older conversation ..... ] ← breakpoint 3 (grows; advance each turn)
[ messages: newest user turn ....... ]   no breakpoint — volatile tail
```

- Tool change → only breakpoint-1 region rewrites; rare.
- New document for a new task → breakpoints 2 and 3 regions rewrite; 1 still hits.
- Normal next turn → 1 and 2 hit from cache; only the appended turn is new.

For a growing chat, on each call put the final breakpoint at the **end of the last stable turn** (i.e. just before the new user message). The accumulated history then keeps reading from cache.

---

## Extended (longer) TTL

The default cache lifetime is short (~5 min, refreshed on hit). For workloads that re-hit on a slower cadence, request the longer (~1 hr) retention where supported:

```python
"cache_control": {"type": "ephemeral", "ttl": "1h"}
```

Confirm support and pricing for the longer TTL in the current docs before relying on it — it carries a different write premium.

---

## Reading the usage signal

Every response includes (under `usage`):

| field | meaning | what you want |
|---|---|---|
| `cache_creation_input_tokens` | tokens written to cache this call | high on the **first** call only |
| `cache_read_input_tokens` | tokens served from cache | **high and rising** on calls 2..N |
| `input_tokens` | uncached input remainder | low (just the volatile tail) on repeats |

Decision rule: if `cache_read_input_tokens` stays `0` across repeated calls that *should* share a prefix, the prefix is not byte-stable. The cause is almost always one of the cache-busters in `SKILL.md` step 4 — a timestamp/id in the prefix, reordered tools, formatting drift, or a per-call value spliced above the breakpoint.
